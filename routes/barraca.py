from flask import Blueprint, flash, redirect, render_template, request, url_for

from helpers import refresh_order_status, role_required, to_api_status, to_internal_status
from models import Order, OrderItem, db

barraca_bp = Blueprint("barraca", __name__)

ACTIVE = ("recebido", "preparando", "pronto")
HISTORY = ("entregue", "cancelado")
ALL_FILTERS = ("todos", "recebido", "preparando", "pronto", "entregue", "cancelado", "ativos", "historico")


@barraca_bp.route("/")
@role_required("garcom", "lojista")
def dashboard():
    status_filter = request.args.get("status", "ativos")
    if status_filter not in ALL_FILTERS:
        status_filter = "ativos"

    query = Order.query.order_by(Order.created_at.asc())
    if status_filter == "ativos":
        query = query.filter(Order.status.in_(ACTIVE))
    elif status_filter == "historico":
        query = query.filter(Order.status.in_(HISTORY))
    elif status_filter != "todos":
        query = query.filter(Order.status == status_filter)

    orders = query.all()

    counts = {
        "recebido": Order.query.filter_by(status="recebido").count(),
        "preparando": Order.query.filter_by(status="preparando").count(),
        "pronto": Order.query.filter_by(status="pronto").count(),
        "entregue": Order.query.filter_by(status="entregue").count(),
        "cancelado": Order.query.filter_by(status="cancelado").count(),
    }
    counts["ativos"] = counts["recebido"] + counts["preparando"] + counts["pronto"]

    return render_template(
        "barraca/dashboard.html",
        orders=orders,
        status_filter=status_filter,
        counts=counts,
        to_api_status=to_api_status,
    )


@barraca_bp.route("/pedido/<int:order_id>/status", methods=["POST"])
@role_required("garcom", "lojista")
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    raw = (request.form.get("status") or "").strip().lower()
    new_status = to_internal_status(raw)
    allowed = ("recebido", "preparando", "pronto", "entregue", "cancelado")
    if new_status not in allowed:
        flash("Status inválido.", "danger")
        return redirect(url_for("barraca.dashboard", status=request.args.get("status", "ativos")))

    order.status = new_status
    for item in order.items:
        if item.status == "cancelado" and new_status != "cancelado":
            continue
        if new_status == "cancelado":
            item.status = "cancelado"
        else:
            item.status = new_status
    db.session.commit()
    refresh_order_status(order)
    flash(f"Pedido #{order.id} → {to_api_status(order.status)}", "success")
    return redirect(url_for("barraca.dashboard", status=request.args.get("status", "ativos")))
