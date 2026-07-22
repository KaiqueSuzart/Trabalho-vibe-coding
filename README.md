# Maré Clara

Sistema web acadêmico para **barraca de praia**: reserva de tendas, cardápio com fotos, pedidos pelo celular, painéis de garçom/cozinha e gestão do lojista — tudo com **banco local SQLite**.

> Trabalho de desenvolvimento de aplicação · vibe coding  
> Repositório: [KaiqueSuzart/Trabalho-vibe-coding](https://github.com/KaiqueSuzart/Trabalho-vibe-coding)

---

## Visão geral

Na areia, o cliente não precisa ficar acenando para o garçom. Ele informa o **número da tenda**, usa o **PIN do dia**, monta o pedido no celular e acompanha o status. A cozinha/bar prepara, o garçom entrega na tenda e o lojista acompanha vendas, estoque e ocupação.

```text
Cliente (celular)  →  Pedido + pagamento
        ↓
Cozinha / Bar      →  Prepara itens
        ↓
Garçom             →  Entrega + baixa na conta
        ↓
Lojista            →  Cardápio, estoque, relatórios
```

---

## Funcionalidades

### Cliente
- Mapa visual das tendas por zona (**Frente Mar**, **Meio**, **Fundo**)
- **Reservar** tenda (data, período, nome, telefone)
- **Pedir agora** com número da tenda + PIN do dia
- Cardápio com **fotos**, categorias e carrossel na home
- Clique no item → quantidade, observação e subtotal
- Carrinho com 3 formas de pagamento:
  - **Pagar agora (online)** — PIX/cartão simulado
  - **Pagar na entrega** — garçom cobra ao trazer
  - **Deixar na conta** — fecha tudo no final
- Acompanhar pedidos e status da conta (pago / em aberto / entregue)
- **Acompanhar** pedido via API (`/acompanhar`) e **Teste API** (`/teste-api`)
- Estimativa de espera, cancelamento em até 5 min e bloqueio de pedido duplicado (&lt; 2 min)

### Painel da Barraca (`/barraca`)
- Pedidos ativos do mais antigo ao mais recente
- Contadores e filtro por status
- Atualização de status (recebido → em preparo → pronto → entregue / cancelado)
- Histórico de entregues/cancelados visualmente distinto

### Garçom
- Check-in manual de tendas
- Pedidos em andamento + prontos para entregar
- Pedido manual (cliente sem celular)
- Entrega com cobrança na entrega
- Conta da tenda com **baixa de pagamento** e **baixa de entrega** por item/pedido
- Fechar conta e liberar a tenda no mapa

### Cozinha / Bar (KDS)
- Fila separada por setor (bar × cozinha)
- Status: recebido → preparando → pronto
- Pedidos online só entram na fila **depois** do pagamento confirmado

### Lojista (admin)
- Dashboard do dia (faturamento, ticket médio, ocupação, top produtos)
- CRUD de produtos, categorias e tendas
- Controle de estoque + alertas de estoque baixo
- Usuários (lojista / garçom)
- Reservas, mapa e relatórios

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3 + Flask |
| Banco | SQLite local ou **Postgres/Supabase** (`DATABASE_URL`) |
| ORM | Flask-SQLAlchemy |
| Front | Jinja2 + HTML/CSS/JS (responsivo) |
| Auth | Sessão Flask (equipe) · PIN do dia (cliente) |
| API | `GET /api/pedido/<numero>` → 200 JSON ou 404 |
| Deploy | Vercel + Supabase |

---

## Como rodar

### Requisitos
- Python **3.10+**

### Instalação

```bash
git clone https://github.com/KaiqueSuzart/Trabalho-vibe-coding.git
cd Trabalho-vibe-coding

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
python seed.py
python app.py
```

Abra no navegador: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Credenciais demo

| Papel | Usuário | Senha |
|-------|---------|-------|
| Lojista | `admin` | `admin` |
| Garçom | `garcom` | `garcom` |

**PIN do dia (cliente):** `1234`

---

## Fluxo para apresentar (roteiro)

1. **Reservar** uma tenda (ou ir direto em Pedir)
2. Em **Pedir**, informe o nº da tenda + PIN `1234`  
   → a sessão abre e a tenda fica **ocupada** no mapa
3. Escolha itens no cardápio → carrinho → forma de pagamento
4. Login **garçom** → veja **Pedidos em andamento**
5. Abra **Cozinha/Bar** → Preparar → Pronto
6. Volte ao garçom → **Entregar** (e cobrar, se for “na entrega”)
7. Em **Conta**, dê baixa no que foi pago/entregue e feche a tenda
8. Login **admin** → dashboard, estoque e relatórios

---

## Regras de negócio (resumo)

| Situação | O que acontece |
|----------|----------------|
| Tenda livre/reservada + PIN correto | Abre sessão e libera o cardápio |
| Tenda em manutenção | Bloqueada |
| Pedido online sem pagar | Não entra na cozinha até confirmar pagamento |
| Estoque insuficiente | Pedido bloqueado |
| Fechamento da conta | Tenda volta a **livre** no mapa |
| `python seed.py` | **Apaga e recria** o banco com dados demo |

---

## Estrutura do projeto

```text
Trabalho-vibe-coding/
├── app.py              # App Flask + migração de schema
├── config.py           # Configurações (SQLite, PIN do dia)
├── models.py           # Modelos (tendas, pedidos, estoque...)
├── helpers.py          # Auth por papel, totais da conta
├── migrate.py          # Garante colunas novas no SQLite
├── seed.py             # Dados de demonstração
├── test_e2e.py         # Teste ponta a ponta
├── requirements.txt
├── routes/
│   ├── public.py       # Cliente, reserva, cardápio, pagamento
│   ├── auth.py         # Login / logout
│   ├── waiter.py       # Painel do garçom
│   ├── kitchen.py      # Cozinha / bar
│   ├── admin.py        # Lojista
│   └── api.py          # Endpoints JSON (polling)
├── templates/          # Telas Jinja2
└── static/
    ├── css/style.css
    ├── js/app.js       # Carrossel + UX
    └── img/products/   # Fotos do cardápio
```

---

## Testes

```bash
python test_e2e.py
```

O script valida o fluxo completo: abrir tenda, pedir, cozinha, entrega, pagamento online, admin (produto/estoque) e fechamento da conta.

---

## Observações acadêmicas

- Banco **100% local** — não precisa de MySQL/PostgreSQL na nuvem
- PIX/cartão são **simulação** (registro local, sem gateway real)
- Interface pensada para **celular (cliente)** e **desktop/tablet (equipe)**
- Atualização dos painéis por **polling** (reload automático)

---

## Autoria

Projeto desenvolvido como trabalho acadêmico de vibe coding.  
Repositório GitHub: https://github.com/KaiqueSuzart/Trabalho-vibe-coding
