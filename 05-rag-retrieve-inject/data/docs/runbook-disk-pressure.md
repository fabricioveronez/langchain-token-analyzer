# Runbook — Disco cheio / DiskPressure no node

## Sintoma
Aplicações começam a falhar ao escrever arquivos, logs param de ser gravados, ou pods
são despejados (`Evicted`) com a mensagem `The node was low on resource: ephemeral-storage`.
O `kubectl describe node` mostra a condition `DiskPressure: True`. Em servidores fora do
Kubernetes, comandos falham com `No space left on device`.

## Diagnóstico
1. Cheque o uso do disco no node: `df -h`. Procure partições em 100% (`/`, `/var`).
2. Encontre os maiores consumidores:
   `du -sh /var/lib/docker/* 2>/dev/null | sort -h | tail` ou
   `du -sh /var/log/* | sort -h | tail`.
3. Suspeitos clássicos:
   - Logs de aplicação sem rotação crescendo até encher `/var/log`.
   - Imagens de container e camadas antigas acumuladas.
   - Arquivos temporários ou uploads que nunca são limpos.
   - `emptyDir` ou volume efêmero de um pod crescendo sem limite.
   - Tabela de banco/journal/WAL crescendo em disco compartilhado.

## Mitigação
- Imediato: libere espaço com segurança — comprima/rotacione logs, limpe `/tmp`,
  remova imagens não usadas (`docker image prune` / `crictl rmi --prune`).
- Configure rotação de logs (logrotate ou limites do runtime de container).
- Defina `resources.limits` de `ephemeral-storage` nos pods para evitar que um único pod
  encha o node.
- Monitore com alerta em ~80% de uso para agir antes do disco encher de fato.
- Mova dados que crescem (logs, métricas, backups) para storage dedicado/externo.
