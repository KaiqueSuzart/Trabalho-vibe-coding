from flask import Blueprint, jsonify

from helpers import serialize_order_api
from models import Order, Tent
from models import Session as TentSession
from flask import session

api_bp = Blueprint("api", __name__)


def _not_found(numero):
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


@api_bp.route("/pedido/<numero>")
def pedido_status(numero):
    """GET /api/pedido/:numero — enunciado do professor (200 ou 404).

    Aceita numero como string e valida internamente: assim um número não
    inteiro (ex.: /api/pedido/abc) devolve o MESMO JSON de 404 do contrato,
    e não a página de erro HTML padrão do Flask.
    """
    try:
        pedido_id = int(numero)
    except (TypeError, ValueError):
        return _not_found(numero)

    order = Order.query.get(pedido_id)
    if not order:
        return _not_found(pedido_id)
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
    # Só o dono da sessão (cliente com check-in nesta tenda) ou a equipe logada
    # podem ler os pedidos. Sem isso, qualquer um itera o ID e lê o consumo
    # de qualquer tenda.
    is_staff = bool(session.get("user_id"))
    is_owner = session.get("client_session_id") == session_id
    if not (is_staff or is_owner):
        return jsonify({"error": "forbidden"}), 403

    tent_session = TentSession.query.get_or_404(session_id)
    payload = []
    for order in tent_session.orders:
        payload.append(serialize_order_api(order))
    return jsonify({"session_status": tent_session.status, "orders": payload})


@api_bp.route("/barraca/summary")
def barraca_summary():
    """Assinatura leve dos pedidos ativos para o painel detectar novidade
    sem recarregar a página inteira a cada ciclo."""
    if not session.get("user_id"):
        return jsonify({"error": "unauthorized"}), 401
    rows = (
        Order.query.with_entities(Order.id, Order.status)
        .filter(Order.status.in_(["recebido", "preparando", "pronto"]))
        .order_by(Order.id.asc())
        .all()
    )
    signature = ";".join(f"{oid}:{st}" for oid, st in rows)
    return jsonify({"count": len(rows), "signature": signature})


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
