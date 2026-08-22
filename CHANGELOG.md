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
- modelo de cargas configuráveis com corrente medida, de placa ou estimada;
- base elétrica fixa 127 V/60 Hz para o conjunto padrão de 390 W;
- BOM A0 de quadro, controladora, sensores, atuadores e hub;
- manifestos de I/O, netlist e parâmetros de fabricação da PCB SELV;
- validação automática de 161 referências entre BOM e manifestos;
- laudo preliminar, matriz de riscos e dois desenhos técnicos da Rev A.

### Segurança

- rejeição de identificadores, unidades e números não finitos;
- rejeição de campos MQTT ausentes, extras ou com tipos ambíguos;
- scanner impede tokens, chaves privadas e segredos atribuídos.
