# Maré Clara

Sistema de pedidos digitais para **barraca de praia** (trabalho acadêmico · vibe coding).

**Link:** https://trabalho-vibe-coding-liard.vercel.app  
**Repo:** https://github.com/KaiqueSuzart/Trabalho-vibe-coding

---

## O que faz

Cliente pede pelo celular (tenda + PIN), barraca/cozinha/garçom gerenciam a fila e o lojista cuida de cardápio, estoque e relatórios.

```text
Cliente → Pedido + pagamento
   ↓
Barraca / Cozinha → Prepara
   ↓
Garçom → Entrega + conta
   ↓
Lojista → Gestão
```

---

## Funcionalidades

### Cliente
- Mapa de tendas, reserva, cardápio com fotos
- Pedir com nº da tenda + PIN do dia
- Carrinho (pagar online / na entrega / na conta)
- Acompanhar pedidos (`/acompanhar`) e conta da tenda
- Estimativa de espera, cancelar em até 5 min, anti-duplicado (&lt; 2 min)

### Enunciado da matéria
- API `GET /api/pedido/<numero>` (200 ou 404)
- Tela de teste da API: `/teste-api`
- Painel da barraca: `/barraca` (filtros, contadores, histórico)
- 3 pedidos demo no seed (recebido / em preparo / entregue)

### Equipe
- **Garçom:** check-in, entrega, pedido manual, conta/baixa, mapa
- **Cozinha/Bar:** fila por setor (recebido → preparando → pronto)
- **Lojista:** dashboard, produtos, categorias, tendas, estoque, usuários, reservas, relatórios

---

## Stack

| | |
|--|--|
| Backend | Python 3 + Flask |
| Banco | SQLite (local) ou **Postgres/Supabase** (`DATABASE_URL`) |
| Front | Jinja2 + CSS/JS responsivo |
| Deploy | Vercel + Supabase |

---

## Como rodar (local)

```bash
git clone https://github.com/KaiqueSuzart/Trabalho-vibe-coding.git
cd Trabalho-vibe-coding
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python seed.py
python app.py
```

Abra: http://127.0.0.1:5000

### Credenciais demo

| Papel | Login |
|-------|--------|
| Lojista | `admin` / `admin` |
| Garçom | `garcom` / `garcom` |
| Cliente | PIN do dia: `1234` |

Para usar Supabase: defina `DATABASE_URL` no `.env` (não versionado) e rode `python setup_supabase.py` ou `python seed.py`.

---

## Rotas úteis

| URL | Função |
|-----|--------|
| `/` | Home |
| `/pedir` | Abrir tenda (PIN) |
| `/cardapio` | Cardápio |
| `/reservar` | Reserva |
| `/acompanhar` | Status via API |
| `/teste-api` | Teste JSON 200/404 |
| `/barraca/` | Painel da barraca (login) |
| `/garcom/` | Garçom |
| `/cozinha/` | Cozinha/Bar |
| `/admin/` | Lojista |
| `/api/pedido/<n>` | API do enunciado |

---

## Testes

```bash
python test_smoke.py   # abas + botões
python test_e2e.py     # fluxo completo
```

---

## Deploy (Vercel)

Variáveis de ambiente (**Production e Preview**):

| Key | Value |
|-----|--------|
| `SECRET_KEY` | qualquer string secreta |
| `DAY_PIN` | `1234` |
| `DATABASE_URL` | pooler abaixo (obrigatório) |

**DATABASE_URL (copie exatamente):**

```text
postgresql://postgres.olsznvaungwnxdsbjprl:Al101299130874%2A@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

Importante:
- Host do **pooler** com porta **5432** (session) — não use `db.xxx.supabase.co`
- O `*` da senha vira `%2A`
- Inclua `?sslmode=require`
- Salve → **Redeploy** (sem cache, se possível)

Diagnóstico: https://trabalho-vibe-coding-liard.vercel.app/health  
Se `db_ping` for `false`, olhe `db_error` e `db_host` no JSON.

---

## Estrutura

```text
app.py, config.py, models.py, helpers.py, migrate.py, seed.py
routes/     public, auth, waiter, kitchen, barraca, admin, api
templates/  cliente, equipe, admin
static/     css, js, fotos do cardápio
vercel.json
HISTORICO_PROMPTS.md   # entrega da matéria
```

---

## Observações

- PIX/cartão são **simulados** (sem gateway real)
- `python seed.py` **recria** o banco (apaga dados)
- Interface: mobile (cliente) e desktop (equipe)

## Autoria

Trabalho acadêmico · vibe coding · FIAP
