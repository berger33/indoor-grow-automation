# Tutorial de montagem DIY

Este tutorial substitui integralmente a sequência industrial antiga. Ele usa
um notebook, um ESP32, placa perfurada, relés, MOSFETs, bombas econômicas,
sensores analógicos, caixas organizadoras, potes de vidro e estante aramada.

## Antes de começar

Água e eletricidade exigem disciplina mesmo em um projeto doméstico:

- trabalhe sempre desenergizado durante a montagem;
- mantenha toda eletrônica acima da água e dentro de caixa fechada;
- use tomada aterrada e proteção DR existente;
- nunca deixe borne de rede exposto;
- qualquer criação ou alteração de cabo/tomada de 127 V deve ser feita por
  pessoa qualificada;
- não use nutrientes antes de aprovar o teste completo somente com água;
- não deixe a primeira receita real sem supervisão.

## Ordem obrigatória

1. [Comprar e conferir os componentes](01-compras.md)
2. [Montar placa perfurada, MOSFETs e relés](02-protoboard-e-reles.md)
3. [Montar estante, caixas e potes](03-prateleira-e-potes.md)
4. [Instalar bombas, tubos e fiação](04-bombas-e-fiacao.md)
5. [Instalar e calibrar sensores](05-sensores-ph-ec-clima.md)
6. [Configurar e gravar o firmware](06-firmware-esp32.md)
7. [Instalar o hub no notebook](07-hub-no-notebook.md)
8. [Executar o primeiro teste com água](08-primeiro-teste-com-agua.md)
9. [Cadastrar e executar a primeira receita](09-primeira-receita.md)
10. [Confirmar Home Assistant e tomadas EKAZA](10-home-assistant-ekaza.md)

Não pule um gate. Se uma etapa falhar, desligue, corrija e repita a própria
etapa antes de avançar.

## Evidências a guardar

- fotos da montagem seca e das etiquetas;
- modelo/pinagem dos módulos recebidos;
- tensão do buck e corrente das bombas;
- volumes dos dez ciclos de calibração por dosadora;
- leituras das soluções de pH/EC;
- resultado dos testes de vazamento, parada, timeout e retorno de energia;
- commit do firmware e do hub usados;
- data e resultado do teste com água e da primeira receita.

O tutorial orienta uma montagem experimental. Ele não transforma módulos
genéricos em instrumentos certificados e não elimina a necessidade de
supervisão e manutenção.
