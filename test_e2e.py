"""Teste ponta a ponta: reserva/pedido/cozinha/garçom/admin/pagamento."""

from app import create_app
from models import Order, OrderItem, Payment, Product, Tent, User, db
from models import Session as TentSession


def main():
    app = create_app()
    client = app.test_client()
    staff = app.test_client()
    admin = app.test_client()
    fails = []

    def ok(cond, msg):
        if cond:
            print(f"  OK  {msg}")
        else:
            print(f" FAIL {msg}")
            fails.append(msg)

    print("0) Enunciado professor — API / painel / telas")
    r = client.get("/teste-api")
    ok(r.status_code == 200, "GET /teste-api")
    r = client.get("/acompanhar")
    ok(r.status_code == 200, "GET /acompanhar")
    with app.app_context():
        demo_rec = Order.query.filter_by(status="recebido", notes="Pedido demo avaliação").first()
        demo_prep = Order.query.filter_by(status="preparando", notes="Pedido demo avaliação").first()
        demo_ent = Order.query.filter_by(status="entregue", notes="Pedido demo avaliação").first()
        ok(demo_rec and demo_prep and demo_ent, "3 pedidos demo no seed")
        demo_ids = {
            "recebido": demo_rec.id if demo_rec else None,
            "preparando": demo_prep.id if demo_prep else None,
            "entregue": demo_ent.id if demo_ent else None,
        }
    if demo_ids.get("recebido"):
        r = client.get(f"/api/pedido/{demo_ids['recebido']}")
        ok(r.status_code == 200, "API 200 pedido existente")
        data = r.get_json()
        ok(data and data.get("status") == "recebido" and "itens" in data and "localizacao" in data, "API payload completo")
        ok("horario" in data, "API tem horario")
    if demo_ids.get("preparando"):
        r = client.get(f"/api/pedido/{demo_ids['preparando']}")
        ok(r.status_code == 200 and r.get_json().get("status") == "em preparo", "API mapeia em preparo")
    if demo_ids.get("entregue"):
        r = client.get(f"/api/pedido/{demo_ids['entregue']}")
        ok(r.status_code == 200 and r.get_json().get("status") == "entregue", "API entregue")
    r = client.get("/api/pedido/999999")
    ok(r.status_code == 404, "API 404 inexistente")
    err = r.get_json() or {}
    ok(err.get("mensagem") or err.get("erro"), "API 404 com mensagem")

    r = staff.post("/login", data={"username": "garcom", "password": "garcom"}, follow_redirects=False)
    ok(r.status_code in (302, 303), "login garçom (pré)")
    r = staff.get("/barraca/")
    ok(r.status_code == 200, "GET /barraca/")
    ok(b"Painel da Barraca" in r.data, "painel barraca renderiza")
    ok(b"Recebido" in r.data or b"recebido" in r.data.lower(), "contadores/filtro no painel")

    print("1) Home / cardápio / pedir")
    ok(client.get("/").status_code == 200, "GET /")
    ok(client.get("/cardapio").status_code == 200, "GET /cardapio")
    ok(client.get("/pedir").status_code == 200, "GET /pedir")

    print("2) Login equipe")
    r = staff.post("/login", data={"username": "garcom", "password": "garcom"}, follow_redirects=False)
    ok(r.status_code in (302, 303), "login garçom")
    r = admin.post("/login", data={"username": "admin", "password": "admin"}, follow_redirects=False)
    ok(r.status_code in (302, 303), "login admin")

    print("3) Abrir tenda livre via PIN (self check-in)")
    with app.app_context():
        tent = Tent.query.filter_by(status="livre").order_by(Tent.number).first()
        ok(tent is not None, "existe tenda livre")
        tent_number = tent.number
        product = Product.query.filter_by(name="Cerveja Lata", available=True).first()
        ok(product is not None, "produto Cerveja Lata")
        stock_before = product.stock_qty
        product_id = product.id

    r = client.post(
        "/pedir",
        data={"tent_number": str(tent_number), "pin": "1234"},
        follow_redirects=False,
    )
    ok(r.status_code in (302, 303) and f"/t/{tent_number}/cardapio" in r.headers.get("Location", ""), "abrir cardápio")

    print("4) Pedido na conta")
    r = client.post(
        f"/t/{tent_number}/carrinho/add",
        data={"product_id": product_id, "quantity": 2, "notes": "bem gelada"},
        follow_redirects=True,
    )
    ok(r.status_code == 200, "add carrinho")
    r = client.post(
        f"/t/{tent_number}/pedir",
        data={"payment_mode": "na_conta", "order_notes": "teste e2e"},
        follow_redirects=False,
    )
    ok(r.status_code in (302, 303), "enviar pedido")

    with app.app_context():
        order = Order.query.filter_by(source="cliente").order_by(Order.id.desc()).first()
        ok(order is not None and order.status == "recebido", f"pedido salvo #{getattr(order,'id',None)}")
        ok(order.payment_mode == "na_conta", "payment_mode na_conta")
        item = order.items[0]
        ok(item.status == "recebido" and item.quantity == 2, "item recebido qtd=2")
        order_id = order.id
        item_id = item.id
        p = Product.query.get(product_id)
        ok(p.stock_qty == stock_before - 2, f"estoque baixou {stock_before}->{p.stock_qty}")
        tent = Tent.query.filter_by(number=tent_number).first()
        ok(tent.status == "ocupada", "tenda ocupada no banco")

    print("5) Painel garçom vê pedido em andamento")
    r = staff.get("/garcom/")
    ok(r.status_code == 200, "GET /garcom/")
    body = r.data.decode("utf-8", errors="ignore")
    ok(f"Pedido #{order_id}" in body or f"#{order_id}" in body, "pedido listado no garçom")
    ok("Pedidos em andamento" in body, "seção em andamento")

    print("6) Cozinha prepara e marca pronto")
    r = staff.get("/cozinha/")
    ok(r.status_code == 200, "GET /cozinha/")
    ok(str(item_id).encode() in r.data or b"Cerveja" in r.data, "item na cozinha")
    r = staff.post(f"/cozinha/item/{item_id}/status", data={"status": "preparando"}, follow_redirects=True)
    ok(r.status_code == 200, "status preparando")
    r = staff.post(f"/cozinha/item/{item_id}/status", data={"status": "pronto"}, follow_redirects=True)
    ok(r.status_code == 200, "status pronto")
    with app.app_context():
        item = OrderItem.query.get(item_id)
        ok(item.status == "pronto", "item pronto no banco")

    print("7) Garçom entrega")
    r = staff.get("/garcom/")
    ok(b"Entregar" in r.data, "botão entregar visível")
    r = staff.post(f"/garcom/entregar/{item_id}", data={}, follow_redirects=True)
    ok(r.status_code == 200, "entregar")
    with app.app_context():
        item = OrderItem.query.get(item_id)
        order = Order.query.get(order_id)
        ok(item.status == "entregue", "item entregue")
        ok(order.status == "entregue", "pedido entregue")

    print("8) Pedido online + pagamento")
    r = client.post(
        f"/t/{tent_number}/carrinho/add",
        data={"product_id": product_id, "quantity": 1, "notes": ""},
    )
    r = client.post(
        f"/t/{tent_number}/pedir",
        data={"payment_mode": "online", "online_method": "pix", "order_notes": ""},
        follow_redirects=False,
    )
    loc = r.headers.get("Location", "")
    ok("/pagar/" in loc, f"redirect pagar {loc}")
    pay_order_id = int(loc.rstrip("/").split("/")[-1])
    with app.app_context():
        o = Order.query.get(pay_order_id)
        ok(o.payment_status == "pendente", "online pendente")
        # cozinha nao deve pegar ainda
        kitchen_pending = (
            OrderItem.query.join(Order)
            .filter(OrderItem.order_id == pay_order_id, OrderItem.status == "recebido")
            .count()
        )
    r = staff.get("/cozinha/")
    # after pay:
    r = client.post(f"/t/{tent_number}/pagar/{pay_order_id}", data={"method": "pix"}, follow_redirects=True)
    ok(r.status_code == 200, "confirmar pix")
    with app.app_context():
        o = Order.query.get(pay_order_id)
        ok(o.payment_status == "pago", "pedido pago")
        pays = Payment.query.filter_by(order_id=pay_order_id).count()
        ok(pays == 1, "Payment salvo")

    print("9) Admin dashboard / produtos / estoque / relatorios")
    r = admin.get("/admin/")
    ok(r.status_code == 200, "admin dashboard")
    ok(b"Faturamento" in r.data or b"faturamento" in r.data.lower(), "dashboard com faturamento")
    r = admin.get("/admin/produtos")
    ok(r.status_code == 200, "admin produtos")
    r = admin.post(
        "/admin/produtos",
        data={
            "action": "create",
            "name": "Produto Teste E2E",
            "category_id": "1",
            "price": "11.50",
            "stock_qty": "10",
            "stock_min": "2",
            "kind": "produto",
            "description": "teste",
            "image_url": "",
        },
        follow_redirects=True,
    )
    ok(r.status_code == 200, "criar produto")
    with app.app_context():
        p = Product.query.filter_by(name="Produto Teste E2E").order_by(Product.id.desc()).first()
        ok(p is not None and p.price == 11.5, "produto persistido")
        pid = p.id
        # garante base conhecida para o teste de estoque
        p.stock_qty = 10
        db.session.commit()
    r = admin.post(
        "/admin/estoque",
        data={"product_id": str(pid), "quantity": "5", "reason": "teste entrada"},
        follow_redirects=True,
    )
    ok(r.status_code == 200, "ajuste estoque")
    with app.app_context():
        p = Product.query.get(pid)
        ok(p.stock_qty == 15, f"estoque 15 (foi {p.stock_qty})")
        # limpa produto de teste para não aparecer no cardápio demo
        from models import StockMovement

        StockMovement.query.filter_by(product_id=pid).delete()
        db.session.delete(p)
        db.session.commit()
    r = admin.get("/admin/relatorios")
    ok(r.status_code == 200, "relatorios")
    r = admin.get("/admin/reservas")
    ok(r.status_code == 200, "reservas")
    r = admin.get("/admin/mapa")
    ok(r.status_code == 200, "mapa admin")

    print("10) Fechar conta")
    with app.app_context():
        sess = (
            TentSession.query.join(Tent)
            .filter(Tent.number == tent_number, TentSession.status.in_(["aberta", "fechamento_solicitado"]))
            .first()
        )
        sid = sess.id
    r = client.post(f"/t/{tent_number}/fechar", follow_redirects=True)
    ok(r.status_code == 200, "cliente pediu fechamento")
    r = staff.get(f"/garcom/conta/{sid}")
    ok(r.status_code == 200, "garçom vê conta")
    # pagar restante
    import re
    from helpers import session_open_total

    with app.app_context():
        sess = TentSession.query.get(sid)
        remaining = session_open_total(sess)
    if remaining > 0.01:
        r = staff.post(
            f"/garcom/conta/{sid}",
            data={"method": "pix", "amount": f"{remaining:.2f}", "notes": "e2e"},
            follow_redirects=True,
        )
        ok(r.status_code == 200, "pagamento fechamento")
    with app.app_context():
        sess = TentSession.query.get(sid)
        tent = Tent.query.filter_by(number=tent_number).first()
        ok(sess.status == "fechada", "sessão fechada")
        ok(tent.status == "livre", "tenda liberada")

    print()
    if fails:
        print(f"RESULTADO: {len(fails)} falha(s)")
        for f in fails:
            print(" -", f)
        raise SystemExit(1)
    print("RESULTADO: todos os testes passaram")


if __name__ == "__main__":
    main()
