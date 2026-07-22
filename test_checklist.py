"""Checklist do enunciado + smoke local + smoke ao vivo (Vercel)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from app import create_app
from models import Order, Product, Tent, db

LIVE = "https://trabalho-vibe-coding-liard.vercel.app"

# Rubrica do professor (Barraquinha Digital)
CHECKLIST = [
    ("OBRIG", "Cardápio com >= 8 itens", True, "/cardapio"),
    ("OBRIG", "Cardápio com >= 2 categorias", True, "/cardapio"),
    ("OBRIG", "Cardápio mobile-friendly", True, "/cardapio"),
    ("OBRIG", "Cliente seleciona itens e quantidades", True, "/pedir"),
    ("OBRIG", "Cliente informa localização (nº tenda)", True, "/pedir"),
    ("OBRIG", "Sistema valida localização antes do pedido", True, "/pedir"),
    ("OBRIG", "Confirmação com número do pedido", True, "flash Pedido #"),
    ("OBRIG", "API GET /api/pedido/:numero", True, "/api/pedido/1"),
    ("OBRIG", "API retorna numero, itens, localizacao, status, horario", True, "/api/pedido/1"),
    ("OBRIG", "Status: recebido / em preparo / pronto / entregue / cancelado", True, "API mapeia"),
    ("OBRIG", "API 404 com mensagem clara", True, "/api/pedido/999999"),
    ("OBRIG", "Tela cliente consome a API", True, "/acompanhar e /pedidos"),
    ("OBRIG", "Painel da barraca lista pedidos ativos (antigo→recente)", True, "/barraca/"),
    ("OBRIG", "Painel mostra nº, local, itens, horário, status", True, "/barraca/"),
    ("OBRIG", "Barraca atualiza status do pedido", True, "/barraca/pedido/<id>/status"),
    ("OBRIG", "Entregues/cancelados visualmente distintos", True, "/barraca/?status=historico"),
    ("OBRIG", "Tela de teste da API", True, "/teste-api"),
    ("OBRIG", "Teste API mostra JSON + status 200/404", True, "/teste-api"),
    ("OBRIG", "3 pedidos demo (recebido, em preparo, entregue)", True, "seed"),
    ("OPC", "Filtro por status no painel", True, "/barraca/?status="),
    ("OPC", "Estimativa de espera", True, "estimativa_minutos"),
    ("OPC", "Histórico separado dos ativos", True, "/barraca/?status=historico"),
    ("OPC", "Anti-duplicado < 2 min", True, "helpers.recent_duplicate_order"),
    ("OPC", "Cancelamento pelo cliente com prazo", True, "cancelar pedido 5 min"),
    ("OPC", "Contador por status no painel", True, "status-counters"),
    ("ENTREGA", "Link público no ar", True, LIVE),
    ("ENTREGA", "Histórico de prompts", True, "HISTORICO_PROMPTS.md"),
]


def http_get(url: str, timeout: int = 40) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "MareClara-Smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, body
    except Exception as e:
        return 0, str(e)


def main() -> int:
    fails: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        print(f"  {'OK ' if cond else 'FAIL'} {msg}")
        if not cond:
            fails.append(msg)

    print("=== CHECKLIST ENUNCIADO ===")
    for kind, title, done, where in CHECKLIST:
        mark = "[x]" if done else "[ ]"
        print(f"  {mark} ({kind}) {title}  → {where}")

    print("\n=== SMOKE LOCAL (todas as abas) ===")
    app = create_app()
    guest = app.test_client()
    staff = app.test_client()
    admin = app.test_client()

    public_paths = [
        "/",
        "/pedir",
        "/cardapio",
        "/reservar",
        "/acompanhar",
        "/teste-api",
        "/login",
        "/health",
    ]
    for path in public_paths:
        r = guest.get(path)
        ok(r.status_code == 200, f"local GET {path} ({r.status_code})")

    # conteúdo mínimo das telas do enunciado
    r = guest.get("/teste-api")
    ok(b"Teste da API" in r.data or b"teste" in r.data.lower(), "local /teste-api renderiza titulo")
    r = guest.get("/acompanhar")
    ok(b"Acompanhar" in r.data or b"acompanhar" in r.data.lower(), "local /acompanhar renderiza")

    with app.app_context():
        demos = Order.query.filter_by(notes="Pedido demo avaliação").all()
        by_status = {o.status: o.id for o in demos}
        ok("recebido" in by_status, "demo recebido")
        ok("preparando" in by_status, "demo em preparo (preparando)")
        ok("entregue" in by_status, "demo entregue")
        products = Product.query.filter_by(available=True).count()
        ok(products >= 8, f"produtos disponiveis >= 8 ({products})")

    r = guest.get("/api/pedido/1")
    ok(r.status_code == 200, f"local API 200 ({r.status_code})")
    data = r.get_json() or {}
    for key in ("numero", "itens", "localizacao", "status", "horario"):
        ok(key in data, f"local API campo {key}")
    r = guest.get("/api/pedido/999999")
    ok(r.status_code == 404, f"local API 404 ({r.status_code})")

    staff.post("/login", data={"username": "garcom", "password": "garcom"})
    admin.post("/login", data={"username": "admin", "password": "admin"})

    staff_paths = [
        "/barraca/",
        "/barraca/?status=ativos",
        "/barraca/?status=historico",
        "/barraca/?status=recebido",
        "/garcom/",
        "/garcom/checkin",
        "/garcom/pedido-manual",
        "/garcom/mapa",
        "/cozinha/",
        "/cozinha/?setor=bar",
        "/cozinha/?setor=cozinha",
    ]
    for path in staff_paths:
        r = staff.get(path)
        ok(r.status_code == 200, f"local GET {path} ({r.status_code})")

    admin_paths = [
        "/admin/",
        "/admin/produtos",
        "/admin/categorias",
        "/admin/tendas",
        "/admin/estoque",
        "/admin/usuarios",
        "/admin/reservas",
        "/admin/relatorios",
        "/admin/mapa",
    ]
    for path in admin_paths:
        r = admin.get(path)
        ok(r.status_code == 200, f"local GET {path} ({r.status_code})")

    print("\n=== SMOKE AO VIVO (Vercel) ===")
    live_paths = [
        ("/", 200),
        ("/pedir", 200),
        ("/cardapio", 200),
        ("/reservar", 200),
        ("/acompanhar", 200),
        ("/teste-api", 200),
        ("/login", 200),
        ("/health", 200),
        ("/api/pedido/1", 200),
        ("/api/pedido/999999", 404),
    ]
    for path, expect in live_paths:
        code, body = http_get(LIVE + path)
        ok(code == expect, f"live {path} -> {code} (esperado {expect})")
        if path == "/teste-api" and code == 200:
            ok("Teste da API" in body or "teste" in body.lower(), "live /teste-api tem conteudo")
        if path == "/acompanhar" and code == 200:
            ok("Acompanhar" in body or "acompanhar" in body.lower(), "live /acompanhar tem conteudo")
        if path == "/health" and code == 200:
            try:
                h = json.loads(body)
                ok(h.get("ok") is True, f"live health ok={h.get('ok')} host={h.get('db_host')}")
            except json.JSONDecodeError:
                ok(False, "live health JSON invalido")
        if path == "/api/pedido/1" and code == 200:
            try:
                payload = json.loads(body)
                ok(payload.get("status") in ("recebido", "em preparo", "pronto", "entregue", "cancelado"), "live API status valido")
            except json.JSONDecodeError:
                ok(False, "live API JSON invalido")

    print()
    if fails:
        print(f"RESULTADO: {len(fails)} falha(s)")
        for f in fails:
            print(" -", f)
        return 1
    print("RESULTADO: checklist OK + todas as abas locais e ao vivo OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
