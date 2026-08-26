# SBOM e auditoria inicial de licenças

## Resultado

`sbom/indoor-grow.spdx.json` é uma SBOM determinística no formato SPDX 2.3.
Ela contém **78 dependências** declaradas/lockadas de Python, painel e firmware,
além do pacote raiz. O Quality Gate compara o arquivo com os manifests e falha
quando ele fica desatualizado.

| Licença declarada/concluída | Pacotes | Tratamento inicial |
|---|---:|---|
| MIT | 37 | permissiva; preservar avisos |
| Apache-2.0 | 24 | permissiva; preservar licença/NOTICE aplicável |
| MPL-2.0 | 12 | copyleft por arquivo; preservar fontes/avisos de arquivos modificados |
| BSD-3-Clause | 2 | permissiva; preservar aviso e condições |
| ISC | 1 | permissiva; preservar aviso |
| EPL-2.0 OR BSD-3-Clause | 1 | usar opção BSD-3-Clause quando aplicável e documentar |
| LGPL-3.0-only | 1 | manter separação/biblioteca e cumprir redistribuição |

Não foi encontrada dependência declarada como GPL forte nos manifests
inspecionados. Isso é uma triagem técnica, não parecer jurídico.

## Cobertura e limites

A SBOM inclui:

- dependências diretas Python fixadas em `requirements.txt`;
- toda a árvore presente em `web/package-lock.json`;
- plataforma e bibliotecas Git fixadas nos `platformio.ini`;
- biblioteca MQTT PubSubClient fixada no registro PlatformIO;
- plataforma Native vendorizada e sua licença Apache-2.0.

Ainda não inclui todos os pacotes transitivos baixados pelo PlatformIO para o
framework/toolchain ESP32. O CI deve exportar o manifesto resolvido depois do
build e incorporá-lo à SBOM da release candidate. Imagens de contêiner também
precisam de digest e SBOM própria na RC.

## Evidência de origem

Licenças Python foram conferidas nos metadados das distribuições instaladas.
Licenças npm vieram do lockfile. O firmware DIY ativo fixa a
[biblioteca DHT da Adafruit](https://github.com/adafruit/DHT-sensor-library), a
[PubSubClient](https://github.com/knolleary/pubsubclient) e a
[plataforma ESP32 do PlatformIO](https://github.com/platformio/platform-espressif32).
Bibliotecas do firmware de três nós permanecem no arquivo histórico, mas não
entram na SBOM executável porque não são compiladas pelo escopo atual.

## Como atualizar

```bash
python scripts/generate_sbom.py
python scripts/generate_sbom.py --check
```

Depois, revise a diferença, licenças novas e obrigações antes do commit. Não
aceite automaticamente `NOASSERTION`, licença ausente ou pacote sem versão.
