"""Smoke test: todas as abas/rotas principais e botões críticos."""

from app import create_app
from models import Order, Product, Tent, db
from models import Session as TentSession


def main():
    app = create_app()
    guest = app.test_client()
    staff = app.test_client()
    admin = app.test_client()
    fails = []

    def ok(cond, msg):
        if cond:
            print(f"  OK  {msg}")
        else:
            print(f" FAIL {msg}")
            fails.append(msg)

    def get_ok(client, path, label=None):
        r = client.get(path)
        label = label or f"GET {path}"
        ok(r.status_code == 200, f"{label} ({r.status_code})")
        return r

    print("=== A) Páginas públicas (nav / abas cliente) ===")
    for path in (
        "/",
        "/pedir",
        "/cardapio",
        "/reservar",
        "/acompanhar",
        "/teste-api",
        "/login",
    ):
        get_ok(guest, path)

    print("=== B) API enunciado ===")
    with app.app_context():
        demo = Order.query.filter_by(notes="Pedido demo avaliação").order_by(Order.id).all()
        ids = [o.id for o in demo]
        ok(len(ids) >= 3, f"pedidos demo >= 3 (tem {len(ids)})")
    if ids:
        r = guest.get(f"/api/pedido/{ids[0]}")
        ok(r.status_code == 200 and "numero" in (r.get_json() or {}), "API 200")
    r = guest.get("/api/pedido/999999")
    ok(r.status_code == 404, "API 404")
    get_ok(guest, "/api/tents", "API /api/tents")

    print("=== C) Login equipe ===")
    r = staff.post("/login", data={"username": "garcom", "password": "garcom"}, follow_redirects=False)
    ok(r.status_code in (302, 303), "login garçom")
    r = admin.post("/login", data={"username": "admin", "password": "admin"}, follow_redirects=False)
    ok(r.status_code in (302, 303), "login admin")

    print("=== D) Abas garçom / barraca / cozinha ===")
    for path in (
        "/garcom/",
        "/garcom/checkin",
        "/garcom/pedido-manual",
        "/garcom/mapa",
        "/barraca/",
        "/barraca/?status=ativos",
        "/barraca/?status=recebido",
        "/barraca/?status=preparando",
        "/barraca/?status=historico",
        "/barraca/?status=todos",
        "/cozinha/",
        "/cozinha/?setor=bar",
        "/cozinha/?setor=cozinha",
    ):
        get_ok(staff, path)

    print("=== E) Abas admin ===")
    for path in (
        "/admin/",
        "/admin/produtos",
        "/admin/categorias",
        "/admin/tendas",
        "/admin/estoque",
        "/admin/usuarios",
        "/admin/reservas",
        "/admin/relatorios",
        "/admin/mapa",
    ):
        get_ok(admin, path)

    print("=== F) Fluxo botoes: pedir -> barraca status -> acompanhar ===")
    with app.app_context():
        tent = Tent.query.filter_by(status="livre").order_by(Tent.number).first()
        product = Product.query.filter_by(name="Água Mineral 500ml", available=True).first()
        ok(tent is not None and product is not None, "tenda livre + produto")
        tent_n = tent.number
        pid = product.id

    r = guest.post("/pedir", data={"tent_number": str(tent_n), "pin": "1234"}, follow_redirects=False)
    ok(r.status_code in (302, 303) and f"/t/{tent_n}" in r.headers.get("Location", ""), "botão abrir tenda (PIN)")

    get_ok(guest, f"/t/{tent_n}")
    get_ok(guest, f"/t/{tent_n}/cardapio")
    get_ok(guest, f"/t/{tent_n}/carrinho")
    get_ok(guest, f"/t/{tent_n}/pedidos")
    get_ok(guest, f"/t/{tent_n}/conta")

    r = guest.post(
        f"/t/{tent_n}/carrinho/add",
        data={"product_id": str(pid), "quantity": "1", "notes": "smoke"},
        follow_redirects=True,
    )
    ok(r.status_code == 200, "botão adicionar ao carrinho")

    r = guest.post(
        f"/t/{tent_n}/pedir",
        data={"payment_mode": "na_conta", "order_notes": "smoke test"},
        follow_redirects=False,
    )
    ok(r.status_code in (302, 303), "botão enviar pedido")

    with app.app_context():
        order = Order.query.filter_by(notes="smoke test").order_by(Order.id.desc()).first()
        ok(order is not None, "pedido criado")
        oid = order.id if order else None

    if oid:
        r = staff.post(f"/barraca/pedido/{oid}/status", data={"status": "em preparo"}, follow_redirects=True)
        ok(r.status_code == 200, "botão barraca → em preparo")
        with app.app_context():
            o = db.session.get(Order, oid)
            ok(o and o.status == "preparando", "status preparando no banco")

        r = staff.post(f"/barraca/pedido/{oid}/status", data={"status": "pronto"}, follow_redirects=True)
        ok(r.status_code == 200, "botão barraca → pronto")
        r = staff.post(f"/barraca/pedido/{oid}/status", data={"status": "entregue"}, follow_redirects=True)
        ok(r.status_code == 200, "botão barraca → entregue")

        r = guest.get(f"/api/pedido/{oid}")
        data = r.get_json() or {}
        ok(r.status_code == 200 and data.get("status") == "entregue", "API acompanha status entregue")

    print("=== G) Reserva + admin mapa ===")
    with app.app_context():
        from datetime import date, timedelta

        free = Tent.query.filter_by(status="livre").order_by(Tent.number).first()
        tid = free.id
        d = (date.today() + timedelta(days=2)).isoformat()
    r = guest.post(
        "/reservar",
        data={
            "tent_id": str(tid),
            "customer_name": "Smoke Teste",
            "customer_phone": "11999999999",
            "date": d,
            "time_slot": "manhã",
        },
        follow_redirects=True,
    )
    ok(r.status_code == 200, "botao reservar tenda")

    print("=== H) Logout ===")
    r = staff.get("/logout", follow_redirects=False)
    ok(r.status_code in (302, 303), "logout")

    print()
    if fails:
        print(f"SMOKE: {len(fails)} falha(s)")
        for f in fails:
            print(" -", f)
        raise SystemExit(1)
    print("SMOKE: todas as abas/botões OK")


if __name__ == "__main__":
    main()
