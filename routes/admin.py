from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func

from helpers import role_required, session_open_total
from models import (
    Category,
    Order,
    OrderItem,
    Payment,
    Product,
    Reservation,
    StockMovement,
    Tent,
    User,
    db,
)
from models import Session as TentSession

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@role_required("lojista")
def dashboard():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    payments_today = Payment.query.filter(Payment.created_at >= today_start).all()
    revenue = sum(p.amount for p in payments_today)
    closed_sessions = TentSession.query.filter(
        TentSession.closed_at >= today_start, TentSession.status == "fechada"
    ).count()
    open_sessions = TentSession.query.filter(
        TentSession.status.in_(["aberta", "fechamento_solicitado"])
    ).count()
    occupied = Tent.query.filter_by(status="ocupada").count()
    total_tents = Tent.query.count()
    low_stock = Product.query.filter(
        Product.kind == "produto", Product.stock_qty <= Product.stock_min
    ).all()

    by_method = {}
    for p in payments_today:
        by_method[p.method] = by_method.get(p.method, 0) + p.amount

    top_products = (
        db.session.query(OrderItem.product_name, func.sum(OrderItem.quantity).label("qty"))
        .join(Order)
        .filter(Order.created_at >= today_start, OrderItem.status != "cancelado")
        .group_by(OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    ticket_avg = revenue / closed_sessions if closed_sessions else 0

    return render_template(
        "admin/dashboard.html",
        revenue=revenue,
        closed_sessions=closed_sessions,
        open_sessions=open_sessions,
        occupied=occupied,
        total_tents=total_tents,
        low_stock=low_stock,
        by_method=by_method,
        top_products=top_products,
        ticket_avg=ticket_avg,
        today=today,
    )


@admin_bp.route("/produtos", methods=["GET", "POST"])
@role_required("lojista")
def products():
    categories = Category.query.order_by(Category.sort_order).all()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            product = Product(
                category_id=int(request.form["category_id"]),
                name=request.form["name"].strip(),
                description=request.form.get("description", "").strip(),
                price=float(request.form["price"]),
                stock_qty=int(request.form.get("stock_qty", 0)),
                stock_min=int(request.form.get("stock_min", 5)),
                kind=request.form.get("kind", "produto"),
                image_url=request.form.get("image_url", "").strip(),
                available=True,
            )
            db.session.add(product)
            db.session.commit()
            flash("Produto criado.", "success")
        elif action == "toggle":
            product = Product.query.get_or_404(int(request.form["product_id"]))
            product.available = not product.available
            db.session.commit()
            flash("Disponibilidade atualizada.", "info")
        elif action == "update":
            product = Product.query.get_or_404(int(request.form["product_id"]))
            product.name = request.form["name"].strip()
            product.price = float(request.form["price"])
            product.description = request.form.get("description", "").strip()
            product.stock_min = int(request.form.get("stock_min", product.stock_min))
            if "image_url" in request.form:
                product.image_url = request.form.get("image_url", "").strip()
            db.session.commit()
            flash("Produto atualizado.", "success")
        return redirect(url_for("admin.products"))

    products_list = Product.query.order_by(Product.name).all()
    return render_template("admin/products.html", products=products_list, categories=categories)


@admin_bp.route("/categorias", methods=["GET", "POST"])
@role_required("lojista")
def categories():
    if request.method == "POST":
        db.session.add(
            Category(
                name=request.form["name"].strip(),
                sector=request.form.get("sector", "cozinha"),
                sort_order=int(request.form.get("sort_order", 0)),
            )
        )
        db.session.commit()
        flash("Categoria criada.", "success")
        return redirect(url_for("admin.categories"))
    cats = Category.query.order_by(Category.sort_order).all()
    return render_template("admin/categories.html", categories=cats)


@admin_bp.route("/tendas", methods=["GET", "POST"])
@role_required("lojista")
def tents():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            number = int(request.form["number"])
            if Tent.query.filter_by(number=number).first():
                flash("Número de tenda já existe.", "danger")
            else:
                db.session.add(
                    Tent(
                        number=number,
                        zone=request.form.get("zone", "Areia"),
                        capacity=int(request.form.get("capacity", 4)),
                        daily_price=float(request.form.get("daily_price", 80)),
                        status=request.form.get("status", "livre"),
                    )
                )
                db.session.commit()
                flash("Tenda criada.", "success")
        elif action == "update":
            tent = Tent.query.get_or_404(int(request.form["tent_id"]))
            tent.zone = request.form.get("zone", tent.zone)
            tent.capacity = int(request.form.get("capacity", tent.capacity))
            tent.daily_price = float(request.form.get("daily_price", tent.daily_price))
            new_status = request.form.get("status", tent.status)
            # não forçar livre se houver sessão aberta
            open_s = (
                TentSession.query.filter_by(tent_id=tent.id)
                .filter(TentSession.status.in_(["aberta", "fechamento_solicitado"]))
                .first()
            )
            if open_s and new_status == "livre":
                flash("Há sessão aberta; feche a conta antes de liberar.", "warning")
            else:
                tent.status = new_status
                db.session.commit()
                flash("Tenda atualizada.", "success")
        return redirect(url_for("admin.tents"))

    tents_list = Tent.query.order_by(Tent.number).all()
    return render_template("admin/tents.html", tents=tents_list)


@admin_bp.route("/estoque", methods=["GET", "POST"])
@role_required("lojista")
def stock():
    if request.method == "POST":
        product = Product.query.get_or_404(int(request.form["product_id"]))
        qty = int(request.form["quantity"])
        reason = request.form.get("reason", "Ajuste manual").strip()
        product.stock_qty += qty
        db.session.add(
            StockMovement(
                product_id=product.id,
                quantity=qty,
                reason=reason,
                user_id=session.get("user_id"),
            )
        )
        db.session.commit()
        flash("Estoque atualizado.", "success")
        return redirect(url_for("admin.stock"))

    products_list = Product.query.filter_by(kind="produto").order_by(Product.name).all()
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(30).all()
    return render_template("admin/stock.html", products=products_list, movements=movements)


@admin_bp.route("/usuarios", methods=["GET", "POST"])
@role_required("lojista")
def users():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            username = request.form["username"].strip()
            if User.query.filter_by(username=username).first():
                flash("Usuário já existe.", "danger")
            else:
                user = User(
                    name=request.form["name"].strip(),
                    username=username,
                    role=request.form.get("role", "garcom"),
                )
                user.set_password(request.form["password"])
                db.session.add(user)
                db.session.commit()
                flash("Usuário criado.", "success")
        elif action == "toggle":
            user = User.query.get_or_404(int(request.form["user_id"]))
            if user.id == session.get("user_id"):
                flash("Você não pode desativar a si mesmo.", "warning")
            else:
                user.active = not user.active
                db.session.commit()
                flash("Status do usuário atualizado.", "info")
        return redirect(url_for("admin.users"))

    users_list = User.query.order_by(User.name).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/reservas")
@role_required("lojista")
def reservations():
    reservations_list = Reservation.query.order_by(Reservation.date.desc(), Reservation.id.desc()).limit(50).all()
    return render_template("admin/reservations.html", reservations=reservations_list)


@admin_bp.route("/reservas/<int:res_id>/cancelar", methods=["POST"])
@role_required("lojista")
def cancel_reservation(res_id):
    reservation = Reservation.query.get_or_404(res_id)
    reservation.status = "cancelada"
    tent = reservation.tent
    if tent.status == "reservada":
        open_s = (
            TentSession.query.filter_by(tent_id=tent.id)
            .filter(TentSession.status.in_(["aberta", "fechamento_solicitado"]))
            .first()
        )
        if not open_s:
            tent.status = "livre"
    db.session.commit()
    flash("Reserva cancelada.", "info")
    return redirect(url_for("admin.reservations"))


@admin_bp.route("/relatorios")
@role_required("lojista")
def reports():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    payments = Payment.query.filter(Payment.created_at >= today_start).order_by(Payment.created_at.desc()).all()
    sessions_today = TentSession.query.filter(TentSession.opened_at >= today_start).all()
    orders_today = Order.query.filter(Order.created_at >= today_start).all()

    occupancy = {
        "livre": Tent.query.filter_by(status="livre").count(),
        "reservada": Tent.query.filter_by(status="reservada").count(),
        "ocupada": Tent.query.filter_by(status="ocupada").count(),
        "manutencao": Tent.query.filter_by(status="manutencao").count(),
    }

    return render_template(
        "admin/reports.html",
        payments=payments,
        sessions_today=sessions_today,
        orders_today=orders_today,
        occupancy=occupancy,
        today=today,
        session_open_total=session_open_total,
    )


@admin_bp.route("/mapa")
@role_required("lojista")
def tent_map():
    tents = Tent.query.order_by(Tent.number).all()
    return render_template("admin/map.html", tents=tents)
