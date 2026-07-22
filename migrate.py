"""Garante colunas novas em SQLite sem precisar apagar o banco sempre."""

from sqlalchemy import inspect, text

from models import db


def ensure_schema() -> None:
    db.create_all()
    inspector = inspect(db.engine)

    def columns(table: str) -> set[str]:
        if table not in inspector.get_table_names():
            return set()
        return {c["name"] for c in inspector.get_columns(table)}

    alters = []

    product_cols = columns("products")
    if product_cols and "image_url" not in product_cols:
        alters.append("ALTER TABLE products ADD COLUMN image_url VARCHAR(500) DEFAULT ''")

    order_cols = columns("orders")
    if order_cols:
        if "payment_mode" not in order_cols:
            alters.append("ALTER TABLE orders ADD COLUMN payment_mode VARCHAR(20) DEFAULT 'na_conta'")
        if "payment_status" not in order_cols:
            alters.append("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pendente'")
        if "payment_method" not in order_cols:
            alters.append("ALTER TABLE orders ADD COLUMN payment_method VARCHAR(20) DEFAULT ''")

    payment_cols = columns("payments")
    if payment_cols and "order_id" not in payment_cols:
        alters.append("ALTER TABLE payments ADD COLUMN order_id INTEGER")

    for stmt in alters:
        db.session.execute(text(stmt))
    if alters:
        db.session.commit()
