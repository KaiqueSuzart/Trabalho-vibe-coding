from flask import Blueprint, jsonify, session

from models import Order, OrderItem, Tent
from models import Session as TentSession

api_bp = Blueprint("api", __name__)


@api_bp.route("/tents")
def tents_status():
    tents = Tent.query.order_by(Tent.number).all()
    return jsonify(
        [
            {
                "id": t.id,
                "number": t.number,
                "zone": t.zone,
                "status": t.status,
                "capacity": t.capacity,
                "daily_price": t.daily_price,
            }
            for t in tents
        ]
    )


@api_bp.route("/session/<int:session_id>/orders")
def session_orders(session_id):
    # cliente só vê a própria sessão
    if session.get("client_session_id") and session.get("client_session_id") != session_id:
        if not session.get("user_id"):
            return jsonify({"error": "forbidden"}), 403

    tent_session = TentSession.query.get_or_404(session_id)
    payload = []
    for order in tent_session.orders:
        payload.append(
            {
                "id": order.id,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "items": [
                    {
                        "id": i.id,
                        "name": i.product_name,
                        "quantity": i.quantity,
                        "status": i.status,
                        "sector": i.sector,
                    }
                    for i in order.items
                ],
            }
        )
    return jsonify({"session_status": tent_session.status, "orders": payload})


@api_bp.route("/kitchen/pending")
def kitchen_pending():
    if not session.get("user_id"):
        return jsonify({"error": "unauthorized"}), 401
    items = (
        OrderItem.query.join(Order)
        .filter(OrderItem.status.in_(["recebido", "preparando"]), OrderItem.sector != "servico")
        .order_by(Order.created_at.asc())
        .all()
    )
    return jsonify(
        [
            {
                "id": i.id,
                "product": i.product_name,
                "quantity": i.quantity,
                "status": i.status,
                "sector": i.sector,
                "tent": i.order.session.tent.number,
                "order_id": i.order_id,
            }
            for i in items
        ]
    )


@api_bp.route("/waiter/ready")
def waiter_ready():
    if not session.get("user_id"):
        return jsonify({"error": "unauthorized"}), 401
    items = OrderItem.query.filter_by(status="pronto").all()
    return jsonify(
        [
            {
                "id": i.id,
                "product": i.product_name,
                "quantity": i.quantity,
                "tent": i.order.session.tent.number,
                "order_id": i.order_id,
            }
            for i in items
        ]
    )
