# ADR 0009 — Integração lógica de tomadas EKAZA

- Estado: aceito
- Data: 2026-08-24
- Substitui parcialmente: ADR 0006

## Contexto

O responsável mantém as quatro luminárias Yuxinou em tomadas inteligentes EKAZA
e não quer instalar alimentação, relé, contator ou condutor de iluminação na
estação. Entretanto, deseja agenda e comando no mesmo painel de operação.

As tomadas são dispositivos de rede que podem ser expostos como entidades
`switch` pela integração Tuya oficial do Home Assistant. A compatibilidade
depende do modelo e deve ser comprovada em bancada; aparência, corrente anunciada
ou marca não bastam para homologar uma unidade.

## Decisão

O notebook que executa o Grow Hub será a única ponte para iluminação:

1. Home Assistant integra as tomadas EKAZA/Tuya e mantém as credenciais externas;
2. o Grow Hub usa a API REST local do Home Assistant;
3. cada luminária possui entidade, agenda semanal e override com expiração;
4. após cada comando o estado da entidade é relido e exibido como confirmado ou
   divergente;
5. indisponibilidade da tomada, nuvem ou Home Assistant não interfere em
   fertirrigação, clima ou intertravamentos locais.

O ESP32 não recebe token, não comanda a luz e não depende desse serviço. A placa
perfurada, os relés DIY e a fiação de 12 V não possuem circuito de iluminação.
Não haverá dimerização, PPFD, medição elétrica nem recomendação agronômica de
fotoperíodo na v1.0.

## Segurança e falhas

- tokens existem somente como segredos de runtime e nunca são versionados;
- comando enviado não equivale a estado confirmado;
- falha de leitura resulta em estado desconhecido e alarme, não em suposição;
- o reconciliador não repete comando quando o observado já coincide;
- override manual sempre expira e a agenda usa timezone IANA explícito;
- agendas concorrentes no aplicativo EKAZA/Tuya devem ser desativadas;
- modelo, corrente, potência, fator de potência e corrente de partida precisam
  ser validados antes de automatizar uma carga real.

## Consequências

O painel poderá centralizar a experiência do operador sem levar potência de
iluminação à estante. Em contrapartida, esta função pode depender da nuvem Tuya e
deve mostrar degradação com transparência. O ADR 0006 permanece válido para toda
a fronteira física/elétrica; somente a proibição de API, tela e agenda lógica é
substituída por esta decisão.

## Critério de homologação

Cada tomada precisa aparecer como `switch` estável, completar cem ciclos de
bancada, recuperar-se de reinicialização e falhas de rede e ter sua plaqueta e
carga aprovadas. Até isso ocorrer, a agenda automática permanece desabilitada e
não autoriza alteração elétrica.
