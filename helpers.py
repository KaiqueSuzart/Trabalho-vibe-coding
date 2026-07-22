from functools import wraps

from flask import abort, flash, redirect, session, url_for

from models import Session as TentSession
from models import db


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
