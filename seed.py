"""Popula o banco SQLite com dados de demonstração."""

from datetime import date, datetime, timedelta

from app import create_app
from models import Category, Product, Reservation, Tent, User, db
from models import Order, OrderItem
from models import Session as TentSession

# Fotos locais (não dependem de link externo quebrado)
IMG = {
    "agua": "/static/img/products/agua.jpg",
    "cerveja": "/static/img/products/cerveja.jpg",
    "caipi": "/static/img/products/caipi.jpg",
    "suco": "/static/img/products/suco.jpg",
    "coco": "/static/img/products/coco.jpg",
    "refri": "/static/img/products/refri.jpg",
    "batata": "/static/img/products/batata.jpg",
    "peixe": "/static/img/products/peixe.jpg",
    "camarao": "/static/img/products/camarao.jpg",
    "pastel": "/static/img/products/pastel.jpg",
    "burger": "/static/img/products/burger.jpg",
    "hotdog": "/static/img/products/hotdog.jpg",
    "wrap": "/static/img/products/wrap.jpg",
    "acai": "/static/img/products/acai.jpg",
    "picole": "/static/img/products/picole.jpg",
    "tenda": "/static/img/products/tenda.jpg",
    "cadeira": "/static/img/products/cadeira.jpg",
    "guarda": "/static/img/products/guarda.jpg",
    "toalha": "/static/img/products/toalha.jpg",
}


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name="Lojista Demo", username="admin", role="lojista")
        admin.set_password("admin")
        garcom = User(name="Garçom Demo", username="garcom", role="garcom")
        garcom.set_password("garcom")
        db.session.add_all([admin, garcom])

        zones = ["Frente Mar", "Meio", "Fundo"]
        for n in range(1, 21):
            db.session.add(
                Tent(
                    number=n,
                    zone=zones[(n - 1) % 3],
                    capacity=4 if n % 2 == 0 else 2,
                    daily_price=100.0 if n <= 8 else 80.0,
                    status="livre",
                )
            )

        cats = [
            Category(name="Bebidas", sector="bar", sort_order=1),
            Category(name="Porções", sector="cozinha", sort_order=2),
            Category(name="Lanches", sector="cozinha", sort_order=3),
            Category(name="Sobremesas", sector="cozinha", sort_order=4),
            Category(name="Serviços", sector="servico", sort_order=5),
        ]
        db.session.add_all(cats)
        db.session.flush()

        products = [
            Product(category_id=cats[0].id, name="Água Mineral 500ml", description="Gelada, sem gás", price=5.0, stock_qty=120, stock_min=20, image_url=IMG["agua"]),
            Product(category_id=cats[0].id, name="Cerveja Lata", description="300ml bem gelada", price=9.0, stock_qty=200, stock_min=40, image_url=IMG["cerveja"]),
            Product(category_id=cats[0].id, name="Caipirinha", description="Limão, gelo e cachaça", price=18.0, stock_qty=80, stock_min=10, image_url=IMG["caipi"]),
            Product(category_id=cats[0].id, name="Suco Natural", description="Laranja ou maracujá", price=12.0, stock_qty=50, stock_min=10, image_url=IMG["suco"]),
            Product(category_id=cats[0].id, name="Água de Coco", description="Natural, gelada", price=10.0, stock_qty=60, stock_min=15, image_url=IMG["coco"]),
            Product(category_id=cats[0].id, name="Refrigerante Lata", description="Diversos sabores", price=8.0, stock_qty=100, stock_min=20, image_url=IMG["refri"]),
            Product(category_id=cats[1].id, name="Batata Frita", description="Porção grande crocante", price=28.0, stock_qty=40, stock_min=8, image_url=IMG["batata"]),
            Product(category_id=cats[1].id, name="Isca de Peixe", description="Com molho tártaro", price=42.0, stock_qty=30, stock_min=5, image_url=IMG["peixe"]),
            Product(category_id=cats[1].id, name="Camarão Empanado", description="400g servidos quentes", price=55.0, stock_qty=25, stock_min=5, image_url=IMG["camarao"]),
            Product(category_id=cats[1].id, name="Pastel de Feira", description="Carne ou queijo (6 un)", price=25.0, stock_qty=35, stock_min=8, image_url=IMG["pastel"]),
            Product(category_id=cats[2].id, name="X-Burger Praia", description="Blend 160g, queijo e salada", price=32.0, stock_qty=40, stock_min=8, image_url=IMG["burger"]),
            Product(category_id=cats[2].id, name="Hot Dog", description="Com milho e batata palha", price=18.0, stock_qty=45, stock_min=10, image_url=IMG["hotdog"]),
            Product(category_id=cats[2].id, name="Wrap de Frango", description="Com salada fresca", price=26.0, stock_qty=30, stock_min=6, image_url=IMG["wrap"]),
            Product(category_id=cats[3].id, name="Açaí 400ml", description="Com granola e banana", price=22.0, stock_qty=40, stock_min=8, image_url=IMG["acai"]),
            Product(category_id=cats[3].id, name="Picolé", description="Sabores de frutas", price=7.0, stock_qty=80, stock_min=15, image_url=IMG["picole"]),
            Product(category_id=cats[4].id, name="Aluguel de Tenda", description="Diária na areia", price=80.0, stock_qty=999, stock_min=0, kind="servico", image_url=IMG["tenda"]),
            Product(category_id=cats[4].id, name="Cadeira Extra", description="Aluguel unitário", price=15.0, stock_qty=999, stock_min=0, kind="servico", image_url=IMG["cadeira"]),
            Product(category_id=cats[4].id, name="Guarda-sol Extra", description="Aluguel do dia", price=20.0, stock_qty=999, stock_min=0, kind="servico", image_url=IMG["guarda"]),
            Product(category_id=cats[4].id, name="Toalha", description="Aluguel limpa", price=10.0, stock_qty=999, stock_min=0, kind="servico", image_url=IMG["toalha"]),
        ]
        db.session.add_all(products)

        db.session.flush()
        tent1 = Tent.query.filter_by(number=1).first()
        tent5 = Tent.query.filter_by(number=5).first()
        tent5.status = "reservada"
        db.session.add_all(
            [
                Reservation(
                    tent_id=tent1.id,
                    customer_name="Ana Silva",
                    customer_phone="11999990001",
                    date=date.today() + timedelta(days=1),
                    time_slot="manhã",
                    value=tent1.daily_price,
                    status="confirmada",
                ),
                Reservation(
                    tent_id=tent5.id,
                    customer_name="Carlos Souza",
                    customer_phone="21988887777",
                    date=date.today(),
                    time_slot="dia todo",
                    value=tent5.daily_price,
                    status="confirmada",
                ),
            ]
        )

        # 3 pedidos de exemplo (enunciado): recebido | em preparo | entregue
        agua = Product.query.filter_by(name="Água de Coco").first()
        batata = Product.query.filter_by(name="Batata Frita").first()
        cerveja = Product.query.filter_by(name="Cerveja Lata").first()
        burger = Product.query.filter_by(name="X-Burger Praia").first()

        def _demo_order(tent_number, customer, items, status, minutes_ago):
            tent = Tent.query.filter_by(number=tent_number).first()
            tent.status = "ocupada" if status != "entregue" else "livre"
            sess = TentSession(
                tent_id=tent.id,
                customer_name=customer,
                status="aberta" if status != "entregue" else "fechada",
                opened_at=datetime.utcnow() - timedelta(minutes=minutes_ago + 5),
                closed_at=datetime.utcnow() - timedelta(minutes=1) if status == "entregue" else None,
                rental_charged=True,
            )
            db.session.add(sess)
            db.session.flush()
            order = Order(
                session_id=sess.id,
                status=status,
                source="cliente",
                payment_mode="na_conta",
                payment_status="pendente" if status != "entregue" else "pago",
                created_at=datetime.utcnow() - timedelta(minutes=minutes_ago),
                notes="Pedido demo avaliação",
            )
            db.session.add(order)
            db.session.flush()
            for product, qty in items:
                db.session.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=qty,
                        status=status,
                        sector=product.category.sector,
                    )
                )
            return order

        o_rec = _demo_order(3, "Demo Recebido", [(agua, 2), (cerveja, 1)], "recebido", 12)
        o_prep = _demo_order(7, "Demo Preparo", [(batata, 1), (burger, 1)], "preparando", 20)
        o_ent = _demo_order(12, "Demo Entregue", [(agua, 1)], "entregue", 45)

        db.session.commit()
        print("Banco seedado com sucesso!")
        print("  admin / admin  (lojista)")
        print("  garcom / garcom")
        print("  PIN do dia para cliente: 1234")
        print(f"  Pedidos demo API: #{o_rec.id} recebido | #{o_prep.id} em preparo | #{o_ent.id} entregue")


if __name__ == "__main__":
    seed()
