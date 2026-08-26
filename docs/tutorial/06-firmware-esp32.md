# Etapa 06 — Configurar e gravar o firmware

O firmware ativo está em `firmware/controller/`. Não grave os projetos antigos
preservados em `archive/engenharia-pesada/firmware/`.

## Compilar

Use PlatformIO Core 6.1.19. Antes de gravar, prepare a configuração privada:

1. copie `firmware/controller/include/secrets.example.h` para
   `firmware/controller/include/secrets.h`;
2. informe o Wi-Fi de 2,4 GHz usado pelo ESP32 e o hostname do notebook na rede;
3. cole a CA, o certificado cliente com CN `grow-01-controller` e sua chave em
   literais C multilinha no arquivo local;
4. confirme que o hostname informado consta no SAN do certificado do broker;
5. não use endereço IP se o certificado foi emitido apenas para um nome DNS;
6. nunca envie `secrets.h`, certificados ou chaves ao Git.

Exemplo de formato, deliberadamente sem credenciais:

```cpp
#define GROW_WIFI_SSID "nome-da-rede"
#define GROW_WIFI_PASSWORD ""
#define GROW_MQTT_HOST "growhub.local"
#define GROW_MQTT_PORT 8883
#define GROW_MQTT_CA R"PEM(conteudo-da-ca)PEM"
#define GROW_MQTT_CLIENT_CERT R"PEM(conteudo-do-certificado)PEM"
#define GROW_MQTT_CLIENT_KEY R"PEM(conteudo-da-chave-local)PEM"
```

As palavras do exemplo não autenticam nada. O arquivo real é ignorado pelo
repositório e deve ter acesso restrito no computador de gravação.

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
5. Confirme a sequência `wifi=connecting`, espera do relógio e
   `mqtt=connected tls=verified identity=grow-01-controller`.
6. Desligue o broker e confirme a indisponibilidade retida no tópico de estado;
   não energize cargas neste teste.
7. Registre commit, ambiente, porta e motivo de reset.
8. Reinicie cinco vezes e confirme todas as saídas inativas.
9. Teste cada GPIO com LED ou multímetro.
10. Confirme que canais de relé são ativos em LOW.
11. Pressione o botão local; o estado deve ir para alarme e zerar saídas.
12. Molhe o sensor de teste; após três amostras, todas as saídas devem desligar.
13. Simule timeout de uma bomba.
14. Simule perda do MQTT durante atuação fictícia e confirme a ida a estado
    seguro sem reconexão automática da saída.

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
- [ ] Nove cenários HIL aprovados.
- [ ] Certificado do broker validado por CA e hostname, sem modo inseguro.
- [ ] CN cliente observado no broker como `grow-01-controller`.
- [ ] LWT muda disponibilidade para `offline` após queda comprovada.
- [ ] Cinco boots sem pulso de saída.
- [ ] Pinagem real coincide com o mapa.
- [ ] Falhas locais levam a OFF.
- [ ] Firmware etiquetado com commit e data.
