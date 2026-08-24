# Revisão dirigida — exaustor e nó climático

Fonte: vídeo complementar de 13:43 fornecido em 2026-08-23. O conteúdo coincide
com o vídeo de projeto das PCBs já estudado, mas permitiu revisar o trecho do
exaustor com foco específico.

## Evidência observada

| Timestamp | Evidência | Confiança |
|---|---|---|
| 02:30–02:44 | terminais da PCB controlam um AC Infinity CLOUDLINE por PWM; o autor cita versões novas com motor EC e borne interno | alta para a revisão filmada |
| 03:42–04:08 | placa de VPD usa dois BME280 e um MLX90614; um canal apresenta leituras anômalas em cabo Cat6 de 10–15 pés | alta |
| 06:54–07:20 | o fan fornece 10 V e GND; MOSFET adapta o PWM de 3,3 V do ESP32 para a entrada de 0–10 V | alta para o circuito filmado |
| 07:20–08:10 | o nó usa 12 V local, regula a lógica e expõe ultrassom, temperatura à prova d'água, vazamento e I²C | alta |

A descrição vinculada pelo autor lista CLOUDLINE S4 e S6. O repositório original
também alerta que, na implementação filmada, a perda de PWM pode parar o fan.
Por isso a reprodução literal do circuito não atende ao requisito fail-safe.

## Perfil adotado

O alvo de atualização é o AC Infinity CLOUDLINE S6 `AI-CLS6`, porque o usuário
pretende substituir o exaustor atual por um mais potente. O fabricante declara
6 pol, 402 CFM, 100–240 VCA, 50/60 Hz, 70 W máximos, motor EC controlado por PWM
e IP44. A unidade atual continua somente liga/desliga em 127 V/60 Hz até a troca.

- ficha oficial: <https://acinfinity.com/cloudline-s6-quiet-inline-fan-6-with-speed-controller/>;
- evidência em marketplace permitido: <https://www.mercadolivre.com.br/exaustor-duto-ac-infinity-cloudline-s6-6-pol-402cfm-silencio/up/MLBU3997482170>.

## Diferença crítica entre revisões

O vídeo mostra três sinais expostos (`10 V`, `GND`, `PWM`). A versão comercial
atual é anunciada como compatível com controladores UIS. Não há evidência
suficiente de que toda unidade `AI-CLS6` atualmente vendida ainda exponha o
mesmo borne interno. Conectar uma interface caseira ao UIS por semelhança de
conector é proibido.

O arquivo
[`exhaust-contract.json`](../../hardware/system/exhaust-contract.json) mantém a
interface direta em HOLD até receber a unidade, registrar revisão/manual,
identificar pinos e medir sinais. Se o borne original não existir, o sistema
usa o controlador do fabricante ou apenas comando liga/desliga aprovado; não
se faz engenharia reversa energizada.

## Requisitos incorporados ao projeto próprio

1. comandos de 0 a 10 níveis, com mínimo seguro definido em comissionamento;
2. limites absolutos de temperatura e UR prevalecem sobre VPD;
3. divergência ou perda dos sensores seleciona ventilação fail-safe, não zero;
4. perda de ESP32/rede não pode retirar a ventilação mínima necessária;
5. comando e feedback físico são entidades diferentes;
6. anti-ciclo, alarme de fan comandado sem resposta e registro de motivo;
7. cálculo do fan considera duto, curvas, filtro e pressão estática, não apenas
   volume geométrico da tenda;
8. fumaça de teste, HIL e piloto climático supervisionado antes de automatizar.

## Pontos ainda não identificados

- revisão exata e pinagem da unidade que será comprada;
- comportamento elétrico ao desconectar PWM em cada revisão;
- comprimento, diâmetro, curvas, filtro e descarga do duto real;
- vazão mínima necessária e nível sonoro aceitável no local;
- corrente de partida medida e coordenação com proteção do circuito;
- existência de feedback de rotação/fluxo acessível sem modificar o produto.
