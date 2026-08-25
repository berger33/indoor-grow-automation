# Etapa 02 — Placa perfurada, MOSFETs e relés

“Protoboard” neste projeto significa placa perfurada **soldada**. A matriz sem
solda pode ser usada somente por poucos minutos em teste de bancada, nunca na
instalação final.

## Montagem sem cargas

1. Desconecte fonte, USB, bombas e qualquer cabo de rede elétrica.
2. Fixe ESP32, buck, MOSFETs e relés na caixa plástica sem encostar trilhas.
3. Deixe bornes acessíveis somente com a tampa aberta e sistema desligado.
4. Faça barramentos de GND e 12 V com bitola compatível.
5. Ligue o buck à entrada de 12 V, mas ainda sem conectar sua saída.
6. Instale fusíveis nos grupos de bombas.
7. Ligue os seis GPIO de dosagem aos MOSFETs conforme `io-map.csv`.
8. Ligue os seis GPIO de atuação aos canais 1–6 do relé.
9. Deixe canais 7–8 do relé sem fio.
10. Instale pulldowns dos MOSFETs e resistores externos de vazamento/parada.
11. Identifique todas as pontas com função e GPIO.
12. Faça inspeção de solda, polaridade e curto com multímetro.

## Primeira energização

1. Mantenha ESP32 e módulos de saída sem cargas.
2. Energize somente a fonte de 12 V.
3. Ajuste o buck para exatamente 5,0 V.
4. Desligue e conecte a alimentação de 5 V do relé conforme seu manual.
5. Ligue o ESP32 por USB.
6. Confirme que nenhum relé pulsa durante boot ou reset.
7. Meça todos os MOSFETs desligados.
8. Repita cinco ciclos de energia e cinco resets.
9. Acione cada canal com firmware de teste e LED/carga fictícia.
10. Desligue antes de instalar a tampa.

## Gate

- [ ] Buck medido em 5,0 V.
- [ ] Nenhuma saída pulsa no boot.
- [ ] Relés são ativos em LOW como documentado.
- [ ] MOSFETs desligam com ESP32 removido.
- [ ] Canais 7–8 estão desconectados.
- [ ] Caixa fecha sem prensar fio ou módulo.

Não conecte 127 V em bancada aberta. Se um aparelho de rede precisar de cabo ou
emenda nova, essa parte fica fora do tutorial DIY e exige pessoa qualificada.
