# Post-mortem — Indisponibilidade do checkout após deploy

**Data do incidente:** 14/03/2026
**Duração:** 38 minutos (14:02 — 14:40)
**Severidade:** SEV-1
**Serviço afetado:** API de checkout (loja online)
**Autores:** time de Pagamentos
**Cultura:** blameless — o foco é o sistema, não a pessoa.

## Resumo
Um deploy de rotina da API de checkout introduziu uma migração de banco incompatível
com a versão anterior do código. Durante o rolling update, pods novos e antigos
conviveram apontando para um schema já alterado, e os pods antigos passaram a falhar.
O checkout ficou indisponível por 38 minutos.

## Impacto
- ~6.200 tentativas de checkout falharam.
- Carrinhos abandonados; perda de receita estimada no período.
- Aumento de chamados no suporte.

## Timeline (horário de Brasília)
- **14:00** — Início do deploy da versão `v2.8.0` via rolling update.
- **14:02** — Taxa de erro 5xx no checkout sobe de ~0% para ~70%.
- **14:05** — Alerta de "error rate alta no checkout" dispara; on-call acionado.
- **14:12** — On-call identifica que os pods na versão antiga estão em erro após a
  migração ter renomeado uma coluna que o código antigo ainda usava.
- **14:30** — Decisão de rollback. Como a migração não era retrocompatível, o rollback
  da imagem sozinho não resolveu — foi preciso reverter também a migração.
- **14:40** — Schema e código alinhados; taxa de erro volta ao normal.

## Causa raiz
A migração renomeou uma coluna em vez de adicionar a nova e manter a antiga. Durante o
rolling update, código antigo e novo coexistem por alguns minutos; o código antigo
quebrou ao não encontrar a coluna renomeada. A migração não era retrocompatível.

## Ações corretivas
- Adotar o padrão **expand/contract** para migrações: primeiro adicionar (expand), fazer
  o código usar o novo, e só depois remover o antigo (contract) num deploy seguinte.
- Bloquear no CI migrações que renomeiam/removem colunas sem etapa de transição.
- Criar runbook de rollback que cubra explicitamente migração + imagem juntas.
- Validar deploys em ambiente que reproduza a convivência de versões (canário).
