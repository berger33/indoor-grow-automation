# SBOM e auditoria inicial de licenças

## Resultado

`sbom/indoor-grow.spdx.json` é uma SBOM determinística no formato SPDX 2.3.
Ela contém **81 dependências** declaradas/lockadas de Python, painel e firmware,
além do pacote raiz. O Quality Gate compara o arquivo com os manifests e falha
quando ele fica desatualizado.

| Licença declarada/concluída | Pacotes | Tratamento inicial |
|---|---:|---|
| MIT | 37 | permissiva; preservar avisos |
| Apache-2.0 | 24 | permissiva; preservar licença/NOTICE aplicável |
| MPL-2.0 | 12 | copyleft por arquivo; preservar fontes/avisos de arquivos modificados |
| BSD-3-Clause | 4 | permissiva; preservar aviso e condições |
| ISC | 1 | permissiva; preservar aviso |
| EPL-2.0 OR BSD-3-Clause | 1 | usar opção BSD-3-Clause quando aplicável e documentar |
| LGPL-3.0-only | 1 | manter separação/biblioteca e cumprir redistribuição |
| NOASSERTION | 1 | bloqueio de fechamento: OneWire no commit fixado |

Não foi encontrada dependência declarada como GPL forte nos manifests
inspecionados. Isso é uma triagem técnica, não parecer jurídico.

## Cobertura e limites

A SBOM inclui:

- dependências diretas Python fixadas em `requirements.txt`;
- toda a árvore presente em `web/package-lock.json`;
- plataforma e bibliotecas Git fixadas nos `platformio.ini`;
- plataforma Native vendorizada e sua licença Apache-2.0.

Ainda não inclui todos os pacotes transitivos baixados pelo PlatformIO para o
framework/toolchain ESP32. O CI deve exportar o manifesto resolvido depois do
build e incorporá-lo à SBOM da release candidate. Imagens de contêiner também
precisam de digest e SBOM própria na RC.

## Evidência de origem

Licenças Python foram conferidas nos metadados das distribuições instaladas.
Licenças npm vieram do lockfile. Para firmware, foram verificados arquivos ou
cabeçalhos dos repositórios upstream: [BME280 BSD](https://github.com/adafruit/Adafruit_BME280_Library),
[MLX90614 BSD](https://github.com/adafruit/Adafruit-MLX90614-Library/blob/master/license.txt),
[HX711 MIT](https://github.com/bogde/HX711/blob/master/LICENSE),
[DallasTemperature MIT](https://github.com/milesburton/Arduino-Temperature-Control-Library) e
[PlatformIO ESP32 Apache-2.0](https://github.com/platformio/platform-espressif32/blob/develop/builder/main.py).

O repositório OneWire não apresentou um identificador SPDX inequívoco no
manifest/arquivo de licença consultado. Ele permanece `NOASSERTION`, mesmo que
existam avisos em arquivos-fonte; a revisão jurídica/técnica do commit fixado é
obrigatória antes de `F5-010` ser concluída.

## Como atualizar

```bash
python scripts/generate_sbom.py
python scripts/generate_sbom.py --check
```

Depois, revise a diferença, licenças novas e obrigações antes do commit. Não
aceite automaticamente `NOASSERTION`, licença ausente ou pacote sem versão.
