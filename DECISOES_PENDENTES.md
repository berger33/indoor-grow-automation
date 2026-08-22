# Decisões pendentes

Itens deste arquivo exigem confirmação humana ou evidência física. Eles não
devem bloquear trabalho independente em outros módulos.

## Instalação física — informações incorporadas

- [x] Adotar 127 V/60 Hz como base da instalação. A frequência brasileira é
  60 Hz; ainda deve ser conferida no ponto de alimentação antes do comissionamento.
- [x] Cadastrar como conjunto padrão quatro painéis Yuxinou: 2 × 120 W, 1 ×
  85 W e 1 × 65 W, total de 390 W.
- [x] Tratar o exaustor atual como motor CA liga/desliga. A imagem fornecida
  mostra quatro fios para ligação 110/220 V, sem interface PWM/0–10 V comprovada.
- [x] Reservar seis recipientes de concentrado de 1 L, um reservatório de água
  de 50 L e um reservatório de mistura/rega de 50 L.
- [x] Autorizar a elaboração e auditoria da BOM e da PCB Rev A.

## Instalação física — validações ainda necessárias

- [ ] Fotografar as plaquetas dos quatro drivers Yuxinou, incluindo tensão,
  corrente, fator de potência, corrente de partida e terminais de dimerização.
- [ ] Fotografar a plaqueta do exaustor atual e fornecer a do futuro substituto.
- [ ] Medir dimensões internas, altura útil e material dos dois reservatórios de
  50 L e dos seis recipientes de 1 L.
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
