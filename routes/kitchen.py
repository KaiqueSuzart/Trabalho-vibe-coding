from flask import Blueprint, flash, redirect, render_template, request, url_for

from helpers import refresh_order_status, role_required
from models import Order, OrderItem, db

kitchen_bp = Blueprint("kitchen", __name__)


@kitchen_bp.route("/")
@role_required("garcom", "lojista")
def dashboard():
    sector = request.args.get("setor", "todos")
    query = (
        OrderItem.query.join(Order)
        .filter(
            OrderItem.status.in_(["recebido", "preparando"]),
            OrderItem.sector != "servico",
        )
        # online só entra na fila depois de pago
        .filter(
            ~((Order.payment_mode == "online") & (Order.payment_status == "pendente"))
        )
    )
    if sector in ("bar", "cozinha"):
        query = query.filter(OrderItem.sector == sector)
    items = query.order_by(Order.created_at.asc()).all()
    return render_template("kitchen/dashboard.html", items=items, sector=sector)


@kitchen_bp.route("/item/<int:item_id>/status", methods=["POST"])
@role_required("garcom", "lojista")
def update_status(item_id):
    item = OrderItem.query.get_or_404(item_id)
    new_status = request.form.get("status")
    if new_status in ("preparando", "pronto", "recebido"):
        item.status = new_status
        db.session.commit()
        refresh_order_status(item.order)
        flash(f"{item.product_name} → {new_status}", "success")
    return redirect(url_for("kitchen.dashboard", setor=request.args.get("setor", "todos")))
