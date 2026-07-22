from datetime import date, datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from models import Category, Product, Reservation, Tent, db
from models import Session as TentSession
from models import Order, OrderItem, Payment, StockMovement

public_bp = Blueprint("public", __name__)


def _charge_tent_rental(tent, tent_session):
    if tent_session.rental_charged:
        return
    rental = Product.query.filter_by(name="Aluguel de Tenda", kind="servico").first()
    if not rental:
        return
    order = Order(
        session_id=tent_session.id,
        notes="Aluguel da tenda",
        status="entregue",
        source="cliente",
        payment_mode="na_conta",
        payment_status="pendente",
    )
    db.session.add(order)
    db.session.flush()
    db.session.add(
        OrderItem(
            order_id=order.id,
            product_id=rental.id,
            product_name=rental.name,
            unit_price=tent.daily_price,
            quantity=1,
            status="entregue",
            sector="servico",
        )
    )
    tent_session.rental_charged = True


def ensure_client_session(tent):
    """
    Retorna sessão aberta da tenda.
    Se ainda não houver check-in, abre automaticamente quando:
    - há reserva confirmada para hoje, ou
    - a tenda está livre/reservada (self check-in com PIN do dia).
    """
    open_session = (
        TentSession.query.filter_by(tent_id=tent.id)
        .filter(TentSession.status.in_(["aberta", "fechamento_solicitado"]))
        .order_by(TentSession.opened_at.desc())
        .first()
    )
    if open_session:
        return open_session, None

    if tent.status == "manutencao":
        return None, "Tenda em manutenção. Escolha outra."

    today_res = (
        Reservation.query.filter_by(tent_id=tent.id, date=date.today())
        .filter(Reservation.status.in_(["confirmada", "pendente"]))
        .order_by(Reservation.id.desc())
        .first()
    )

    # Já ocupada no mapa sem sessão = inconsistência; não deixa outro entrar
    if tent.status == "ocupada" and not open_session:
        return None, "Esta tenda consta como ocupada. Peça ajuda ao garçom."

    if not today_res and tent.status not in ("livre", "reservada"):
        return None, "Não foi possível abrir esta tenda. Fale com o garçom."

    name = today_res.customer_name if today_res else "Cliente"
    phone = today_res.customer_phone if today_res else ""

    tent_session = TentSession(
        tent_id=tent.id,
        reservation_id=today_res.id if today_res else None,
        customer_name=name,
        customer_phone=phone,
        status="aberta",
        rental_charged=False,
    )
    if today_res:
        today_res.status = "checkin"
    tent.status = "ocupada"
    db.session.add(tent_session)
    db.session.flush()
    _charge_tent_rental(tent, tent_session)
    db.session.commit()
    return tent_session, None


@public_bp.route("/")
def home():
    tents = Tent.query.order_by(Tent.number).all()
    categories = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template(
        "client/home.html",
        tents=tents,
        categories=categories,
        today=date.today(),
    )


@public_bp.route("/pedir", methods=["GET", "POST"])
def order_start():
    """Entrada principal: informar nº da tenda + PIN e ir ao cardápio."""
    occupied = (
        Tent.query.filter_by(status="ocupada").order_by(Tent.number).all()
    )
    if request.method == "POST":
        try:
            number = int(request.form.get("tent_number", "").strip())
        except ValueError:
            flash("Informe o número da tenda.", "danger")
            return redirect(url_for("public.order_start"))

        pin = request.form.get("pin", "").strip()
        tent = Tent.query.filter_by(number=number).first()
        if not tent:
            flash("Tenda não encontrada.", "danger")
            return redirect(url_for("public.order_start"))

        if pin != current_app.config["DAY_PIN"]:
            flash("PIN do dia inválido. Peça o código na barraca.", "danger")
            return redirect(url_for("public.order_start"))

        open_session, err = ensure_client_session(tent)
        if err:
            flash(err, "warning")
            return redirect(url_for("public.order_start"))

        session["client_tent"] = tent.number
        session["client_session_id"] = open_session.id
        session["cart"] = session.get("cart", {})
        flash(f"Tenda {tent.number} liberada. Pode pedir!", "success")
        return redirect(url_for("public.menu", number=number))

    return render_template("client/order_start.html", occupied=occupied)


@public_bp.route("/cardapio")
def menu_browse():
    """Cardápio público (só visualização) + atalho para pedir."""
    categories = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template("client/menu_browse.html", categories=categories)


@public_bp.route("/reservar", methods=["GET", "POST"])
def reserve():
    tents = Tent.query.filter(Tent.status != "manutencao").order_by(Tent.number).all()
    if request.method == "POST":
        tent_id = int(request.form["tent_id"])
        tent = Tent.query.get_or_404(tent_id)
        res_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        name = request.form["customer_name"].strip()
        phone = request.form.get("customer_phone", "").strip()
        time_slot = request.form.get("time_slot", "dia todo")

        if not name:
            flash("Informe o nome para a reserva.", "danger")
            return redirect(url_for("public.reserve"))

        conflict = (
            Reservation.query.filter_by(tent_id=tent.id, date=res_date)
            .filter(Reservation.status.in_(["pendente", "confirmada", "checkin"]))
            .first()
        )
        if conflict:
            flash("Esta tenda já está reservada nesta data.", "danger")
            return redirect(url_for("public.reserve"))

        if res_date == date.today() and tent.status == "ocupada":
            flash("Esta tenda está ocupada agora. Escolha outra ou outra data.", "danger")
            return redirect(url_for("public.reserve"))

        reservation = Reservation(
            tent_id=tent.id,
            customer_name=name,
            customer_phone=phone,
            date=res_date,
            time_slot=time_slot,
            value=tent.daily_price,
            status="confirmada",
        )
        db.session.add(reservation)
        # No mapa, "reservada" só faz sentido para o dia de hoje
        if res_date == date.today() and tent.status == "livre":
            tent.status = "reservada"
        db.session.commit()

        if res_date == date.today():
            flash(f"Reserva confirmada! Tenda {tent.number} marcada como reservada no mapa.", "success")
        else:
            flash(
                f"Reserva confirmada para a tenda {tent.number} em {res_date.strftime('%d/%m/%Y')}. "
                f"No mapa ela só aparece 'reservada' no dia da reserva.",
                "success",
            )
        return redirect(url_for("public.home"))

    return render_template("client/reserve.html", tents=tents, today=date.today().isoformat())


@public_bp.route("/t/<int:number>", methods=["GET", "POST"])
def tent_entry(number):
    tent = Tent.query.filter_by(number=number).first_or_404()
    open_session = (
        TentSession.query.filter_by(tent_id=tent.id)
        .filter(TentSession.status.in_(["aberta", "fechamento_solicitado"]))
        .order_by(TentSession.opened_at.desc())
        .first()
    )

    if request.method == "POST":
        pin = request.form.get("pin", "").strip()
        if pin != current_app.config["DAY_PIN"]:
            flash("PIN do dia inválido. Peça o código na barraca.", "danger")
            return redirect(url_for("public.tent_entry", number=number))

        open_session, err = ensure_client_session(tent)
        if err:
            flash(err, "warning")
            return redirect(url_for("public.tent_entry", number=number))

        session["client_tent"] = tent.number
        session["client_session_id"] = open_session.id
        return redirect(url_for("public.menu", number=number))

    return render_template("client/tent_entry.html", tent=tent, open_session=open_session)


@public_bp.route("/t/<int:number>/cardapio")
def menu(number):
    tent = Tent.query.filter_by(number=number).first_or_404()
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    open_session = TentSession.query.get(session["client_session_id"])
    if not open_session or not open_session.is_open:
        session.pop("client_tent", None)
        session.pop("client_session_id", None)
        flash("Sessão encerrada. Faça check-in novamente.", "warning")
        return redirect(url_for("public.tent_entry", number=number))

    categories = Category.query.order_by(Category.sort_order, Category.name).all()
    cart = session.get("cart", {})
    cart_count = sum(int(v.get("quantity", 0)) for v in cart.values())
    return render_template(
        "client/menu.html",
        tent=tent,
        categories=categories,
        cart=cart,
        cart_count=cart_count,
        open_session=open_session,
    )


@public_bp.route("/t/<int:number>/carrinho/add", methods=["POST"])
def cart_add(number):
    if session.get("client_tent") != number:
        return redirect(url_for("public.tent_entry", number=number))

    product_id = str(request.form["product_id"])
    qty = max(1, int(request.form.get("quantity", 1)))
    notes = request.form.get("notes", "").strip()
    cart = session.get("cart", {})
    item = cart.get(product_id, {"quantity": 0, "notes": ""})
    item["quantity"] += qty
    if notes:
        item["notes"] = notes
    cart[product_id] = item
    session["cart"] = cart
    flash("Item adicionado ao carrinho.", "success")
    return redirect(url_for("public.menu", number=number))


@public_bp.route("/t/<int:number>/carrinho")
def cart_view(number):
    if session.get("client_tent") != number:
        return redirect(url_for("public.tent_entry", number=number))

    tent = Tent.query.filter_by(number=number).first_or_404()
    cart = session.get("cart", {})
    lines = []
    total = 0.0
    for pid, data in cart.items():
        product = Product.query.get(int(pid))
        if not product or not product.available:
            continue
        subtotal = product.price * data["quantity"]
        total += subtotal
        lines.append({"product": product, "quantity": data["quantity"], "notes": data.get("notes", ""), "subtotal": subtotal})

    return render_template("client/cart.html", tent=tent, lines=lines, total=total)


@public_bp.route("/t/<int:number>/carrinho/update", methods=["POST"])
def cart_update(number):
    if session.get("client_tent") != number:
        return redirect(url_for("public.tent_entry", number=number))
    product_id = str(request.form["product_id"])
    qty = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    if product_id in cart:
        if qty <= 0:
            cart.pop(product_id, None)
            flash("Item removido do carrinho.", "info")
        else:
            cart[product_id]["quantity"] = min(20, qty)
            flash("Quantidade atualizada.", "success")
        session["cart"] = cart
    return redirect(url_for("public.cart_view", number=number))


@public_bp.route("/t/<int:number>/carrinho/remove", methods=["POST"])
def cart_remove(number):
    if session.get("client_tent") != number:
        return redirect(url_for("public.tent_entry", number=number))
    product_id = str(request.form["product_id"])
    cart = session.get("cart", {})
    if product_id in cart:
        cart.pop(product_id)
        session["cart"] = cart
        flash("Item removido.", "info")
    return redirect(url_for("public.cart_view", number=number))


@public_bp.route("/t/<int:number>/carrinho/clear", methods=["POST"])
def cart_clear(number):
    session["cart"] = {}
    flash("Carrinho limpo.", "info")
    return redirect(url_for("public.menu", number=number))


@public_bp.route("/t/<int:number>/pedir", methods=["POST"])
def place_order(number):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    tent_session = TentSession.query.get(session["client_session_id"])
    if not tent_session or not tent_session.is_open:
        flash("Sessão inválida.", "danger")
        return redirect(url_for("public.tent_entry", number=number))

    cart = session.get("cart", {})
    if not cart:
        flash("Carrinho vazio.", "warning")
        return redirect(url_for("public.menu", number=number))

    payment_mode = request.form.get("payment_mode", "na_conta")
    if payment_mode not in ("online", "na_entrega", "na_conta"):
        payment_mode = "na_conta"

    from helpers import recent_duplicate_order

    dup = recent_duplicate_order(tent_session)
    if dup:
        flash(
            f"Pedido duplicado bloqueado: a tenda {number} já pediu há menos de 2 minutos "
            f"(pedido #{dup.id}). Aguarde um pouco ou acompanhe o pedido atual.",
            "warning",
        )
        return redirect(url_for("public.orders", number=number))

    online_method = request.form.get("online_method", "pix")
    order_notes = request.form.get("order_notes", "").strip()

    if payment_mode == "online":
        payment_status = "pendente"
    elif payment_mode == "na_entrega":
        payment_status = "cobrar_entrega"
    else:
        payment_status = "pendente"

    order = Order(
        session_id=tent_session.id,
        notes=order_notes,
        status="recebido",
        source="cliente",
        payment_mode=payment_mode,
        payment_status=payment_status,
        payment_method=online_method if payment_mode == "online" else "",
    )
    db.session.add(order)
    db.session.flush()

    for pid, data in cart.items():
        product = Product.query.get(int(pid))
        if not product or not product.available:
            continue
        if product.kind == "produto" and product.stock_qty < data["quantity"]:
            db.session.rollback()
            flash(f"Estoque insuficiente para {product.name}.", "danger")
            return redirect(url_for("public.cart_view", number=number))

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=data["quantity"],
            notes=data.get("notes", ""),
            status="recebido",
            sector=product.category.sector if product.category else "cozinha",
        )
        db.session.add(item)

        if product.kind == "produto":
            product.stock_qty -= data["quantity"]
            db.session.add(
                StockMovement(
                    product_id=product.id,
                    quantity=-data["quantity"],
                    reason=f"Pedido #{order.id}",
                )
            )

    db.session.commit()
    session["cart"] = {}

    if payment_mode == "online":
        return redirect(url_for("public.pay_order", number=number, order_id=order.id))

    if payment_mode == "na_entrega":
        flash(f"Pedido #{order.id} enviado! Pague quando o garçom trouxer.", "success")
    else:
        flash(f"Pedido #{order.id} enviado! Vai na conta da tenda.", "success")
    return redirect(url_for("public.orders", number=number))


@public_bp.route("/t/<int:number>/pagar/<int:order_id>", methods=["GET", "POST"])
def pay_order(number, order_id):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    order = Order.query.get_or_404(order_id)
    if order.session_id != session.get("client_session_id"):
        flash("Pedido inválido.", "danger")
        return redirect(url_for("public.orders", number=number))

    tent = Tent.query.filter_by(number=number).first_or_404()

    if request.method == "POST":
        method = request.form.get("method", order.payment_method or "pix")
        if method not in ("pix", "cartao"):
            method = "pix"
        if order.payment_status != "pago":
            order.payment_status = "pago"
            order.payment_method = method
            db.session.add(
                Payment(
                    session_id=order.session_id,
                    order_id=order.id,
                    method=method,
                    amount=order.total,
                    notes=f"Pagamento online pedido #{order.id}",
                )
            )
            db.session.commit()
        flash("Pagamento confirmado! Pedido seguindo para a cozinha/bar.", "success")
        return redirect(url_for("public.orders", number=number))

    return render_template(
        "client/pay.html",
        tent=tent,
        order=order,
        method=order.payment_method or "pix",
    )


@public_bp.route("/t/<int:number>/pedidos")
def orders(number):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    from helpers import CANCEL_WINDOW_MINUTES, can_cancel_order, estimate_wait_minutes

    tent = Tent.query.filter_by(number=number).first_or_404()
    tent_session = TentSession.query.get(session["client_session_id"])
    orders_list = (
        Order.query.filter_by(session_id=tent_session.id)
        .order_by(Order.created_at.desc())
        .all()
        if tent_session
        else []
    )
    # Não listar só aluguel como "pedido de cardápio" confunde — mantém todos
    estimates = {o.id: estimate_wait_minutes(o) for o in orders_list if estimate_wait_minutes(o)}
    can_cancel = {o.id: can_cancel_order(o) for o in orders_list}
    order_ids = [o.id for o in orders_list if o.status != "cancelado"]
    return render_template(
        "client/orders.html",
        tent=tent,
        orders=orders_list,
        open_session=tent_session,
        estimates=estimates,
        can_cancel=can_cancel,
        cancel_minutes=CANCEL_WINDOW_MINUTES,
        order_ids=order_ids,
    )


@public_bp.route("/t/<int:number>/pedidos/<int:order_id>/cancelar", methods=["POST"])
def cancel_order(number, order_id):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    from helpers import can_cancel_order

    order = Order.query.get_or_404(order_id)
    if order.session_id != session.get("client_session_id"):
        flash("Pedido inválido.", "danger")
        return redirect(url_for("public.orders", number=number))

    if not can_cancel_order(order):
        flash("Este pedido não pode mais ser cancelado (prazo esgotado ou já em preparo).", "warning")
        return redirect(url_for("public.orders", number=number))

    order.status = "cancelado"
    for item in order.items:
        item.status = "cancelado"
        product = Product.query.get(item.product_id)
        if product and product.kind == "produto":
            product.stock_qty += item.quantity
            db.session.add(
                StockMovement(
                    product_id=product.id,
                    quantity=item.quantity,
                    reason=f"Cancelamento pedido #{order.id}",
                )
            )
    db.session.commit()
    flash(f"Pedido #{order.id} cancelado.", "info")
    return redirect(url_for("public.orders", number=number))


@public_bp.route("/acompanhar")
def track_order():
    return render_template("client/track.html", initial_numero=request.args.get("n", ""))


@public_bp.route("/teste-api")
def api_test():
    return render_template("client/api_test.html")


@public_bp.route("/t/<int:number>/conta")
def bill(number):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    from helpers import session_gross_total, session_open_total

    tent = Tent.query.filter_by(number=number).first_or_404()
    tent_session = TentSession.query.get(session["client_session_id"])
    total_open = session_open_total(tent_session) if tent_session else 0
    total_gross = session_gross_total(tent_session) if tent_session else 0
    paid = sum(p.amount for p in tent_session.payments) if tent_session else 0
    return render_template(
        "client/bill.html",
        tent=tent,
        open_session=tent_session,
        total=total_open,
        total_gross=total_gross,
        paid=paid,
    )


@public_bp.route("/t/<int:number>/fechar", methods=["POST"])
def request_close(number):
    if session.get("client_tent") != number or not session.get("client_session_id"):
        return redirect(url_for("public.tent_entry", number=number))

    tent_session = TentSession.query.get(session["client_session_id"])
    if tent_session and tent_session.status == "aberta":
        tent_session.status = "fechamento_solicitado"
        db.session.commit()
        flash("Fechamento solicitado. Um garçom virá até a tenda.", "success")
    return redirect(url_for("public.bill", number=number))
