from datetime import datetime, timedelta
from functools import wraps

from flask import abort, flash, redirect, session, url_for

from models import Order, OrderItem
from models import Session as TentSession
from models import db

# Enunciado: recebido | em preparo | pronto | entregue | cancelado
API_STATUS = {
    "recebido": "recebido",
    "preparando": "em preparo",
    "em preparo": "em preparo",
    "pronto": "pronto",
    "entregue": "entregue",
    "cancelado": "cancelado",
}
INTERNAL_STATUS = {
    "recebido": "recebido",
    "em preparo": "preparando",
    "preparando": "preparando",
    "pronto": "pronto",
    "entregue": "entregue",
    "cancelado": "cancelado",
}
CANCEL_WINDOW_MINUTES = 5
DUPLICATE_WINDOW_MINUTES = 2


def to_api_status(status: str) -> str:
    return API_STATUS.get(status, status)


def to_internal_status(status: str) -> str:
    return INTERNAL_STATUS.get(status, status)


def estimate_wait_minutes(order: Order) -> int:
    """Estimativa simples: base + fila de pedidos ativos mais antigos."""
    if order.status in ("entregue", "cancelado", "pronto"):
        return 0
    ahead = (
        Order.query.filter(
            Order.status.in_(["recebido", "preparando"]),
            Order.created_at < order.created_at,
            Order.id != order.id,
        ).count()
    )
    return 8 + ahead * 3


def can_cancel_order(order: Order) -> bool:
    if order.status in ("entregue", "cancelado", "pronto"):
        return False
    if any(i.status in ("preparando", "pronto", "entregue") for i in order.items):
        return False
    limit = order.created_at + timedelta(minutes=CANCEL_WINDOW_MINUTES)
    return datetime.utcnow() <= limit


def recent_duplicate_order(tent_session: TentSession):
    cutoff = datetime.utcnow() - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)
    return (
        Order.query.filter(
            Order.session_id == tent_session.id,
            Order.created_at >= cutoff,
            Order.status.in_(["recebido", "preparando", "pronto"]),
        )
        .order_by(Order.created_at.desc())
        .first()
    )


def serialize_order_api(order: Order) -> dict:
    tent = order.session.tent if order.session else None
    return {
        "numero": order.id,
        "itens": [
            {
                "nome": i.product_name,
                "quantidade": i.quantity,
                "status": to_api_status(i.status),
                "observacao": i.notes or "",
            }
            for i in order.items
        ],
        "localizacao": f"Tenda {tent.number}" if tent else "Desconhecida",
        "tenda": tent.number if tent else None,
        "status": to_api_status(order.status),
        "horario": order.created_at.isoformat() + "Z",
        "horario_exibicao": order.created_at.strftime("%d/%m/%Y %H:%M"),
        "estimativa_minutos": estimate_wait_minutes(order),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Faça login para continuar.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def session_open_total(tent_session: TentSession) -> float:
    """Total ainda em aberto (ignora pedidos já pagos online/na entrega)."""
    total = 0.0
    for order in tent_session.orders:
        if order.status == "cancelado" or order.payment_status == "pago":
            continue
        for item in order.items:
            if item.status != "cancelado":
                total += item.subtotal
    return total


def session_gross_total(tent_session: TentSession) -> float:
    total = 0.0
    for order in tent_session.orders:
        if order.status == "cancelado":
            continue
        for item in order.items:
            if item.status != "cancelado":
                total += item.subtotal
    return total


def refresh_order_status(order) -> None:
    statuses = [i.status for i in order.items if i.status != "cancelado"]
    if not statuses:
        order.status = "cancelado"
    elif all(s == "entregue" for s in statuses):
        order.status = "entregue"
    elif all(s in ("pronto", "entregue") for s in statuses):
        order.status = "pronto"
    elif any(s == "preparando" for s in statuses) or any(s == "pronto" for s in statuses):
        order.status = "preparando"
    else:
        order.status = "recebido"
    db.session.commit()
