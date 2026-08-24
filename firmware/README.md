# Firmware ESP32

O firmware é dividido em três projetos PlatformIO independentes para que uma
falha de clima não retire a segurança da fertirrigação e vice-versa.

| Projeto | Responsabilidade | Estado seguro |
|---|---|---|
| `fertigation/` | DS18B20, dois HX711, Atlas pH/EC e 16 saídas SELV | OE alto e palavra de saída zerada |
| `climate/` | BME280, MLX90614, CO₂ somente leitura, nível do umidificador, exaustor e umidificador | saídas diretas em nível baixo |
| `safety/` | dois pontos de vazamento, E-stop e habilitação global | habilitação global em nível baixo |
| `hil/` | cenários nativos determinísticos | processo encerra com erro na primeira violação |

## Compilar

Instale PlatformIO Core 6.1.19 isoladamente e execute:

```bash
pio run --project-dir firmware/fertigation
pio run --project-dir firmware/climate
pio run --project-dir firmware/safety
pio run --project-dir firmware/hil
pio run --project-dir firmware/hil --target exec
```

Os projetos fixam a plataforma e cada biblioteca por commit. Nenhum SSID,
senha, token ou receita agronômica é gravado no código. Calibrações ausentes
mantêm o nó de fertirrigação em `BOOT`; reiniciar nunca restaura uma saída.

## O que o HIL virtual prova

1. boot começa com todas as saídas desligadas;
2. timeout absoluto corta e retém alarme;
3. vazamento corta imediatamente e impede rearme enquanto molhado;
4. perda do hub durante atuação corta a saída;
5. falha de sensor crítico inibe o comando;
6. reinício volta a `BOOT`, sem repetir a última ordem.

Esses testes não substituem o HIL físico nem o ensaio com água. Pinagem,
footprints, polaridades e plaquetas continuam `A0/HOLD` até medição real.
