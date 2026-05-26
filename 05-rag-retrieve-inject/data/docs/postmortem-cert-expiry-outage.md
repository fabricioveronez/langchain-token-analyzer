# Post-mortem — Outage da API pública por certificado expirado

**Data do incidente:** 02/02/2026
**Duração:** 1h12 (03:14 — 04:26)
**Severidade:** SEV-1
**Serviço afetado:** API pública (gateway)
**Autores:** time de Plataforma
**Cultura:** blameless — o foco é o sistema, não a pessoa.

## Resumo
O certificado TLS do gateway da API pública expirou de madrugada. Todos os clientes
externos passaram a receber erro de certificado e não conseguiam mais consumir a API.
Não houve nenhum deploy ou mudança — o gatilho foi a data de expiração do certificado.

## Impacto
- API pública totalmente indisponível para clientes externos por 1h12.
- Integrações de parceiros falharam em massa durante a madrugada.
- Jobs agendados de clientes que rodam de madrugada falharam.

## Timeline (horário de Brasília)
- **03:14** — Certificado atinge a data de expiração (`notAfter`). Handshakes TLS começam
  a falhar com `certificate has expired`.
- **03:21** — Monitoramento sintético externo detecta falha e dispara alerta.
- **03:30** — On-call acionado; confirma com `openssl s_client` que o certificado expirou.
- **03:50** — Descoberto que a renovação automática (cert-manager) havia parado semanas
  antes por um desafio ACME falhando, sem alerta configurado para isso.
- **04:10** — Certificado renovado manualmente e instalado no gateway.
- **04:26** — Gateway recarrega o certificado; API volta a responder normalmente.

## Causa raiz
A renovação automática do certificado falhava silenciosamente desde meados de janeiro
(desafio ACME bloqueado por uma mudança de DNS). Como não havia alerta de expiração nem
de falha de renovação, ninguém percebeu até o certificado vencer de fato.

## Ações corretivas
- Adicionar alerta de **expiração de certificado** com 30 e 7 dias de antecedência.
- Adicionar alerta de **falha de renovação** do cert-manager (CertificateRequest em erro).
- Inventariar todos os certificados em produção e seus pontos de renovação.
- Monitoramento sintético externo de TLS para pegar o problema antes dos clientes.
