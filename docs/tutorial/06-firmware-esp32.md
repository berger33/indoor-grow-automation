# Etapa 06 — Configurar e gravar o firmware

O firmware ativo está em `firmware/controller/`. Não grave os projetos antigos
preservados em `archive/engenharia-pesada/firmware/`.

## Compilar

```bash
pio run --project-dir firmware/controller
pio run --project-dir firmware/hil
pio run --project-dir firmware/hil --target exec
```

## Gravar

1. Desconecte todas as bombas e cargas dos módulos.
2. Confira a variante física do ESP32 e o `io-map.csv`.
3. Conecte somente USB e grave o ambiente `esp32_diy_controller`.
4. Abra o monitor serial em 115200 bit/s.
5. Registre commit, ambiente, porta e motivo de reset.
6. Reinicie cinco vezes e confirme todas as saídas inativas.
7. Teste cada GPIO com LED ou multímetro.
8. Confirme que canais de relé são ativos em LOW.
9. Pressione o botão local; o estado deve ir para alarme e zerar saídas.
10. Molhe o sensor de teste; após três amostras, todas as saídas devem desligar.
11. Simule timeout de uma bomba.
12. Simule perda do heartbeat durante atuação.

## Coeficientes de pH/EC

O controlador usa `valor = slope × volts + offset`. Grave em `Preferences`:

- `ph_slope`, `ph_offset`;
- `ec_slope`, `ec_offset`.

Use o fluxo guiado do painel e as soluções medidas na etapa 05. Sem os quatro
coeficientes, tensão bruta pode aparecer no diagnóstico, mas correção química
automática deve permanecer bloqueada.

## Interlocks que devem passar

- somente uma dosadora por vez;
- pH+ e pH− nunca simultâneos;
- irrigação e dreno nunca simultâneos;
- vazamento e botão local cortam tudo;
- timeout repetido não é renovado por comando duplicado;
- reboot não restaura saída;
- pH/EC inválidos impedem correção química.

## Gate

- [ ] Controller e HIL compilam sem warning tratado como erro.
- [ ] Sete cenários HIL aprovados.
- [ ] Cinco boots sem pulso de saída.
- [ ] Pinagem real coincide com o mapa.
- [ ] Falhas locais levam a OFF.
- [ ] Firmware etiquetado com commit e data.
