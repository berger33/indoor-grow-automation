# Decisões pendentes

Itens deste arquivo exigem confirmação humana ou evidência física. Eles não
devem bloquear trabalho independente em outros módulos.

## Instalação física — informações incorporadas

- [x] Adotar 127 V/60 Hz como base da instalação. A frequência brasileira é
  60 Hz; ainda deve ser conferida no ponto de alimentação antes do comissionamento.
- [x] Manter toda a potência de iluminação fora da estação: as luminárias Yuxinou
  permanecem nas tomadas EKAZA existentes e recebem apenas comandos de software.
- [x] Tratar o exaustor atual como motor CA liga/desliga. A imagem fornecida
  mostra quatro fios para ligação 110/220 V, sem interface PWM/0–10 V comprovada.
- [x] Reservar seis recipientes de concentrado de 1 L, um reservatório de água
  de 50 L e um reservatório de mistura/rega de 50 L.
- [x] Autorizar a elaboração e auditoria da BOM e da PCB Rev A.

## Instalação física — validações ainda necessárias

- [ ] Fotografar a plaqueta do exaustor atual e fornecer a do futuro substituto.
- [ ] Fotografar a plaqueta e informar o código exato de cada tomada EKAZA;
  confirmar que cada unidade aparece como entidade `switch` no Home Assistant.
- [ ] Fotografar as plaquetas das quatro luminárias e medir corrente e inrush por
  tomada; os 390 W nominais totais não homologam plugue, carga ou circuito.
- [ ] Executar cem ciclos por tomada e ensaiar perda/retorno de Wi-Fi, internet,
  Home Assistant e nuvem Tuya antes de habilitar a agenda automática.
- [ ] Medir dimensões internas, altura útil e material dos dois reservatórios de
  50 L e dos seis recipientes de 1 L.
- [ ] Informar a altura entre reservatórios, cultivo e destino do dreno, além da
  distância total de cada linha hidráulica.
- [ ] Confirmar se o reservatório de água será abastecido manualmente ou por uma
  linha fixa com osmose reversa.
- [ ] Definir modelo do umidificador ou autorizar a seleção após ensaio de bancada.
- [ ] Informar distância do quadro ao ponto de alimentação, método de instalação
  dos cabos, esquema de aterramento e cargas auxiliares pretendidas.
- [ ] Dimensionar e executar circuito dedicado, DR/DPS, proteção e aterramento
  com profissional habilitado conforme NBR 5410 e NR-10.
- [ ] Executar ERC/DRC no KiCad, revisão independente, montagem de uma unidade,
  ensaios elétricos/HIL e piloto com água antes de fabricar lote.

## Regras

Nenhuma compra, fabricação, ligação à rede elétrica ou publicação de release
v1.0 será executada automaticamente com base apenas em suposição.

## Resolvidas

- [x] Repositório público `berger33/indoor-grow-automation` criado, conectado e
  populado em 2026-08-22.
- [x] Escopo v1.0 limitado a fertirrigação, irrigação, clima, segurança, hub e
  tutorial de montagem em 2026-08-23.
