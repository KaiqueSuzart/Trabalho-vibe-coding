# Histórico de prompts — Maré Clara (Barraquinha Digital)

**Disciplina:** FIAP · Global MBA em IA Leadership & Vibe Coding · Projeto Final  
**Aplicação:** Maré Clara — sistema de pedidos para barraca de praia  
**Ferramenta usada:** Cursor (assistente de código com IA)  
**Link público da aplicação:** https://trabalho-vibe-coding-liard.vercel.app  
**Repositório:** https://github.com/KaiqueSuzart/Trabalho-vibe-coding  

> Os prompts abaixo estão em **ordem cronológica**, como foram escritos durante o desenvolvimento.  
> Notas curtas após cada prompt mostram a intenção, o erro encontrado e o ajuste — evidência de iteração.  
> **Segurança:** chaves/senhas do Supabase foram **redigidas** neste documento de entrega (`[REDACTED]`). No chat original foram enviadas à IA para conectar o banco.

---

## Prompt 1 — 22/07/2026, 14:08

```
eu tenho que fazer um trabalho de desenvolvimento de aplicação de barraca de praia para faculdade, quero um banco local mesmo, e quero que vc pensa em tudo oq pode ter numero da tenda pagina pro cliente pedir visão do logista etc pansa em  tudo pega referencia na intenet para poder fazer um completo
```

**Resultado / raciocínio:** Partimos do problema (fila na praia, cliente com celular) e não de uma tela solta. A IA pesquisou referências de sistemas reais e propôs um plano completo (cliente, garçom, cozinha, lojista) com SQLite local.

---

## Prompt 2 — 22/07/2026, 14:09

```
1)a
2)b
```

**Resultado / raciocínio:** Escolhas do plano: stack **Python + Flask** e escopo **completo** (não só MVP mínimo).

---

## Prompt 3 — 22/07/2026, 14:10

```
App Barraca de Praia (Flask + SQLite)

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.
```

**Resultado / raciocínio:** Autorização para implementar o plano inteiro (modelos, rotas, templates, seed).

---

## Prompt 4 — 22/07/2026, 14:28

```
Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.
```

**Resultado / raciocínio:** Continuação da implementação após retomada da sessão / plano.

---

## Prompt 5 — 22/07/2026, 14:28

```
pode abrir o server
```

**Resultado / raciocínio:** Validação manual: subir `python app.py` e testar no navegador.

---

## Prompt 6 — 22/07/2026, 14:32

```
olha esse front end ta muito feito, melhore deixa mais bonito sem cara de IA
```

**Resultado / raciocínio:** Feedback de produto/UX. Identidade visual própria (praia, tipografia, cores), evitando visual genérico “IA”.

---

## Prompt 7 — 22/07/2026, 14:34

```
e alem de resevar deveria ter uma parte pra menu pedir as coisas na mesa etc
```

**Resultado / raciocínio:** Gap de fluxo: reserva sozinha não resolve a operação. Incluir pedido na tenda (cardápio + localização).

---

## Prompt 8 — 22/07/2026, 14:37

```
precisa melhorar esse cardapio, colocar fotos etc tudo pra melhorar e quando eu clico mostra a contidade etc e escolher pra pagar online ou quando o cara vim trazer ja pensa em tudo
```

**Resultado / raciocínio:** Cardápio com fotos, modal de quantidade e modos de pagamento (online / na entrega / na conta).

---

## Prompt 9 — 22/07/2026, 14:41

```
e o banco de dados ja esta funcionando esta local mesmo?, pq eu tinha alocado uma mesa e ela ainda esta aparecendo livre
```

**Resultado / raciocínio:** Bug de regra de negócio: status da tenda não refletia reserva/ocupação. Correção no fluxo de reserva/check-in.

---

## Prompt 10 — 22/07/2026, 14:42

```
ta dando esse erro no inicio
```

*(print/screenshot do erro anexado no chat)*

**Resultado / raciocínio:** Correção de erro de startup (schema/migração/ambiente).

---

## Prompt 11 — 22/07/2026, 14:44

```
oq seria esse pin do dia?
```

**Resultado / raciocínio:** Explicação da decisão de identificação sem cadastro: PIN do dia + número da tenda (em vez de login do cliente).

---

## Prompt 12 — 22/07/2026, 14:45

```
e uma duvida ele valida a tenta que tem gente? ex se eu pedir pra uma tenda que nao esta reservada ele aceita? isso pode ja veja todas as regras de negocio possivel
```

**Resultado / raciocínio:** Revisão das regras: manutenção bloqueia; check-in com PIN em tenda livre/reservada; sessão ocupada; etc.

---

## Prompt 13 — 22/07/2026, 14:46

```
nesse cardapior aqui seria bom um carrossel, alem disso esse aplicação tbm ta total focando pra celular tbm ne tem que ficar perfeito nos 2
```

**Resultado / raciocínio:** Carrossel no cardápio + responsividade mobile e desktop (cliente na praia + equipe no balcão).

---

## Prompt 14 — 22/07/2026, 14:48

```
alguns ficou sem foto
```

**Resultado / raciocínio:** Completar imagens faltantes dos produtos.

---

## Prompt 15 — 22/07/2026, 14:51

```
eu reservei mas esta dando esse erro
```

*(print do erro anexado)*

**Resultado / raciocínio:** Correção do fluxo de reserva (validação/persistência/flash).

---

## Prompt 16 — 22/07/2026, 14:54

```
eu pedi e nao apareceu aqui pro garçom faça todos os test, para verificar se tudo ta funcionando perfeito ate no admin pra ver se esta salvando
```

**Resultado / raciocínio:** Bug crítico cliente→painel. Criamos/rodamos testes ponta a ponta (`test_e2e.py`) cobrindo cliente, garçom, cozinha e admin.

---

## Prompt 17 — 22/07/2026, 14:57

```
e aqui nao tem como dar baixa oq ja foi pago oq nao foi oq ja foi entregue etc
```

**Resultado / raciocínio:** Conta detalhada com baixa de pagamento e de entrega por item/pedido.

---

## Prompt 18 — 22/07/2026, 15:00

```
cria um readme completo pra esse trabalho bonito explicando as funcionadade etc e ja sobe pro git https://github.com/KaiqueSuzart/Trabalho-vibe-coding.git
```

**Resultado / raciocínio:** README + push para o GitHub (base do deploy).

---

## Prompt 19 — 22/07/2026, 15:04

```
se eu subir no vercel o bando de dados vai funcionar?
```

**Resultado / raciocínio:** Diagnóstico: SQLite no Vercel não serve (filesystem read-only). Caminho: Postgres (Supabase).

---

## Prompt 20 — 22/07/2026, 15:08

```
veja oq da pra melhorar nesse site tudas as melhorias pode trazer
```

**Resultado / raciocínio:** Rodada de UX (labels PT, nav mobile, carrinho editável, empty states, check-in, etc.).

---

## Prompt 21 — 22/07/2026, 15:23

```
criei uma conta free no supabase
anon public
[REDACTED — chave anon]

service_role
secret
[REDACTED — chave service_role]

https://olsznvaungwnxdsbjprl.supabase.co 

cria pra mim tudo dentro desse supabase
```

**Resultado / raciocínio:** Migração para Postgres: schema, `DATABASE_URL`, seed no Supabase.

---

## Prompt 22 — 22/07/2026, 15:26

```
[REDACTED] essa e a senha do supabase
```

**Resultado / raciocínio:** Conexão autenticada e população das tabelas.

---

## Prompt 23 — 22/07/2026, 15:26

```
[REDACTED] essa e a senha do supabase
```

*(reenvio da senha)*

---

## Prompt 24 — 22/07/2026, 15:28

```
pra eu subir pro vercel oq ja tenho que colocar aqui?
```

*(print da tela Environment Variables do Vercel)*

**Resultado / raciocínio:** Orientação das variáveis: `SECRET_KEY`, `DAY_PIN`, `DATABASE_URL`.

---

## Prompt 25 — 22/07/2026, 15:30

```
deu esse erro
```

*(print: FUNCTION_INVOCATION_FAILED / 500 no Vercel)*

**Resultado / raciocínio:** Causa: GitHub ainda em SQLite + conexão Direct IPv6. Correção: código com `DATABASE_URL`, pooler IPv4, push e redeploy.

---

## Prompt 26 — 22/07/2026, 15:32

```
@.../Barraquinha de Praia Digital.docx achei oq o professor pediu, verifica se ja tem tudo oq ele solicitou
```

**Resultado / raciocínio:** Cruzamento com o enunciado. App já era maior que o pedido, mas faltavam peças obrigatórias da rubrica: `GET /api/pedido/:numero`, tela de teste da API, painel “da barraca” no formato pedido e 3 pedidos demo.

---

## Prompt 27 — 22/07/2026, 15:37

```
perfeito eu quero que vc faça tudo oq tem e oq professor pede faz tudo e ja testa
```

**Resultado / raciocínio:** Implementação do obrigatório + opcionais (filtro, contadores, histórico, estimativa, anti-duplicado, cancelamento) e testes e2e — todos passaram.

---

## Prompt 28 — 22/07/2026, 15:45

```
olhas as fotos ta tudo errado poucas estão certa arruma isso pode pegar as fotos certo na intenert
```

*(prints do cardápio com imagens trocadas: açaí, água de coco, hot dog, camarão, etc.)*

**Resultado / raciocínio:** Troca de todas as fotos do cardápio para bater com o nome do produto + cache-bust e push.

---

## Prompt 29 — 22/07/2026 (entrega)

```
pode fazer 
Ainda falta na entrega da matéria
Montar o histórico de prompts (documento com a sequência do Cursor) e colar no formulário junto com o link.
```

**Resultado / raciocínio:** Este documento.

---

## Decisões que o avaliador pode perguntar (resumo)

| Pergunta | Decisão tomada |
|----------|----------------|
| Como identificar o cliente sem cadastro? | Número da tenda + **PIN do dia** |
| Pedidos somem ao recarregar? | Não — persistidos em **Postgres/Supabase** (antes SQLite local) |
| Como a barraca vê pedidos novos? | Painel `/barraca` + cozinha/garçom com atualização periódica |
| Por que a API retorna 404? | Contrato claro: pedido inexistente ≠ objeto vazio |
| Cardápio muda como? | Admin CRUD de produtos/categorias |
| Escala | Pooler no Vercel; NullPool; fila por status |

---

## Entrega — o que colar no formulário

1. **URL da aplicação:** https://trabalho-vibe-coding-liard.vercel.app  
2. **Este histórico** (arquivo `HISTORICO_PROMPTS.md` / `.txt`)  
3. **Logins demo:** `admin`/`admin`, `garcom`/`garcom`, PIN cliente `1234`  
4. **Teste da API:** `/teste-api` — pedidos demo `#1` recebido, `#2` em preparo, `#3` entregue; inexistente `999999` → 404  

---

*Gerado a partir do histórico real de conversa no Cursor · 22/07/2026*
