# Firmware ESP32 DIY

O hardware ativo usa um único projeto PlatformIO:

| Projeto | Responsabilidade | Estado seguro |
|---|---|---|
| `controller/` | DHT22, pH/EC analógicos, boias, vazamento, 6 dosadoras, mistura, irrigação, dreno, exaustor e umidificador | MOSFETs em LOW; relés ativos em LOW mantidos em HIGH |
| `hil/` | cenários nativos determinísticos do núcleo | encerra com erro na primeira violação |

Os três nós antigos e a saída por `SN74HCT595` foram preservados somente em
`archive/engenharia-pesada/firmware/`.

## Compilar

Instale PlatformIO Core 6.1.19 isoladamente e execute:

```bash
pio run --project-dir firmware/controller
pio run --project-dir firmware/hil
pio run --project-dir firmware/hil --target exec
```

## Pinagem

Não copie pinos de tutoriais genéricos. Use somente
[`hardware/controller-rev-a/io-map.csv`](../hardware/controller-rev-a/io-map.csv).

- `GPIO21,22,23,25,26,27`: seis canais MOSFET ativos em HIGH;
- `GPIO13,14,16,17,18,19`: seis relés ativos em LOW;
- `GPIO34/35`: pH e EC no ADC1;
- `GPIO36/39`: vazamento e parada local, com resistores externos;
- `GPIO32/33`: boias mínima e máxima;
- `GPIO4`: DHT22.

GPIO34–39 aceitam apenas entrada. A tensão em qualquer GPIO não pode exceder
3,3 V.

## Calibração analógica

O firmware não assume uma fórmula universal para módulos econômicos. Cada canal
usa uma reta `valor = slope × volts + offset`, gravada em `Preferences` com as
chaves:

- `ph_slope` e `ph_offset`;
- `ec_slope` e `ec_offset`.

Sem coeficientes válidos, o firmware publica tensão bruta e marca pH/EC como não
calibrados. O painel não deve liberar correção química automática.

## Segurança preservada

1. boot começa com todas as saídas desligadas;
2. relé ativo em LOW recebe `HIGH` antes de o GPIO virar saída;
3. somente uma bomba de dosagem pode operar por vez;
4. pH+ e pH− não podem operar simultaneamente;
5. irrigação e drenagem são mutuamente exclusivas no roteamento de comandos;
6. toda bomba usa timeout absoluto que não é renovado por comando repetido;
7. vazamento confirmado em três leituras e botão local levam a alarme retido;
8. reinício volta a `BOOT` e nunca repete a última ordem;
9. sensor crítico inválido inibe o atuador correspondente;
10. os dois canais físicos de relé sem uso permanecem desconectados.

O botão de parada é um comando local em baixa tensão, não um dispositivo de
segurança certificado.

## Antes de conectar cargas

1. grave o firmware com todos os conectores de bomba removidos;
2. reinicie cinco vezes e confirme níveis inativos com multímetro;
3. teste cada canal com LED ou carga fictícia;
4. confirme a lógica ativa em LOW do relé recebido;
5. meça a saída do buck em 5,0 V;
6. meça pH/EC em toda a faixa e confirme máximo de 3,3 V;
7. teste vazamento, parada, timeout e perda do hub;
8. conecte uma bomba por vez, sempre com fusível e somente água.
