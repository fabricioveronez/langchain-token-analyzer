# Runbook — Exhaustão de pool de conexões com o banco

## Sintoma
A aplicação começa a lançar erros como `timeout acquiring connection from pool`,
`connection pool exhausted` ou `too many clients already`. As requisições ficam lentas
e depois falham em massa. O banco (PostgreSQL/MySQL) aparece saudável em CPU e memória,
mas recusa novas conexões.

## Diagnóstico
1. Veja quantas conexões estão abertas no banco:
   - PostgreSQL: `SELECT count(*), state FROM pg_stat_activity GROUP BY state;`
     Muitas em `idle in transaction` indicam transações que não foram fechadas.
   - Compare com `max_connections` do servidor.
2. Some os pools de todas as réplicas da aplicação. Exemplo clássico: pool de 20 por
   réplica × 30 réplicas = 600 conexões, mas o banco só aceita 100 — o limite estoura.
3. Causas comuns:
   - Conexões vazadas: código que pega conexão do pool e não devolve (falta de
     `close()`/`finally`, ou exceção no meio da transação).
   - Pool subdimensionado para a concorrência real.
   - Queries lentas segurando conexões por muito tempo.
   - Escalou réplicas horizontalmente sem rever o teto do banco.

## Mitigação
- Curto prazo: reinicie as réplicas para liberar conexões presas e dê fôlego ao banco.
- Corrija o vazamento garantindo que toda conexão volte ao pool (use context manager /
  `try-finally`).
- Coloque um pooler externo (PgBouncer em modo transaction) entre app e banco para
  multiplexar conexões.
- Dimensione o pool considerando réplicas × pool por réplica ≤ `max_connections`.
- Adicione timeout de transação para queries que travam.
