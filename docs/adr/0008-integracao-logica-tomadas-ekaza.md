# ADR 0008 — Integração lógica com tomadas EKAZA

- Estado: aceito
- Data: 2026-08-23
- Supera parcialmente: ADR 0006

## Contexto

As luminárias já estão instaladas em tomadas inteligentes EKAZA e não devem
entrar no quadro, na PCB, na BOM elétrica nem nos chicotes deste sistema. O
operador, porém, quer visualizar o estado e programar liga/desliga no mesmo
painel mobile-first mostrado no vídeo de referência.

Tomadas EKAZA Wi-Fi são anunciadas como compatíveis com Tuya/Smart Life. A
integração oficial Tuya do Home Assistant suporta dispositivos adicionados aos
aplicativos Tuya Smart ou Smart Life, por autenticação e QR code. Essa integração
é `Cloud Push` e o SDK oficial pode expor menos funções que o aplicativo.

## Decisão

1. Nenhuma tensão, tomada, relé, contator, medição, dimmer ou borne de
   iluminação será adicionado ao rack ou à PCB.
2. O Raspberry Pi hospedará um adaptador lógico Home Assistant/Tuya para as
   tomadas EKAZA que forem comprovadamente pareáveis pelo Smart Life/Tuya Smart.
3. O backend continua sendo a fonte da agenda e usa a entidade `switch` do Home
   Assistant como porta; o painel nunca fala diretamente com a tomada.
4. O ESP32 não recebe senha EKAZA/Tuya, não chama nuvem e não participa do
   fotoperíodo. Perda dessa integração não interfere em fertirrigação ou clima.
5. Cada comando registra desejado, estado observado, instante, origem e erro. A
   UI só mostra “ligada” após confirmação da entidade; timeout fica “desconhecido”.
6. Agenda aceita timezone, dias, hora de ligar/desligar, habilitação e exceção
   manual com expiração. Reinício reconcilia desejado versus observado.
7. Credenciais, tokens e URLs ficam em secret store/variáveis de ambiente; nunca
   em firmware, repositório, logs, QR code capturado ou backup sem criptografia.
8. A integração só é liberada depois de testar o modelo real, medir a carga nas
   tomadas e confirmar que potência, corrente e inrush das luminárias não excedem
   a especificação do fabricante.

## Fluxo de configuração

1. identificar modelo/plaqueta de cada tomada EKAZA e cada luminária;
2. confirmar no aplicativo se o dispositivo pode ser adicionado ao Tuya Smart ou
   Smart Life; a compatibilidade comercial não substitui esse teste;
3. no Home Assistant, adicionar a integração oficial Tuya, informar `User Code`
   e concluir o QR code em tela separada;
4. renomear entidades como `switch.grow_light_1` a `switch.grow_light_4`;
5. cadastrar no backend apenas os IDs permitidos, sem credenciais Tuya;
6. testar ligar/desligar individual, estado, perda de internet, retorno e reboot;
7. só então habilitar a agenda pelo painel.

## Consequências

- o painel ganha página “Iluminação remota” e agenda de fotoperíodo;
- hardware e documentação elétrica continuam explicitamente sem iluminação;
- há dependência de Wi-Fi, nuvem Tuya e autenticação periódica neste módulo;
- uma tomada incompatível continua operável pelo aplicativo EKAZA, mas não é
  simulada nem controlada por integração não documentada;
- dimmer, PPFD, potência de driver, canais espectrais e automação Arduino de luz
  permanecem fora do escopo.

## Fontes

- EKAZA, tomada inteligente 16 A: <https://www.ekaza.com.br/automacao/tomada-inteligente-16a/>;
- Home Assistant, integração oficial Tuya: <https://www.home-assistant.io/integrations/tuya/>;
- Tuya, serviços de nuvem: <https://developer.tuya.com/en/docs/cloud>.

## Critérios de retirada do HOLD

- modelos/plaquetas e carga das quatro tomadas registrados;
- pareamento Smart Life/Tuya comprovado e entidades `switch` disponíveis;
- liga/desliga e confirmação testados 100 vezes por tomada;
- perda/retorno de Wi-Fi, internet, Tuya, Home Assistant e backend ensaiados;
- agenda, timezone, reboot e override manual cobertos por testes;
- usuário leigo valida o tutorial sem acesso a segredo no repositório.
