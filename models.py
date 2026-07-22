from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # lojista | garcom
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Tent(db.Model):
    __tablename__ = "tents"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    zone = db.Column(db.String(40), default="Areia")
    capacity = db.Column(db.Integer, default=4)
    daily_price = db.Column(db.Float, default=80.0)
    # livre | reservada | ocupada | manutencao
    status = db.Column(db.String(20), default="livre")
    notes = db.Column(db.String(255), default="")

    reservations = db.relationship("Reservation", back_populates="tent", lazy=True)
    sessions = db.relationship("Session", back_populates="tent", lazy=True)


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    tent_id = db.Column(db.Integer, db.ForeignKey("tents.id"), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(40), default="")
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), default="dia todo")
    value = db.Column(db.Float, default=0.0)
    # pendente | confirmada | checkin | cancelada | concluida
    status = db.Column(db.String(20), default="confirmada")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tent = db.relationship("Tent", back_populates="reservations")


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    tent_id = db.Column(db.Integer, db.ForeignKey("tents.id"), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=True)
    customer_name = db.Column(db.String(120), default="Cliente")
    customer_phone = db.Column(db.String(40), default="")
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    # aberta | fechamento_solicitado | fechada
    status = db.Column(db.String(30), default="aberta")
    rental_charged = db.Column(db.Boolean, default=False)

    tent = db.relationship("Tent", back_populates="sessions")
    reservation = db.relationship("Reservation")
    orders = db.relationship("Order", back_populates="session", lazy=True)
    payments = db.relationship("Payment", back_populates="session", lazy=True)

    @property
    def is_open(self) -> bool:
        return self.status in ("aberta", "fechamento_solicitado")


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    # bar | cozinha | servico
    sector = db.Column(db.String(20), default="cozinha")
    sort_order = db.Column(db.Integer, default=0)

    products = db.relationship("Product", back_populates="category", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), default="")
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    stock_qty = db.Column(db.Integer, default=0)
    stock_min = db.Column(db.Integer, default=5)
    # produto | servico (aluguel extra)
    kind = db.Column(db.String(20), default="produto")
    image_url = db.Column(db.String(500), default="")

    category = db.relationship("Category", back_populates="products")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255), default="")
    # recebido | preparando | pronto | entregue | cancelado
    status = db.Column(db.String(20), default="recebido")
    source = db.Column(db.String(20), default="cliente")  # cliente | garcom
    # online | na_entrega | na_conta
    payment_mode = db.Column(db.String(20), default="na_conta")
    # pendente | pago | cobrar_entrega
    payment_status = db.Column(db.String(20), default="pendente")
    payment_method = db.Column(db.String(20), default="")  # pix | cartao | dinheiro

    session = db.relationship("Session", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", lazy=True, cascade="all, delete-orphan")

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def is_paid(self) -> bool:
        return self.payment_status == "pago"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    notes = db.Column(db.String(255), default="")
    # recebido | preparando | pronto | entregue | cancelado
    status = db.Column(db.String(20), default="recebido")
    sector = db.Column(db.String(20), default="cozinha")

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    method = db.Column(db.String(20), nullable=False)  # dinheiro | pix | cartao
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255), default="")

    session = db.relationship("Session", back_populates="payments")
    order = db.relationship("Order")


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # positivo entrada, negativo saída
    reason = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    product = db.relationship("Product")
    user = db.relationship("User")
