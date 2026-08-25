# Etapa 05 — Sensores de clima, pH/EC, nível e vazamento

Sensores econômicos são úteis, mas precisam de montagem cuidadosa, referência e
calibração. Nunca conecte uma saída analógica acima de 3,3 V ao ESP32.

## DHT22

1. Monte o DHT22 em pequena placa perfurada ventilada.
2. Posicione na altura da copa, à sombra e fora do jato do umidificador.
3. Ligue dados ao GPIO4 e instale pullup quando o módulo não o incluir.
4. Compare temperatura e UR por 24 h com outro termohigrômetro.
5. Registre desvio e não aplique offset sem evidência.

## pH e EC

1. Instale somente as sondas na zona molhada; módulos BNC ficam na caixa seca.
2. Mantenha cabos BNC e analógicos afastados de motores, relés e fonte.
3. Alimente o módulo conforme o manual recebido.
4. Antes do ESP32, meça a saída em água e padrões conhecidos.
5. Confirme que a tensão permanece entre 0 e 3,3 V.
6. Se exceder, instale condicionamento/divisor calculado e repita a medição.
7. Ligue pH ao GPIO34 e EC ao GPIO35.
8. Enxágue sondas com água adequada entre padrões; não seque por fricção.
9. Calibre pH com pontos conhecidos e EC com padrão da faixa de trabalho.
10. Grave lote, validade, temperatura, tensão e coeficientes obtidos.
11. Releia um padrão independente e aceite somente dentro da tolerância definida.
12. Armazene as sondas conforme o fabricante; sonda de pH não deve secar.

## Boias e vazamento

1. Monte a boia mínima no reservatório de mistura sem furar antes de testar orientação.
2. Monte a boia máxima acima do volume normal de trabalho.
3. Ligue aos GPIO32/33 com `INPUT_PULLUP`.
4. Coloque dois sensores de vazamento nos pontos mais baixos da bandeja.
5. Ligue o agregado ao GPIO36 com pulldown externo.
6. Ligue o botão local NF ao GPIO39 com pullup externo de 10 kΩ.
7. Teste sensores com água limpa e, separadamente, solução de teste descartável.
8. Desconecte cada sensor e confirme que a inspeção identifica a falha.

## Gate

- [ ] pH/EC limitados fisicamente a 3,3 V.
- [ ] Calibração registrada e verificada em padrão conhecido.
- [ ] DHT22 comparado por 24 h.
- [ ] Boias mudam de estado na altura correta.
- [ ] Vazamento corta todas as saídas após três confirmações.
- [ ] Botão local corta saídas e exige rearme manual.
