# Regras de negócio — tendas e pedidos (Maré Clara)

## Status da tenda (mapa)

| Status | Cor | Significado | Quem abre sessão com PIN |
|--------|-----|-------------|---------------------------|
| `livre` | Verde | Disponível | Qualquer cliente com PIN |
| `reservada` | Amarelo | Reserva do dia | Cliente com PIN (demo) |
| `ocupada` | Vermelho | Sessão aberta | Bloqueado — só garçom |
| `manutencao` | Cinza | Fora de uso | Bloqueado |

## Por que 2, 3 e 7 aparecem ocupadas

- **3** e **7**: pedidos demo do seed (avaliação).
- **2** (ou outras): sessões abertas em testes/uso.
- A lista em **/pedir** e o **mapa** leem o mesmo campo `tent.status`.

## Fluxo de abertura (PIN)

1. PIN do dia correto (demo `1234`)
2. Se já existe sessão aberta → reutiliza
3. Se manutenção → erro
4. Se ocupada → erro (“peça ajuda ao garçom”)
5. Se livre/reservada → cria sessão, marca ocupada, aluguel na conta

## Pedidos

- Online só entra na cozinha depois de pago
- Anti-duplicado: mesma tenda em menos de 2 min
- Cancelamento cliente: até 5 min se ainda não preparou
- Fechar conta (garçom) → tenda volta a livre

## Bug corrigido (mapa sem cor)

Classes CSS usavam `status-{{ status|label }}` e geravam `status-Ocupada` (o CSS espera `status-ocupada`). Agora a classe usa o status cru; o `|label` fica só no texto.
