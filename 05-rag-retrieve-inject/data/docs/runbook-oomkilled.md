# Runbook — Container morto por falta de memória (OOMKilled)

## Sintoma
Um container é encerrado abruptamente e reiniciado. O `kubectl describe pod <pod>`
mostra `Last State: Terminated`, `Reason: OOMKilled` e `Exit Code: 137`. A aplicação
"morre do nada" sob carga, sem stack trace, geralmente após um pico de tráfego ou ao
processar um payload grande.

## Diagnóstico
1. Confirme o OOMKill: `kubectl describe pod <pod>` e procure `OOMKilled` em `Last State`.
2. Compare o uso real com o limite definido:
   `kubectl top pod <pod>` e o `resources.limits.memory` no manifesto.
3. O OOM pode vir de dois lados:
   - **Limite do cgroup (Kubernetes)**: o processo passou do `limits.memory` e o kernel
     matou só aquele container. É o caso mais comum.
   - **Pressão de memória no node**: o node inteiro fica sem RAM e o kubelet começa a
     despejar pods. Cheque `kubectl describe node` por `MemoryPressure`.
4. Causas frequentes: vazamento de memória na aplicação, cache sem limite, carregar um
   arquivo/resultado de query inteiro em memória, ou heap da JVM maior que o limite do
   container (a JVM não enxerga o limite do cgroup sem configuração).

## Mitigação
- Ajuste `resources.requests` e `resources.limits` de memória com base no uso real
  observado, com folga para picos.
- Para JVM, configure `-XX:MaxRAMPercentage` para respeitar o limite do container.
- Investigue e corrija o vazamento (heap dump, profiling) — aumentar o limite só adia
  o problema se houver leak.
- Adicione paginação/streaming no processamento de grandes volumes em vez de carregar
  tudo em memória de uma vez.
