# Tutorial 10A — tomadas EKAZA no painel

> Estado: **software A0/HOLD**. Este procedimento não abre tomada, luminária,
> quadro ou cabo. A carga continua na instalação existente e deve ser conferida
> por profissional antes da agenda automática.

## O que será obtido

Até quatro tomadas EKAZA aparecerão como chaves remotas no painel, cada uma com
estado desejado, estado confirmado, agenda e override temporário. O Raspberry Pi
intermedeia o comando por Home Assistant/Tuya. O ESP32 não recebe credenciais e
nenhum condutor de iluminação entra no rack.

Configuração-base das luminárias informadas:

| Canal lógico | Potência nominal | Entidade sugerida |
|---|---:|---|
| painel 1 | 120 W | `switch.grow_light_1` |
| painel 2 | 120 W | `switch.grow_light_2` |
| painel 3 | 85 W | `switch.grow_light_3` |
| painel 4 | 65 W | `switch.grow_light_4` |

Os 390 W nominais não bastam para aprovar tomada: registre 127 V/60 Hz, corrente,
fator de potência e inrush medidos de cada painel. Não agrupe luminárias em uma
única tomada sem validar plugue, tomada, circuito e especificação EKAZA.

## Pré-requisitos

- Raspberry Pi e Home Assistant acessíveis na rede local;
- telefone com aplicativo Tuya Smart ou Smart Life oficial;
- modelo, número de série/identificador e plaqueta de cada tomada fotografados;
- nenhuma agenda concorrente ativa no aplicativo EKAZA/Tuya;
- backup do hub concluído;
- senha Wi-Fi e conta não compartilhadas em captura, issue ou arquivo do Git.

O fabricante EKAZA anuncia modelos compatíveis com Tuya/Smart Life, mas o modelo
real precisa ser testado. Reparear pode apagar cenas e agendas existentes; faça
isso em janela de manutenção e com as luminárias desligadas.

## Pareamento e autorização

1. Confirme que cada tomada liga e desliga pelo aplicativo EKAZA e anote o canal.
2. Instale **Tuya Smart** ou **Smart Life** oficial e crie a conta do sistema.
3. Siga o manual da tomada para adicioná-la a esse aplicativo. Se ela não aceitar,
   pare: mantenha o aplicativo EKAZA e registre incompatibilidade; não instale
   firmware alternativo nem use API não documentada.
4. No Home Assistant, abra **Configurações → Dispositivos e serviços**.
5. Selecione **Adicionar integração → Tuya**.
6. No aplicativo Tuya/Smart Life, abra **Eu → engrenagem → Conta e segurança** e
   copie o `User Code` somente para a tela de configuração local.
7. Conclua o fluxo e escaneie o QR code exibido pelo Home Assistant usando uma
   segunda tela. Não fotografe nem versione o QR code.
8. Recarregue a integração Tuya e confirme uma entidade `switch` por tomada.
9. Renomeie as entidades conforme a tabela; nomes são IDs estáveis, não apelidos.
10. Baixe o diagnóstico de cada dispositivo e confirme que `status`,
    `status_range` e `function` não estão vazios.

Referência atual do fluxo: <https://www.home-assistant.io/integrations/tuya/>.

## Teste antes da agenda

Para cada tomada, repita 100 ciclos espaçados conforme o manual:

1. mande ligar pelo Home Assistant;
2. confirme mudança da entidade e verificação visual da luminária;
3. mande desligar;
4. confirme entidade e carga;
5. registre latência, falha, estado desconhecido e reconexão.

Depois teste separadamente perda de Wi-Fi, internet, nuvem Tuya, Home Assistant
e backend. O painel deve mostrar `desconhecido` quando não houver confirmação;
nunca deve fingir que um comando foi executado. Falha de luz não pode bloquear
irrigação, dosagem, clima ou segurança.

## Configuração da agenda

1. escolha timezone `America/Sao_Paulo`;
2. cadastre dias, hora de ligar e hora de desligar para cada entidade;
3. visualize a próxima transição antes de salvar;
4. verifique agenda que cruza meia-noite;
5. use override manual sempre com expiração;
6. reinicie o hub e confira reconciliação do desejado com o observado;
7. mantenha apenas o hub como agenda autoritativa para evitar comandos duplos.

## Critério de liberação

- [ ] Quatro entidades estáveis e corretamente associadas.
- [ ] Carga/inrush aprovados por tomada e circuito.
- [ ] Cem ciclos por canal sem estado falso positivo.
- [ ] Falhas de rede/nuvem/hub exibidas e recuperadas.
- [ ] Timezone, meia-noite, reboot e override cobertos por testes.
- [ ] Nenhum segredo encontrado pelo scanner do repositório.
- [ ] Fertirrigação e clima continuam operando com Tuya indisponível.

Se qualquer item falhar, a agenda permanece em HOLD e as tomadas continuam no
controle manual já existente.
