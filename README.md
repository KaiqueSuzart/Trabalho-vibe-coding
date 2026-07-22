# Maré Clara

**Sistema digital de pedidos para barraca de praia**  
Projeto final · FIAP · Global MBA em IA Leadership & **Vibe Coding**

> Na areia, o cliente pede pelo celular. A barraca organiza a fila. Sem acenar pro garçom.

---

### Links da entrega

| | |
|--|--|
| **App publicada** | [trabalho-vibe-coding-liard.vercel.app](https://trabalho-vibe-coding-liard.vercel.app) |
| **Repositório** | [github.com/KaiqueSuzart/Trabalho-vibe-coding](https://github.com/KaiqueSuzart/Trabalho-vibe-coding) |
| **Histórico de prompts** | [`HISTORICO_PROMPTS.md`](./HISTORICO_PROMPTS.md) |
| **Checklist do enunciado** | [`CHECKLIST_ENUNCIADO.md`](./CHECKLIST_ENUNCIADO.md) |
| **Regras de negócio** | [`REGRAS_NEGOCIO.md`](./REGRAS_NEGOCIO.md) |
| **Diagnóstico** | [/health](https://trabalho-vibe-coding-liard.vercel.app/health) |

---

## O problema

Em dias de pico, barracas de praia sofrem com fila, pedido errado e garçom sobrecarregado. Quase todo cliente está com o celular na mão — o sistema conecta **quem pede** com **quem prepara e entrega**.

```text
  CLIENTE (celular)          BARRACA (operação)
  ───────────────            ─────────────────
  Cardápio + tenda     →     Painel de pedidos
  Acompanhar status    ←     Cozinha / Garçom
```

---

## Tecnologias

| Camada | Tecnologia | Uso neste projeto |
|--------|------------|-------------------|
| Linguagem | **Python 3.12** | Backend e scripts |
| Framework | **Flask 3** | Rotas, sessão, blueprints |
| Templates | **Jinja2** | Telas HTML server-side |
| ORM | **Flask-SQLAlchemy** | Modelos e queries |
| Banco (produção) | **PostgreSQL via Supabase** | Persistência na nuvem |
| Driver | **psycopg2-binary** | Conexão Postgres |
| Config | **python-dotenv** | Variáveis locais (`.env`) |
| Front | **HTML / CSS / JS** | UI responsiva (mobile + desktop) |
| Fontes | **Bebas Neue + Source Sans 3** | Identidade visual |
| Deploy | **Vercel** (Python / serverless) | App pública |
| Banco cloud | **Supabase** (Postgres + pooler IPv4) | Dados em produção |
| Testes | `test_checklist.py`, `test_e2e.py`, `test_smoke.py` | Rubrica + fluxos |

### Por que Supabase?

O Vercel tem filesystem **read-only** — SQLite local **não funciona** em produção. O app usa **Postgres gerenciado no Supabase**, com connection **pooler** (IPv4) para serverless.

- Local: SQLite (`barraca.db`) **ou** o mesmo Supabase via `DATABASE_URL`
- Produção: sempre **Supabase Postgres**

---

## O que o professor pediu × o que tem

### Obrigatório (rubrica)

| # | Exigência | Status | Onde testar |
|---|-----------|--------|-------------|
| 1 | Cardápio ≥ **8 itens**, ≥ **2 categorias**, uso no celular | Feito | [/cardapio](https://trabalho-vibe-coding-liard.vercel.app/cardapio) |
| 2 | Pedido com itens/qtd, **localização (nº da tenda)**, validação, confirmação com **nº do pedido** | Feito | [/pedir](https://trabalho-vibe-coding-liard.vercel.app/pedir) |
| 3 | API `GET /api/pedido/:numero` → JSON com nº, itens, localização, status, horário | Feito | [/api/pedido/1](https://trabalho-vibe-coding-liard.vercel.app/api/pedido/1) |
| 4 | Status: recebido · em preparo · pronto · entregue · cancelado | Feito | API mapeia `preparando` → `em preparo` |
| 5 | Pedido inexistente → **404** com mensagem clara | Feito | [/api/pedido/999999](https://trabalho-vibe-coding-liard.vercel.app/api/pedido/999999) |
| 6 | Tela do cliente **consome a API** | Feito | [/acompanhar](https://trabalho-vibe-coding-liard.vercel.app/acompanhar) |
| 7 | **Painel da barraca**: fila, update de status, entregues/cancelados distintos | Feito | [/barraca](https://trabalho-vibe-coding-liard.vercel.app/barraca/) |
| 8 | **Tela de teste da API** (número → JSON + status HTTP) | Feito | [/teste-api](https://trabalho-vibe-coding-liard.vercel.app/teste-api) |
| 9 | **3 pedidos demo** pré-carregados | Feito | `#1` recebido · `#2` em preparo · `#3` entregue |

### Opcionais (nota extra) — todos feitos

| Extra | Status |
|-------|--------|
| Filtro por status no painel | Feito |
| Estimativa de tempo de espera | Feito |
| Histórico separado dos ativos | Feito |
| Anti-pedido duplicado (&lt; 2 min) | Feito |
| Cancelamento pelo cliente (prazo 5 min) | Feito |
| Contadores por status no topo do painel | Feito |

### Além do enunciado (operação real de barraca)

- Mapa de tendas por zona (Frente Mar / Meio / Fundo)
- Reserva de tenda
- PIN do dia (cliente sem cadastro)
- Pagamento: online (simulado) · na entrega · na conta
- Painéis de **garçom**, **cozinha/bar** e **lojista**
- Estoque, usuários, relatórios, dashboard

---

## Como o professor pode testar em 2 minutos

1. Abra a [tela de teste da API](https://trabalho-vibe-coding-liard.vercel.app/teste-api)  
   - `1` → **200** (recebido)  
   - `2` → **200** (em preparo)  
   - `3` → **200** (entregue)  
   - `999999` → **404**
2. Login equipe: **`garcom` / `garcom`** → [/barraca](https://trabalho-vibe-coding-liard.vercel.app/barraca/) (atualize status)
3. Cliente: [/pedir](https://trabalho-vibe-coding-liard.vercel.app/pedir) com tenda **livre** + PIN **`1234`**

### Credenciais demo

| Papel | Acesso |
|-------|--------|
| Lojista | `admin` / `admin` |
| Garçom / Cozinha / Barraca | `garcom` / `garcom` |
| Cliente | PIN do dia: **`1234`** |

---

## Arquitetura (visão rápida)

```text
┌─────────────┐     HTTPS      ┌──────────────────┐
│  Navegador  │ ─────────────► │  Vercel (Flask)  │
│  mobile/PC  │                │  app.py + Jinja  │
└─────────────┘                └────────┬─────────┘
                                        │ DATABASE_URL
                                        │ (pooler IPv4)
                               ┌────────▼─────────┐
                               │  Supabase        │
                               │  PostgreSQL      │
                               └──────────────────┘
```

Blueprints: `public` · `auth` · `barraca` · `waiter` · `kitchen` · `admin` · `api`

---

## Como rodar localmente

```bash
git clone https://github.com/KaiqueSuzart/Trabalho-vibe-coding.git
cd Trabalho-vibe-coding

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python seed.py
python app.py
```

Abra: **http://127.0.0.1:5000**

### Usar o mesmo banco Supabase no PC

Crie um arquivo `.env` (não vai pro Git):

```env
SECRET_KEY=barraca-praia-faculdade-2026
DAY_PIN=1234
DATABASE_URL=postgresql://postgres.SEU_REF:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

Depois: `python seed.py` (recria os dados demo) ou `python setup_supabase.py`.

> **Atenção:** `seed.py` **apaga e recria** as tabelas.

---

## Deploy (Vercel + Supabase)

Variáveis no painel da Vercel (Production **e** Preview):

| Key | Exemplo |
|-----|---------|
| `SECRET_KEY` | string secreta qualquer |
| `DAY_PIN` | `1234` |
| `DATABASE_URL` | URI do **pooler** Supabase + `?sslmode=require` |

Regras importantes:

- Use o host **`*.pooler.supabase.com`** (IPv4) — **não** `db.*.supabase.co` (só IPv6; quebra no Vercel)
- Caracteres especiais na senha precisam de **URL-encode** (ex.: `*` → `%2A`)
- Após salvar variáveis → **Redeploy**
- Saúde: [/health](https://trabalho-vibe-coding-liard.vercel.app/health) deve retornar `"ok": true`

---

## Rotas principais

| URL | Função |
|-----|--------|
| `/` | Home + mapa de tendas + cardápio |
| `/pedir` | Abrir sessão (tenda + PIN) |
| `/cardapio` | Cardápio (só visualização) |
| `/reservar` | Reserva de tenda |
| `/acompanhar` | Status do pedido via API |
| `/teste-api` | Teste oficial da API (enunciado) |
| `/barraca/` | Painel da barraca |
| `/garcom/` | Painel do garçom |
| `/cozinha/` | KDS cozinha / bar |
| `/admin/` | Lojista |
| `/api/pedido/<n>` | API do enunciado |
| `/health` | Diagnóstico de deploy |

---

## Testes automatizados

```bash
python test_checklist.py   # rubrica + abas local e Vercel
python test_smoke.py       # abas e botões
python test_e2e.py         # fluxo completo ponta a ponta
```

---

## Estrutura do repositório

```text
Trabalho-vibe-coding/
├── app.py                 # Flask app + /health
├── config.py              # SQLite / Supabase (DATABASE_URL)
├── models.py              # Tendas, pedidos, estoque, usuários…
├── helpers.py             # Auth, API status, regras
├── seed.py                # Dados demo (+ 3 pedidos do enunciado)
├── setup_supabase.py      # Seed no Postgres
├── routes/                # public, auth, barraca, waiter, kitchen, admin, api
├── templates/             # Telas Jinja2
├── static/                # CSS, JS, fotos do cardápio
├── vercel.json            # Deploy Python
├── HISTORICO_PROMPTS.md   # Entrega (engenharia de prompt)
├── CHECKLIST_ENUNCIADO.md
└── REGRAS_NEGOCIO.md
```

---

## Decisões de produto (perguntas do enunciado)

| Pergunta | Decisão |
|----------|---------|
| Como identificar o cliente sem cadastro? | **Nº da tenda + PIN do dia** |
| Pedidos somem ao recarregar? | **Não** — persistidos no **Supabase Postgres** |
| Como a barraca vê pedido novo? | Painel `/barraca` com atualização periódica + API |
| Por que a API retorna 404? | Contrato HTTP claro: inexistente ≠ objeto vazio |
| Cardápio muda como? | CRUD no painel do lojista (`/admin`) |

---

## Observações acadêmicas

- PIX / cartão são **simulados** (sem gateway real)
- Interface pensada para **celular (cliente)** e **desktop (equipe)**
- Projeto desenvolvido com **Vibe Coding** (Cursor) — o processo está em `HISTORICO_PROMPTS.md`

---

## Autoria

Trabalho acadêmico · **Maré Clara** · Barraca de praia digital  
FIAP · MBA IA Leadership & Vibe Coding
