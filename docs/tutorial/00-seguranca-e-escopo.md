# Etapa 00 — segurança, escopo e responsabilidades

## Objetivo

Ao terminar esta etapa, você deve conseguir apontar as zonas seca e molhada,
explicar o que o E-stop remove e separar atividades de montagem mecânica/SELV
das atividades exclusivas de profissional habilitado.

Não comece a comprar ou montar enquanto o repositório indicar `A0/HOLD`.

## O sistema que será montado

- seis recipientes de concentrado de 1 L com dosagem individual;
- um reservatório de água de 50 L;
- um reservatório de mistura/rega de 50 L;
- transferência, mistura, irrigação e dreno;
- pH, EC, temperatura da solução, massa/nível e vazamento;
- temperatura, umidade, VPD, CO₂, exaustão e umidificação;
- Raspberry Pi e painel local.

A automação de iluminação existente não se conecta a este projeto.

## Divisão de responsabilidades

| Atividade | Pessoa leiga com tutorial | Profissional habilitado |
|---|:---:|:---:|
| Conferir códigos, quantidades e danos de transporte | sim | opcional |
| Montar prateleiras, contenção e plataformas sem energia | sim | opcional |
| Cortar/identificar mangueiras após P&ID aprovado | sim | opcional |
| Montar chicote plugável SELV desenergizado | somente após validação do capítulo | revisão recomendada |
| Dimensionar cabos, disjuntores, DR, DPS e aterramento | não | obrigatório |
| Abrir quadro com rede presente | não | obrigatório |
| Ligar ou medir 127 V | não | obrigatório |
| Executar laudo de continuidade do PE/isolação/DR | não | obrigatório |
| Calibrar sensores e bombas com água | sim, após liberação | supervisão inicial recomendada |
| Manusear ácido/base/fertilizante concentrado | conforme SDS e treinamento | suporte quando aplicável |

## Zonas que você deve marcar no local

1. **Zona seca:** quadro, fontes e hub; nenhuma tubulação acima dela.
2. **Zona de dosagem:** frascos e peristálticas dentro de contenção removível.
3. **Zona hidráulica:** tanques, bombas, válvulas e uniões.
4. **Zona de cultivo:** emissores, bandeja/dreno e sensores climáticos SELV.
5. **Rota de emergência:** acesso livre ao E-stop, seccionamento e saída.

Não escolha distâncias definitivas pela imagem realista. Use o desenho cotado
as-built que será liberado após medir o local.

## Estado seguro esperado

Ao pressionar o E-stop ou detectar vazamento crítico:

- dosadoras e agitadores param;
- bombas de transferência, mistura, irrigação e dreno param;
- válvulas normalmente fechadas retornam fechadas;
- umidificador desliga;
- exaustor assume o estado seguro definido no comissionamento;
- hub e sensores podem permanecer alimentados para registrar e alertar;
- o alarme não desaparece apenas porque a água secou ou o sistema reiniciou.

O reset só é aceito depois de inspeção física, remoção da causa e confirmação do
operador autorizado.

## Checklist desta etapa

- [ ] Li `docs/ESCOPO_V1.md` e sei que iluminação não integra o sistema.
- [ ] Li o aviso `A0/HOLD` e não vou comprar lote nem energizar o protótipo.
- [ ] Identifiquei no local uma parede/zona seca acima dos tanques.
- [ ] Confirmei que nenhuma mangueira precisará passar sobre quadro ou hub.
- [ ] Reservei acesso frontal aos dois tanques e seis frascos.
- [ ] Reservei caminho livre para E-stop e seccionamento.
- [ ] Identifiquei o profissional responsável pela instalação 127 V.
- [ ] Sei onde registrar fotos, medições e desvios antes de continuar.

## Evidência para liberar a etapa 01

Anexe ao relatório de instalação:

- foto panorâmica do local sem componentes instalados;
- croqui com zona seca, tanques, cultivo, dreno e ponto de alimentação;
- medidas de largura, profundidade, altura e distâncias entre zonas;
- nome/registro do profissional que revisará a parte elétrica;
- confirmação de que não existe integração com a iluminação.

Se qualquer rota de água cruzar a zona seca, a etapa é reprovada e o layout deve
ser redesenhado.
