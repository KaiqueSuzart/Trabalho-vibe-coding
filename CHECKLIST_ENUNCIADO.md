# Checklist — enunciado Barraquinha Digital × Maré Clara

**App:** https://trabalho-vibe-coding-liard.vercel.app  
**Como validar:** `python test_checklist.py`

## Obrigatório

| # | Exigência | Status | Onde testar |
|---|-----------|--------|-------------|
| 1 | Cardápio ≥8 itens, ≥2 categorias, mobile | OK | `/cardapio` |
| 2 | Pedido com itens/qtd + localização (tenda) + validação + nº do pedido | OK | `/pedir` → cardápio → carrinho |
| 3 | `GET /api/pedido/:numero` (JSON + 404) | OK | `/api/pedido/1` e `/api/pedido/999999` |
| 4 | Painel da barraca (fila, update status, entregues/cancelados distintos) | OK | login `garcom`/`garcom` → `/barraca` |
| 5 | Tela de teste da API (nº → JSON + status HTTP) | OK | `/teste-api` |
| 6 | 3 pedidos demo (recebido / em preparo / entregue) | OK | seed → pedidos `#1` `#2` `#3` |
| 7 | Acompanhamento do cliente consome a API | OK | `/acompanhar` e tela de pedidos |

## Opcionais (nota extra)

| Item | Status |
|------|--------|
| Filtro por status | OK (`/barraca/?status=`) |
| Estimativa de espera | OK |
| Histórico separado | OK |
| Anti-duplicado &lt; 2 min | OK |
| Cancelamento pelo cliente | OK (5 min) |
| Contadores por status | OK |

## Entrega

| Item | Status |
|------|--------|
| Link público | https://trabalho-vibe-coding-liard.vercel.app |
| Histórico de prompts | `HISTORICO_PROMPTS.md` |

## Logins demo

- Lojista: `admin` / `admin`
- Garçom: `garcom` / `garcom`
- PIN cliente: `1234`
