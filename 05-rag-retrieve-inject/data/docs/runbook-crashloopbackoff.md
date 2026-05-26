# Runbook — Pod em CrashLoopBackOff

## Sintoma
Um pod do Kubernetes fica reiniciando indefinidamente. O `kubectl get pods` mostra o
status `CrashLoopBackOff` e a contagem de `RESTARTS` sobe sem parar. O Kubernetes
aumenta progressivamente o intervalo entre as tentativas de reinício (backoff
exponencial, até um teto de 5 minutos).

## Diagnóstico
1. Veja por que o container morreu na última execução:
   `kubectl describe pod <pod>` — observe `Last State`, `Reason` e `Exit Code`.
   - `Exit Code 0` com reinício costuma ser processo que termina cedo demais.
   - `Exit Code 1` / `2` geralmente é erro de aplicação no startup.
   - `Exit Code 137` é o container morto por falta de memória (ver runbook de OOMKilled).
2. Leia os logs do container que crashou (não o atual):
   `kubectl logs <pod> --previous`.
3. Causas comuns:
   - Erro de configuração: variável de ambiente faltando, secret não montado, URL de
     banco inválida — a aplicação sobe, tenta conectar, falha e encerra.
   - Falha no liveness probe: o probe aponta para a porta/rota errada e o kubelet mata
     o container achando que ele travou.
   - Migração de banco que falha no boot e derruba o processo.
   - Imagem com binário incompatível com a arquitetura do node.

## Mitigação
- Corrija a configuração ausente (env/secret/configmap) e reaplique o deployment.
- Se for liveness probe mal configurado, ajuste `initialDelaySeconds` e o `path`/`port`
  para dar tempo de a aplicação subir antes do primeiro check.
- Para depurar com calma, suba uma cópia do pod com o comando trocado por `sleep 3600`
  e entre via `kubectl exec` para inspecionar o ambiente.
- Faça rollback para a última imagem saudável se o crash começou após um deploy:
  `kubectl rollout undo deployment/<nome>`.
