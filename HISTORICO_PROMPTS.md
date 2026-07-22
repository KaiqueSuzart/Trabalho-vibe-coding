# Histórico de prompts — Maré Clara (Barraquinha Digital)

| Campo | Valor |
|--------|--------|
| Disciplina | FIAP · Global MBA em IA Leadership & Vibe Coding |
| Projeto | Barraquinha Digital / Maré Clara |
| Ferramenta | Cursor (Vibe Coding) |
| App publicada | https://trabalho-vibe-coding-liard.vercel.app |
| Repositório | https://github.com/KaiqueSuzart/Trabalho-vibe-coding |
| Data | 22/07/2026 |

### Como este histórico foi construído (visão de engenharia de prompt)

Em vez de um único prompt genérico (“faz um app de praia”), o desenvolvimento foi **quebrado em camadas**:

1. **Problema e personas** (antes de UI)
2. **Escopo fechado + critérios de aceite**
3. **Implementação por fatias**
4. **Correção com bug report específico** (esperado × observado)
5. **Alinhamento à rubrica do enunciado**
6. **Deploy e persistência real**

Técnicas usadas de propósito: *role prompting*, *constraints*, *acceptance criteria*, *negative constraints* (“não faça X”), *error specificity*, *iteration loops* e *definition of done*.

> Credenciais sensíveis (chaves/senha Supabase) aparecem como `[REDACTED]` neste arquivo de entrega.

---

# FASE 0 — Briefing e escopo (antes de código)

## Prompt 01 — Problema, personas e restrições de contexto

```text
Atue como product engineer + tech lead de um protótipo acadêmico.

Contexto do problema:
Durante o verão, barracas de praia no litoral brasileiro sofrem com fila, pedido errado e garçom sobrecarregado. O cliente quase sempre está com o celular na mão, mas o atendimento ainda é 100% presencial.

Pergunta central:
Como criar um sistema digital simples o suficiente para uso na praia (sol, areia, conexão instável) e que ao mesmo tempo organize a operação da barraca?

Quero que você:
1) Pesquise referências reais de sistemas para quiosque/barraca/praia.
2) Proponha um escopo COMPLETO (não mockup) com dois lados obrigatórios:
   - Cliente: cardápio, pedido com localização (nº da tenda), acompanhamento de status
   - Barraca: painel de pedidos, atualização de status, fila organizada
3) Inclua papéis extras que fazem sentido operacionalmente (garçom, cozinha/bar, lojista), explicando o porquê.
4) Banco LOCAL na primeira versão (SQLite).
5) Entregue um plano por fases (MVP → completo), com decisões críticas a justificar:
   - identificação do cliente sem cadastro
   - pedidos simultâneos
   - persistência dos dados
   - UX mobile-first

Não comece a codar ainda. Quero primeiro o plano e as decisões de produto.
```

**Por que esse prompt:** ancora no problema (não na solução), define papéis, força pesquisa e separa planejamento de implementação — padrão de prompt engineering.

**Saída obtida:** plano Maré Clara (Flask + SQLite), personas, mapa de tendas, KDS, admin.

---

## Prompt 02 — Fechamento de stack e amplitude do escopo

```text
Decisões fechadas:
1) Stack: Python + Flask + SQLite + Jinja2 (simples de apresentar e de rodar local).
2) Amplitude: escopo COMPLETO (cliente + garçom + cozinha/bar + lojista), não só o MVP mínimo.

Confirme o plano final em formato executável (módulos, entidades, rotas principais e ordem de implementação).
Não implemente ainda.
```

**Por que esse prompt:** reduz ambiguidade com escolhas explícitas (evita a IA “inventar” stack no meio do caminho).

---

## Prompt 03 — Brief técnico com Definition of Done

```text
Implemente o plano anexado do app “Maré Clara” (barraca de praia).

Regras:
- Siga o plano; não reescreva o plano.
- Marque to-dos em progresso e complete todos.
- Não pare no meio.

Definition of Done (DoD):
[ ] Seed com tendas, categorias (>=2), produtos (>=8) e usuários demo
[ ] Cliente: mapa, reserva, pedir com nº da tenda + PIN do dia, cardápio, carrinho, pedidos, conta
[ ] Garçom: painel, check-in, entrega, conta
[ ] Cozinha/Bar: fila por status/setor
[ ] Lojista: CRUD básico, estoque, relatórios
[ ] App sobe com `python seed.py` + `python app.py`

Credenciais demo desejadas: admin/admin, garcom/garcom, PIN 1234.
```

**Por que esse prompt:** checklist de aceite transforma “faça o app” em contrato verificável.

---

# FASE 1 — Validação e UX

## Prompt 04 — Subir e validar

```text
Suba o servidor local e me diga a URL + como testar o happy path em 5 passos.
Se houver erro de boot, corrija antes de seguir.
```

---

## Prompt 05 — Refino visual com negative constraints

```text
O front está funcional, mas com “cara de IA genérica”.

Melhore a identidade visual com estas constraints:
- Tema praia/barraca (não dashboard SaaS roxo)
- Tipografia com personalidade (evitar Inter/Roboto default)
- Hierarquia clara: marca forte no primeiro viewport
- Mobile-first para o cliente; desktop confortável para equipe
- Evitar: cards excessivos, pills demais, glow, visual genérico de template

Não mude regras de negócio neste passo — só UI/UX.
```

**Técnica:** *negative prompting* + escopo estreito (só visual) para não quebrar o que já funciona.

---

## Prompt 06 — Completar o fluxo de valor (pedido na tenda)

```text
Além de reservar, o sistema PRECISA do fluxo operacional:
cliente escolhe itens do cardápio e pede para a tenda/mesa.

Entregáveis:
- Entrada por número da tenda
- Cardápio por categoria
- Carrinho + confirmação com número do pedido
- Pedido deve aparecer na operação (garçom/cozinha)

Critério de aceite: eu faço um pedido como cliente e vejo o mesmo pedido no painel da equipe.
```

---

## Prompt 07 — Cardápio rico + pagamento (escopo de produto)

```text
Melhore o cardápio pensando em uso real na praia:

1) Fotos nos produtos
2) Ao clicar: quantidade, observação, subtotal
3) Formas de pagamento:
   - pagar agora (online simulado)
   - pagar na entrega
   - deixar na conta da tenda
4) UX de botões grandes / toque fácil

Critério: fluxo completo até gerar pedido numerado e status inicial "recebido".
```

---

# FASE 2 — Regras de negócio e debugging

## Prompt 08 — Bug report específico (estado da tenda)

```text
Bug / inconsistência de estado:

Esperado: ao alocar/reservar uma tenda, o mapa deve refletir status (reservada/ocupada).
Observado: reservei/aloquei e a tenda continua aparecendo como LIVRE.

Perguntas:
1) O banco local SQLite está realmente persistindo?
2) Qual transição de status está faltando no fluxo?

Corrija a regra e me explique a máquina de estados da tenda
(livre → reservada → ocupada → livre / manutenção).
```

**Técnica:** esperado × observado (padrão ouro de prompt de correção).

---

## Prompt 09 — Erro de startup (com evidência)

```text
Ao abrir o app, aparece este erro no início:
[screenshot anexado]

Quero:
1) causa raiz
2) correção
3) como evitar que volte (migração/schema)
```

---

## Prompt 10 — Decisão de produto: PIN do dia

```text
Explique a decisão do “PIN do dia”:
- por que não exigir cadastro do cliente?
- qual o risco se dois clientes informarem a mesma tenda?
- como isso se compara a QR code / login?

Quero a justificativa como se fosse responder ao avaliador.
```

---

## Prompt 11 — Auditoria de regras de negócio

```text
Faça uma auditoria de regras. Exemplos:
- Pedir em tenda não reservada: aceita ou bloqueia?
- Tenda em manutenção?
- Pedido online não pago entra na cozinha?
- Estoque insuficiente?

Liste TODAS as regras atuais + ajuste o que estiver frouxo para operação real de sábado com pico.
Entregue uma tabela Situação → Comportamento.
```

---

# FASE 3 — UX mobile + qualidade

## Prompt 12 — Carrossel + responsividade dual

```text
No cardápio:
1) Adicione carrossel de produtos na home/browse.
2) A aplicação precisa ficar boa em CELULAR e DESKTOP (não só mobile).
   Cliente = mobile; equipe = tablet/desktop.

Aceite: testável em largura ~390px e ~1280px sem quebrar botões/nav.
```

---

## Prompt 13 — Assets faltando

```text
Alguns produtos ficaram sem foto.
Complete todas as imagens do seed/cardápio. Nenhum item principal pode ficar sem thumbnail.
```

---

## Prompt 14 — Bug na reserva (evidência)

```text
Fluxo: eu reservei uma tenda e recebi este erro:
[screenshot]

Corrija, adicione validação clara (mensagem em PT) e garanta que a reserva persista e apareça no admin.
```

---

## Prompt 15 — Regressão crítica + testes automatizados

```text
Falha grave:
Cliente finalizou pedido, mas NÃO apareceu no painel do garçom.

Tarefa:
1) Corrigir a causa (status/filtro/pagamento/sessão).
2) Criar/rodar testes ponta a ponta cobrindo:
   - cliente pede
   - garçom vê
   - cozinha atualiza
   - admin persiste produto/estoque
3) Só considere pronto quando os testes passarem.

Isso é bloqueante para a nota.
```

**Técnica:** eleva severidade + exige prova automática (não “acho que funcionou”).

---

## Prompt 16 — Conta operacional (baixa)

```text
Na conta da tenda preciso dar baixa do que:
- já foi pago
- ainda está em aberto
- já foi entregue / não entregue

Implemente baixa de pagamento e baixa de entrega por item/pedido, com totais claros.
```

---

## Prompt 17 — Documentação e publicação do código

```text
Crie um README completo (funcionalidades, como rodar, credenciais, fluxo de apresentação, regras).
Em seguida faça commit e push para:
https://github.com/KaiqueSuzart/Trabalho-vibe-coding.git
```

---

# FASE 4 — Persistência real e deploy

## Prompt 18 — Pergunta crítica de arquitetura

```text
Se eu publicar no Vercel, o SQLite vai funcionar?

Quero resposta honesta de engenharia:
- o que quebra no filesystem serverless
- alternativas (Postgres/Supabase)
- o que mudar no código (DATABASE_URL, pool, etc.)
```

---

## Prompt 19 — Melhoria contínua (backlog guiado)

```text
Audite o produto e implemente melhorias de UX/fluxo que aumentem chance de uso real num sábado lotado:
nav mobile, labels em PT, empty states, carrinho editável, confirmações, copy da home, etc.
Priorize impacto operacional, não cosmética vazia.
```

---

## Prompt 20 — Migração Supabase (escopo cloud)

```text
Criei projeto free no Supabase:
URL: https://olsznvaungwnxdsbjprl.supabase.co
ANON_KEY: [REDACTED]
SERVICE_ROLE: [REDACTED]

Quero:
1) schema/tabelas equivalentes ao app
2) seed com dados demo
3) Flask lendo DATABASE_URL (Postgres)
4) .env local NÃO commitado

Definition of Done: app local aponta para Supabase e login demo funciona.
```

---

## Prompt 21 — Credencial de banco

```text
Senha do database Supabase: [REDACTED]
Configure a connection string (URL-encode se necessário) e rode o seed.
```

---

## Prompt 22 — Variáveis no Vercel

```text
Estou na tela Environment Variables do Vercel.
Quais Keys/Values exatas preciso colocar para Production/Preview?
Liste só o essencial para o Flask subir com Postgres.
```

---

## Prompt 23 — Incident response (deploy 500)

```text
Deploy no ar, mas ao abrir a URL:
"This Serverless Function has crashed" / FUNCTION_INVOCATION_FAILED / 500.

Hipóteses a verificar:
- código no GitHub ainda em SQLite
- DATABASE_URL ausente/errada
- conexão Direct IPv6 vs pooler IPv4 no serverless

Corrija, faça push e me diga o que mudou na URL do banco (pooler).
```

**Técnica:** incident prompt com hipóteses — acelera diagnóstico sem “não funciona”.

---

# FASE 5 — Alinhamento à rubrica do professor

## Prompt 24 — Gap analysis do enunciado

```text
Li o documento oficial “Barraquinha de Praia Digital.docx”.

Faça um gap analysis honesto: o que JÁ temos vs o que a rubrica exige obrigatoriamente.

Checklist obrigatório do enunciado:
1) Cardápio (>=8 itens, >=2 categorias, mobile)
2) Fazer pedido (itens/qtd, localização, validação, nº do pedido)
3) API GET /api/pedido/:numero (JSON + 404)
4) Painel da barraca (fila, update status, entregues/cancelados distintos)
5) Tela de teste da API (input + JSON + status code)
6) 3 pedidos pré-carregados (em preparo, recebido, entregue)

Opcionais (nota extra): filtro, estimativa, histórico, anti-duplicado, cancelamento, contadores.

Entregue tabela: item → status (tem / parcial / falta).
Não implemente ainda — só diagnóstico.
```

**Por que esse prompt:** evita “achar que está completo”; força confronto com a rubrica.

---

## Prompt 25 — Fechar 100% da rubrica + teste

```text
Agora implemente TUDO que falta do enunciado + os opcionais, sem remover o que já existe (reservas, estoque, admin, etc.).

Incluir:
- GET /api/pedido/<numero> com status do enunciado (mapear preparando ↔ "em preparo")
- /teste-api
- /barraca com filtros/contadores/histórico
- seed com 3 pedidos demo
- acompanhamento do cliente consumindo a API
- opcionais: estimativa, anti-duplicado 2min, cancelamento 5min

Definition of Done:
- testes automatizados passando
- API 200 e 404 demonstráveis
- painel atualiza status ponta a ponta
```

---

## Prompt 26 — Qualidade de conteúdo (imagens)

```text
As fotos do cardápio estão trocadas (ex.: açaí mostrando outra coisa, água de coco errada, hot dog errado).

Substitua TODAS as imagens para bater com o nome do produto.
Faça cache-bust se necessário e publique.
Aceite: no carrossel, cada card visualmente corresponde ao item.
```

---

## Prompt 27 — Entregável de processo (histórico)

```text
Monte o histórico de prompts para a entrega da matéria, em ordem cronológica,
evidenciando raciocínio, correção de erros e evolução do escopo.
Inclua o link público + como o professor testa a API.
```

---

## Prompt 28 — Hardening final (QA + limpeza + docs)

```text
Faça uma bateria de testes de TODAS as abas e botões principais.
Remova arquivos desnecessários (ex.: .env.example).
Atualize o README para refletir o estado real (Vercel + Supabase + API).
Commit e push.

DoD: smoke + e2e verdes; repo limpo; README coerente com o deploy.
```

---

# Reflexão final (para o avaliador / engenharia de prompt)

### O que funcionou nos prompts
- Separar **planejar** de **implementar**
- Dar **critérios de aceite** objetivos
- Corrigir bugs com **esperado × observado**
- Usar **negative constraints** no design
- Fechar com **gap analysis da rubrica** (não assumir cobertura)

### O que eu mudaria numa próxima vez
- Desde o dia 1 pedir a API `/api/pedido/:numero` e a tela de teste (evitar retrabalho)
- Já começar com Postgres se o deploy alvo for Vercel
- Incluir checklist de acessibilidade/toque (44px) no prompt de UI

### Respostas prontas às perguntas do enunciado

| Pergunta | Resposta da solução |
|----------|---------------------|
| Dois clientes na mesma tenda? | PIN + sessão da tenda; risco de conflito existe — mitigado por operação do garçom e anti-duplicado curto |
| Recarregar apaga pedidos? | Não — persistidos em Postgres/Supabase |
| Novo pedido sem F5? | Painéis com refresh periódico + API |
| Por que 404? | Contrato HTTP claro para inexistente |
| Cardápio muda como? | Admin CRUD |
| 10 vs 100 pedidos? | Fila ordenada + filtros; escala via pooler/serverless |

---

## O que colar no formulário de entrega

1. **URL:** https://trabalho-vibe-coding-liard.vercel.app  
2. **Este histórico** (`HISTORICO_PROMPTS.md`)  
3. **Como testar rápido:**  
   - `/teste-api` → pedido `1` (200) e `999999` (404)  
   - login `garcom`/`garcom` → `/barraca`  
   - PIN cliente `1234`

---

*Documento de processo · Vibe Coding · foco em engenharia de prompt e entrega alinhada à rubrica*
