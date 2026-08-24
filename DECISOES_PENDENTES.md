# Decisões pendentes

Itens deste arquivo exigem confirmação humana ou evidência física. Eles não
devem bloquear trabalho independente em outros módulos.

## Instalação física — informações incorporadas

- [x] Adotar 127 V/60 Hz como base da instalação. A frequência brasileira é
  60 Hz; ainda deve ser conferida no ponto de alimentação antes do comissionamento.
- [x] Excluir por completo a **carga elétrica** de iluminação do rack/PCB e
  integrar somente liga/desliga/agendamento das tomadas EKAZA via hub, conforme
  ADR 0008.
- [x] Tratar o exaustor atual como motor CA liga/desliga. A imagem fornecida
  mostra quatro fios para ligação 110/220 V, sem interface PWM/0–10 V comprovada.
- [x] Reservar seis recipientes de concentrado de 1 L, um reservatório de água
  de 50 L e um reservatório de mistura/rega de 50 L.
- [x] Empilhar `TK-101` sobre `TK-201` no mesmo prumo, usando prateleiras e
  plataformas independentes; descartar a disposição horizontal anterior.
- [x] Autorizar a elaboração e auditoria da BOM e da PCB Rev A.

## Instalação física — validações ainda necessárias

- [ ] Fotografar a plaqueta do exaustor atual e fornecer a do futuro substituto.
- [ ] Medir duto, curvas, filtro e pressão disponível antes de comprar o
  CLOUDLINE S6 `AI-CLS6`; depois confirmar revisão, manual e pinagem recebidos.
- [ ] Informar modelo/plaqueta das tomadas EKAZA e comprovar pareamento de cada
  uma no Tuya Smart ou Smart Life; registrar corrente/inrush das quatro luzes.
- [ ] Medir dimensões internas, altura útil e material dos dois reservatórios de
  50 L, inclusive tampa/alças/curso de retirada, e dos seis recipientes de 1 L.
- [ ] Medir a área disponível para confirmar o envelope máximo de 900 × 600 ×
  2.000 mm e registrar material/estado da parede e do piso.
- [ ] Selecionar rack com documentação de pelo menos 250 kg distribuídos e
  prateleiras de tanque de pelo menos 100 kg, depois validar flecha e ancoragem.
- [ ] Fabricar/selecionar `CT1` e `CT2` e demonstrar 110 L livres, dois drenos
  superiores e esvaziamento seguro em teste somente com água.
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
- [x] Escopo v1.0 centrado em fertirrigação, irrigação, clima, segurança, hub e
  tutorial, com iluminação somente como integração lógica EKAZA/Tuya e sem
  hardware no rack, em 2026-08-23.
