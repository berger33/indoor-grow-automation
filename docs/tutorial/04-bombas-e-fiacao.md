# Etapa 04 — Bombas, tubos e fiação de 12 V

As seis peristálticas usam MOSFETs. Mistura, irrigação e drenagem usam relés. O
enchimento do reservatório é manual nesta versão.

## Tubos

1. Posicione uma peristáltica para cada pote e identifique `PD1` a `PD6`.
2. Corte as linhas com folga para manutenção, sem curvas fechadas.
3. Ligue a sucção ao pote correspondente e a descarga ao reservatório de mistura.
4. Termine as descargas acima do nível máximo para reduzir sifonamento.
5. Prenda tubos sem esmagá-los e sem deixar peso sobre a tampa.
6. Posicione a bomba de mistura totalmente submersa no volume mínimo seguro.
7. Ligue a irrigação à linha principal e distribuidores.
8. Dimensione o dreno sem estreitamento; não use linha menor que a saída da bomba.
9. Prenda mangueiras para que uma desconexão não alcance a eletrônica.
10. Identifique as duas pontas de toda linha.

## Fiação DC

1. Mantenha a fonte desligada da tomada.
2. Ligue positivos das peristálticas aos ramais protegidos por fusível.
3. Ligue retornos aos canais MOSFET correspondentes.
4. Ligue as três bombas de água aos contatos dos relés conforme o mapa.
5. Use terminal crimpado ou borne; não torça fio solto em parafuso.
6. Separe fios de motor dos cabos pH/EC.
7. Faça teste de tração em cada terminal.
8. Meça curto entre 12 V e GND antes de inserir fusíveis.
9. Insira um fusível por vez e teste uma bomba por vez.
10. Registre corrente de partida e corrente contínua.

## Teste individual com água

1. Coloque sucção e descarga em recipientes com água limpa.
2. Acione cada peristáltica por 5 s e confirme o sentido.
3. Verifique vazamento na cabeça e no tubo.
4. Teste mistura, irrigação e dreno por 10 s.
5. Confirme que desligam no fim do comando.
6. Simule timeout e confirme corte.
7. Tente irrigação e drenagem juntas; a segunda ordem deve ser recusada.
8. Se uma bomba não mover água, desligue antes de investigar.

## Gate

- [ ] Cada tubo corresponde ao rótulo do canal.
- [ ] Fusíveis instalados e dimensionados pela corrente medida.
- [ ] Nenhuma linha pode gotejar sobre eletrônica.
- [ ] Todas as bombas desligam por timeout.
- [ ] Irrigação e drenagem não ligam juntas.
- [ ] Correntes registradas e fonte sem aquecimento anormal.
