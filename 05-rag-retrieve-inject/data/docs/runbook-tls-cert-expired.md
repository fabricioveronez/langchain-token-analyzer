# Runbook — Certificado TLS expirado

## Sintoma
Clientes começam a receber erros de TLS ao acessar o serviço: `certificate has expired`,
`SSL certificate problem: certificate has expired`, ou o navegador exibe
`NET::ERR_CERT_DATE_INVALID`. Chamadas entre serviços (service-to-service) falham no
handshake. O problema costuma surgir "de repente", sem nenhum deploy — porque o gatilho
foi o relógio, não uma mudança de código.

## Diagnóstico
1. Verifique a validade do certificado servido:
   `echo | openssl s_client -connect <host>:443 -servername <host> 2>/dev/null | openssl x509 -noout -dates`
   Veja `notAfter` — se a data já passou, o certificado expirou.
2. Confirme qual certificado está sendo servido (pode haver vários no caminho: load
   balancer, ingress, sidecar). O expirado pode estar em qualquer camada.
3. Causas comuns:
   - Renovação automática (cert-manager / Let's Encrypt) que parou de funcionar:
     desafio ACME falhando, DNS quebrado, ou ClusterIssuer mal configurado.
   - Certificado renovado mas não recarregado pelo processo (precisa reload/restart).
   - Certificado interno de mTLS expirado entre microsserviços.

## Mitigação
- Emita/renove o certificado imediatamente e faça o serviço recarregá-lo.
- Para cert-manager, cheque o `Certificate` e o `CertificateRequest`:
  `kubectl describe certificate <nome>` — veja os eventos do desafio.
- Restaure a renovação automática para não depender de ação manual.
- Adicione alerta de expiração com antecedência (ex.: avisar 30 e 7 dias antes do
  `notAfter`) para nunca ser pego pela data.
- Documente todos os certificados em uso e seus pontos de renovação.
