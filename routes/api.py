from flask import Blueprint, jsonify

from helpers import serialize_order_api
from models import Order, Tent
from models import Session as TentSession
from flask import session

api_bp = Blueprint("api", __name__)


@api_bp.route("/pedido/<int:numero>")
def pedido_status(numero):
    """GET /api/pedido/:numero — enunciado do professor (200 ou 404)."""
    order = Order.query.get(numero)
    if not order:
        return (
            jsonify(
                {
                    "erro": True,
                    "mensagem": f"Pedido #{numero} não encontrado.",
                    "numero": numero,
                }
            ),
            404,
        )
    return jsonify(serialize_order_api(order)), 200


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
    if session.get("client_session_id") and session.get("client_session_id") != session_id:
        if not session.get("user_id"):
            return jsonify({"error": "forbidden"}), 403

    tent_session = TentSession.query.get_or_404(session_id)
    payload = []
    for order in tent_session.orders:
        payload.append(serialize_order_api(order))
    return jsonify({"session_status": tent_session.status, "orders": payload})


@api_bp.route("/kitchen/pending")
def kitchen_pending():
    from models import OrderItem

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
    from models import OrderItem

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
