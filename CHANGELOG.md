# Changelog

Todas as mudanças relevantes serão registradas neste arquivo. O projeto segue
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e pretende adotar
versionamento semântico a partir da primeira release.

## [Não publicado]

### Adicionado

- estrutura inicial do repositório;
- especificação de referência e seis pranchas técnicas;
- decisões iniciais de arquitetura e segurança;
- backlog executável por fases.
- portão local e CI com compilação Python, 29 testes e scan de segredos;
- modelo imutável de amostras com unidade, timestamp e qualidade;
- validação de plausibilidade e política de telemetria stale;
- contrato MQTT de telemetria v1 com codec estrito e schema JSON;
- templates estruturados de issue e pull request;
- política de branches, commits e releases;
- atualizações semanais de Actions e dependências Python via Dependabot.
- modelo de cargas ambientais configuráveis com corrente medida, de placa ou
  estimada;
- escopo v1 restrito a fertirrigação, irrigação, clima, segurança, hub e tutorial;
- base elétrica fixa 127 V/60 Hz sem qualquer circuito de iluminação;
- revisão dirigida do vídeo V1 de hardware com evidências por timestamp;
- BOM A0 de quadro, controladora, seis frascos, dois tanques, hidráulica,
  sensores, atuadores, contenção e hub;
- matriz de 15 funções comandadas e controladora redimensionada para 16 canais;
- registradores `SN74HCT595`, safe enable e atualização atômica das saídas;
- manifestos de I/O, netlist e parâmetros de fabricação da PCB SELV 200 × 120 mm;
- validação automática de 248 referências e da matriz de atuadores;
- laudo preliminar e desenhos técnicos atualizados para `A0/REWORK/HOLD`;
- três visualizações realistas conceituais da estação, fertirrigação e clima;
- índice de tutorial em 15 etapas e capítulo inicial de segurança.

### Segurança

- rejeição de identificadores, unidades e números não finitos;
- rejeição de campos MQTT ausentes, extras ou com tipos ambíguos;
- scanner impede tokens, chaves privadas e segredos atribuídos.
