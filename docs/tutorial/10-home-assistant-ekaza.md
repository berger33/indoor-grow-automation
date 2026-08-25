# Etapa 10 — Home Assistant e tomadas EKAZA

Esta integração continua igual na camada de software. Ela controla somente as
tomadas EKAZA já existentes para iluminação. Nenhum condutor de luminária entra
no ESP32, nos relés DIY ou na estante hidráulica.

## Parear e identificar

1. Confirme cada tomada no aplicativo oficial compatível.
2. Adicione a integração Tuya suportada ao Home Assistant.
3. Confirme uma entidade `switch` distinta por tomada.
4. Renomeie IDs de forma estável.
5. Registre qual luminária corresponde a cada entidade.
6. Remova agendas concorrentes do aplicativo para ter uma fonte autoritativa.
7. Crie token exclusivo do Grow Hub e guarde fora do Git.
8. Configure URL e token no ambiente do hub.
9. Reinicie e releia cada entidade.
10. Confirme que o painel diferencia desejado, observado e divergente.

## Homologação

1. Teste ligar/desligar e releia o estado real.
2. Repita cem ciclos por tomada, espaçados conforme o equipamento.
3. Registre latência, indisponibilidade e falso positivo.
4. Teste perda de Wi-Fi, internet, Home Assistant e integração Tuya.
5. Confirme que falha de iluminação não bloqueia cultivo.
6. Teste agenda cruzando meia-noite e timezone `America/Sao_Paulo`.
7. Teste override com expiração.
8. Reinicie hub/Home Assistant e confirme reconciliação.

## Segurança

Não abra tomada, luminária ou cabo. Confirme a compatibilidade de potência e
corrente segundo o modelo real da tomada e da carga. Um comando sem releitura
confirmada deve aparecer como desconhecido/divergente, nunca como sucesso.

## Gate

- [ ] Entidades reais e estáveis.
- [ ] Cem ciclos por canal registrados.
- [ ] Estado observado confirmado após cada comando.
- [ ] Falhas de rede não afetam fertirrigação ou clima.
- [ ] Nenhum segredo em arquivo versionado ou log.
