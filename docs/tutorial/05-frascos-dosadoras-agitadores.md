# Tutorial 05 — frascos, dosadoras e agitadores

> Estado: **A0/HOLD**. Este capítulo permite preparar e testar o conjunto a seco.
> Não coloque fertilizante, corretor de pH nem energize o banco antes de concluir
> amostras, proteções mecânicas, compatibilidade química, HIL e piloto com água.

## Resultado esperado

Ao terminar, a estação terá seis canais independentes, na mesma ordem lógica do
sistema de referência, cada um com frasco de 1 L, barra magnética revestida em
PTFE, agitador sob o frasco, bomba peristáltica e mangueira identificada nas duas
pontas. A denominação `Veg (Grow)` preserva a palavra escolhida para este projeto
e registra o nome `Grow` exibido no sistema original.

| Índice | Etiqueta do usuário | Alias da referência | Bomba | Agitador | Entrada de rotação |
|---:|---|---|---|---|---|
| 0 | pH Down | pH Down | `PD1` | `M1` | `STIR_TACH_1` |
| 1 | CalMag | CalMag | `PD2` | `M2` | `STIR_TACH_2` |
| 2 | Micro | Micro | `PD3` | `M3` | `STIR_TACH_3` |
| 3 | Bloom | Bloom | `PD4` | `M4` | `STIR_TACH_4` |
| 4 | Veg | Grow | `PD5` | `M5` | `STIR_TACH_5` |
| 5 | pH Up | pH Up | `PD6` | `M6` | `STIR_TACH_6` |

Esses nomes identificam funções. O fabricante, a concentração e a dose continuam
configuráveis e devem vir do rótulo, da ficha de segurança e da receita do cultivo.

## Peças ainda sujeitas a aprovação

- seis frascos de vidro ou material compatível, 1 L, com tampa removível;
- seis ventiladores ARCTIC F8 PWM, MPN `AFACO-080P2-GBA01`, 12 V, 80 mm;
- doze ímãs de neodímio, dois por ventilador, dimensões e grau ainda em HOLD;
- seis barras magnéticas revestidas em PTFE, tamanho ainda em HOLD;
- seis proteções `SG1–SG6` que impeçam tocar a hélice e retenham um ímã solto;
- seis bombas peristálticas 24 V `PD1–PD6`, tubos removíveis e compatíveis;
- conversor Mean Well `DDR-30G-12` e proteção individual dos seis ramais;
- mangueira de cada produto, conectores, retenção e etiquetas resistentes;
- bandeja secundária removível sob cada fileira de três frascos.

Não substitua o ventilador de 12 V por uma peça de 24 V. Não escolha ímã, adesivo,
barra, tubo ou vedação apenas pela aparência de um anúncio.

## Montagem mecânica sem produtos

1. Imprima o mapa de canais acima e as pranchas do caderno Rev A.
2. Meça frasco, tampa e ventilador recebidos; registre lote e dimensões.
3. Faça um gabarito com três frascos por fileira e confirme retirada frontal.
4. Instale cada ventilador horizontalmente no berço, soprando para uma direção
   documentada e sem receber gotejamento.
5. Instale somente a proteção mecânica de teste. A fixação definitiva dos dois
   ímãs depende de ensaio de balanceamento e retenção; não improvise cola.
6. Coloque uma barra de teste em um frasco vazio e verifique que ela não encosta
   na tampa, no pescador ou na mangueira quando o frasco for preenchido.
7. Posicione `PD1–PD6` na zona seca adjacente, com acesso frontal para troca do
   tubo peristáltico. Nunca coloque a bomba sob uma conexão que possa pingar.
8. Passe uma linha exclusiva do pescador do frasco à entrada da respectiva bomba.
9. Leve a descarga de cada bomba separadamente até `TK-201`; não una concentrados
   em um coletor antes da água de mistura.
10. Forme quebra-sifão e instale retenção somente após medir pressão de abertura.
11. Etiquete frasco, bomba, mangueira, borne e cabo de tacômetro com o mesmo índice.
12. Fotografe o caminho inteiro de cada canal para o registro as-built.

## Alimentação e sinais SELV

O `OUT07` apenas habilita um driver externo. `DC2` converte 24 V para 12 V e
alimenta os seis ventiladores em velocidade total, como na referência. Cada ramal
deve ter proteção dimensionada depois de medir corrente de partida e regime. O fio
de tacômetro de cada ventilador retorna individualmente à entrada correspondente;
o PWM não é necessário no perfil de referência.

O software só libera `PDn` depois de receber rotação válida de `Mn`. Perda ou
leitura stale durante a dosagem desliga o banco, bloqueia a bomba e gera alarme
retido. O operador precisa eliminar a causa e rearmar explicitamente.

## Sequência de referência

1. confirme nível, vazamentos, qualidade de pH/EC e limites de batelada;
2. transfira água para `TK-201` até o volume inicial;
3. ligue a bomba de mistura de `TK-201` e aguarde 5 s;
4. ligue os seis agitadores e confirme rotação dos canais necessários;
5. dose CalMag, aguarde 60 s;
6. dose Micro, aguarde 60 s;
7. dose Bloom, aguarde 60 s;
8. dose Veg (`Grow` na referência), aguarde 60 s;
9. desligue o banco de agitadores;
10. dilua com água até o alvo de EC ou o limite seguro de volume;
11. somente depois habilite a malha separada de pH.

`pH Up` e `pH Down` não entram na receita base acima. A correção de pH é uma
rotina separada, nunca aciona os dois canais simultaneamente e exige mistura e
tempo de estabilização entre microdoses.

## Teste de recebimento — ainda sem químicos

- [ ] O MPN e a pinagem de cada ventilador foram fotografados.
- [ ] Nenhum rotor raspa e todas as proteções contêm uma peça solta.
- [ ] Os seis tacômetros são lidos simultaneamente por pelo menos 30 min.
- [ ] A corrente total cabe em `DC2` com margem e sem aquecimento anormal.
- [ ] Cada bomba foi acionada individualmente com água e destino visível.
- [ ] Desconectar o tacômetro `n` bloqueia `PDn` e retém o alarme.
- [ ] Trocar duas mangueiras é detectado pela conferência ponta a ponta.
- [ ] Parada de emergência e vazamento retiram energia de todos os atuadores.

## Critério para retirar o HOLD

Exige amostras medidas, desenho de proteção congelado, ensaio de retenção dos
ímãs, teste de compatibilidade por ficha de segurança, curva de cada peristáltica,
HIL, piloto supervisionado somente com água e revisão das rotas as-built. A
primeira batelada química pertence ao Tutorial 13 e não é autorizada aqui.
