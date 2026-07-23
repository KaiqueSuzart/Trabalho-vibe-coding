from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from helpers import login_required, refresh_order_status, role_required, session_open_total
from models import Category, Order, OrderItem, Payment, Product, Reservation, StockMovement, Tent, db
from models import Session as TentSession

waiter_bp = Blueprint("waiter", __name__)


@waiter_bp.route("/")
@role_required("garcom", "lojista")
def dashboard():
    ready_items = (
        OrderItem.query.join(Order)
        .filter(OrderItem.status == "pronto", OrderItem.sector != "servico")
        .order_by(Order.created_at.asc())
        .all()
    )
    pending_orders = (
        Order.query.filter(Order.status.in_(["recebido", "preparando", "pronto"]))
        .order_by(Order.created_at.asc())
        .all()
    )
    # esconde pedidos que só têm aluguel/serviço
    pending_orders = [
        o
        for o in pending_orders
        if any(i.sector != "servico" and i.status != "cancelado" for i in o.items)
    ]
    close_requests = TentSession.query.filter_by(status="fechamento_solicitado").all()
    open_sessions = TentSession.query.filter(TentSession.status.in_(["aberta", "fechamento_solicitado"])).all()
    tents = Tent.query.order_by(Tent.number).all()
    return render_template(
        "waiter/dashboard.html",
        ready_items=ready_items,
        pending_orders=pending_orders,
        close_requests=close_requests,
        open_sessions=open_sessions,
        tents=tents,
    )


@waiter_bp.route("/entregar/<int:item_id>", methods=["POST"])
@role_required("garcom", "lojista")
def deliver_item(item_id):
    item = OrderItem.query.get_or_404(item_id)
    order = item.order
    item.status = "entregue"
    db.session.commit()
    refresh_order_status(order)

    msg = f"{item.product_name} marcado como entregue."
    if order.payment_status == "cobrar_entrega" and request.form.get("collect_payment") == "1":
        method = request.form.get("method", "dinheiro")
        if method not in ("dinheiro", "pix", "cartao"):
            method = "dinheiro"
        # cobra o pedido inteiro na primeira cobrança
        if order.payment_status != "pago":
            order.payment_status = "pago"
            order.payment_method = method
            db.session.add(
                Payment(
                    session_id=order.session_id,
                    order_id=order.id,
                    method=method,
                    amount=order.total,
                    notes=f"Cobrado na entrega — pedido #{order.id}",
                )
            )
            db.session.commit()
            msg += f" Pagamento ({method}) registrado."
    elif order.payment_status == "cobrar_entrega":
        msg += " Atenção: cobrar na tenda."
    elif order.payment_status == "pago":
        msg += " (já pago)"

    flash(msg, "success")
    return redirect(url_for("waiter.dashboard"))


@waiter_bp.route("/checkin", methods=["GET", "POST"])
@role_required("garcom", "lojista")
def checkin():
    tents = Tent.query.order_by(Tent.number).all()
    if request.method == "POST":
        tent_id = int(request.form["tent_id"])
        tent = Tent.query.get_or_404(tent_id)
        name = request.form.get("customer_name", "Cliente").strip() or "Cliente"
        phone = request.form.get("customer_phone", "").strip()
        reservation_id = request.form.get("reservation_id") or None

        existing = (
            TentSession.query.filter_by(tent_id=tent.id)
            .filter(TentSession.status.in_(["aberta", "fechamento_solicitado"]))
            .first()
        )
        if existing:
            flash("Já existe sessão aberta nesta tenda.", "warning")
            return redirect(url_for("waiter.checkin"))

        if tent.status == "manutencao":
            flash("Tenda em manutenção.", "danger")
            return redirect(url_for("waiter.checkin"))

        reservation = None
        if reservation_id:
            reservation = Reservation.query.get(int(reservation_id))
            if reservation:
                reservation.status = "checkin"
                name = reservation.customer_name
                phone = reservation.customer_phone

        tent_session = TentSession(
            tent_id=tent.id,
            reservation_id=reservation.id if reservation else None,
            customer_name=name,
            customer_phone=phone,
            status="aberta",
            rental_charged=False,
        )
        tent.status = "ocupada"
        db.session.add(tent_session)
        db.session.flush()

        # cobra aluguel da tenda como item de serviço, se existir produto
        rental = Product.query.filter_by(name="Aluguel de Tenda", kind="servico").first()
        if rental:
            order = Order(session_id=tent_session.id, notes="Aluguel da tenda", status="entregue", source="garcom")
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

        db.session.commit()
        from flask import current_app

        pin = current_app.config.get("DAY_PIN", "1234")
        flash(f"Check-in da tenda {tent.number} ok. PIN do dia para o cliente: {pin}", "success")
        return redirect(url_for("waiter.dashboard"))

    from datetime import date as date_cls

    today_reservations = (
        Reservation.query.filter(
            Reservation.date == date_cls.today(),
            Reservation.status.in_(["confirmada", "pendente"]),
        )
        .order_by(Reservation.id.asc())
        .all()
    )
    return render_template("waiter/checkin.html", tents=tents, reservations=today_reservations)


@waiter_bp.route("/pedido-manual", methods=["GET", "POST"])
@role_required("garcom", "lojista")
def manual_order():
    open_sessions = TentSession.query.filter(TentSession.status.in_(["aberta", "fechamento_solicitado"])).all()
    categories = Category.query.order_by(Category.sort_order).all()

    if request.method == "POST":
        session_id = int(request.form["session_id"])
        tent_session = TentSession.query.get_or_404(session_id)
        product_id = int(request.form["product_id"])
        qty = max(1, int(request.form.get("quantity", 1)))
        notes = request.form.get("notes", "").strip()
        product = Product.query.get_or_404(product_id)

        if product.kind == "produto":
            result = db.session.execute(
                db.update(Product)
                .where(Product.id == product.id, Product.stock_qty >= qty)
                .values(stock_qty=Product.stock_qty - qty)
            )
            if result.rowcount == 0:
                db.session.rollback()
                flash("Estoque insuficiente.", "danger")
                return redirect(url_for("waiter.manual_order"))

        order = Order(session_id=tent_session.id, notes=notes, status="recebido", source="garcom")
        db.session.add(order)
        db.session.flush()
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=qty,
                notes=notes,
                status="recebido",
                sector=product.category.sector if product.category else "cozinha",
            )
        )
        if product.kind == "produto":
            db.session.add(
                StockMovement(
                    product_id=product.id,
                    quantity=-qty,
                    reason=f"Pedido manual #{order.id}",
                    user_id=session.get("user_id"),
                )
            )
        db.session.commit()
        flash(f"Pedido lançado na tenda {tent_session.tent.number}.", "success")
        return redirect(url_for("waiter.dashboard"))

    return render_template("waiter/manual_order.html", open_sessions=open_sessions, categories=categories)


@waiter_bp.route("/conta/<int:session_id>", methods=["GET", "POST"])
@role_required("garcom", "lojista")
def close_bill(session_id):
    tent_session = TentSession.query.get_or_404(session_id)
    from helpers import session_gross_total

    def money_paid():
        return float(
            db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0.0))
            .filter(Payment.session_id == tent_session.id)
            .scalar()
        )

    if request.method == "POST":
        action = request.form.get("action", "close")
        method = request.form.get("method", "pix")
        if method not in ("pix", "dinheiro", "cartao"):
            method = "pix"

        if action == "pay_order":
            order = Order.query.get_or_404(int(request.form["order_id"]))
            if order.session_id != tent_session.id:
                flash("Pedido inválido para esta tenda.", "danger")
            elif order.payment_status == "pago":
                flash(f"Pedido #{order.id} já está pago.", "info")
            else:
                order.payment_status = "pago"
                order.payment_method = method
                db.session.add(
                    Payment(
                        session_id=tent_session.id,
                        order_id=order.id,
                        method=method,
                        amount=order.total,
                        notes=f"Baixa pedido #{order.id}",
                    )
                )
                db.session.commit()
                flash(f"Baixa de pagamento no pedido #{order.id} (R$ {order.total:.2f}).", "success")
            return redirect(url_for("waiter.close_bill", session_id=session_id))

        if action == "deliver_item":
            item = OrderItem.query.get_or_404(int(request.form["item_id"]))
            if item.order.session_id != tent_session.id:
                flash("Item inválido.", "danger")
            else:
                item.status = "entregue"
                db.session.commit()
                refresh_order_status(item.order)
                flash(f"{item.product_name} marcado como entregue.", "success")
            return redirect(url_for("waiter.close_bill", session_id=session_id))

        if action == "mark_ready_delivered":
            # marca todos os itens 'pronto' desta sessão como entregues
            items = (
                OrderItem.query.join(Order)
                .filter(Order.session_id == tent_session.id, OrderItem.status == "pronto")
                .all()
            )
            for item in items:
                item.status = "entregue"
            db.session.commit()
            for order in {i.order for i in items}:
                refresh_order_status(order)
            flash(f"{len(items)} item(ns) entregues.", "success")
            return redirect(url_for("waiter.close_bill", session_id=session_id))

        # action == close (pagar restante e/ou liberar)
        remaining = round(session_open_total(tent_session), 2)
        raw_amount = request.form.get("amount", remaining)
        try:
            amount = float(str(raw_amount).replace(",", "."))
        except ValueError:
            amount = remaining
        notes = request.form.get("notes", "").strip()

        if remaining <= 0.01:
            amount = 0.0
        else:
            db.session.add(
                Payment(
                    session_id=tent_session.id,
                    method=method,
                    amount=amount,
                    notes=notes or "Fechamento de conta",
                )
            )
            db.session.flush()

        if amount + 0.01 >= remaining:
            for order in tent_session.orders:
                if order.status == "cancelado":
                    continue
                if order.payment_status != "pago":
                    order.payment_status = "pago"
                    order.payment_method = method or order.payment_method or method
            tent_session.status = "fechada"
            tent_session.closed_at = datetime.utcnow()
            tent = tent_session.tent
            tent.status = "livre"
            if tent_session.reservation:
                tent_session.reservation.status = "concluida"
            flash("Conta fechada e tenda liberada.", "success")
        else:
            flash("Pagamento parcial registrado. Ainda há valor em aberto.", "info")
        db.session.commit()
        return redirect(url_for("waiter.close_bill", session_id=session_id))

    total_open = session_open_total(tent_session)
    total_gross = session_gross_total(tent_session)
    paid = money_paid()
    remaining = round(total_open, 2)
    orders = sorted(tent_session.orders, key=lambda o: o.created_at or datetime.utcnow())
    payments = (
        Payment.query.filter_by(session_id=tent_session.id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    return render_template(
        "waiter/close_bill.html",
        tent_session=tent_session,
        orders=orders,
        payments=payments,
        total=total_open,
        total_gross=total_gross,
        paid=paid,
        remaining=remaining,
    )


@waiter_bp.route("/mapa")
@role_required("garcom", "lojista")
def tent_map():
    tents = Tent.query.order_by(Tent.number).all()
    return render_template("waiter/map.html", tents=tents)
