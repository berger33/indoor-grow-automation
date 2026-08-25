# Etapa 08 — Primeiro teste completo somente com água

Não use nutrientes, ácido ou base. Preencha todos os seis potes com água limpa e
use somente água nas caixas.

## Inspeção seca

1. Desligue a tomada e confira tubos, abraçadeiras, fusíveis e etiquetas.
2. Confirme eletrônica fechada e acima dos reservatórios.
3. Confirme bandeja vazia e sensores secos.
4. Confira parada local acessível.
5. Confirme saídas OFF no painel antes de energizar.

## Teste por degraus

1. Energize e aguarde hub/ESP32 ficarem saudáveis.
2. Teste uma dosadora por vez por 5 s.
3. Teste mistura por 10 s.
4. Teste irrigação e colete o volume entregue.
5. Teste drenagem e confirme que não opera seca.
6. Teste exaustor e umidificador sem alterar cabos energizados.
7. Observe cada conexão com papel seco por 30 min.
8. Execute uma receita simulada com água nos seis potes.
9. Meça volume de cada dosadora em dez ciclos.
10. Atualize calibração individual no painel.

## Falhas obrigatórias

1. Molhe um sensor e confirme alarme/corte.
2. Tente rearmar ainda molhado; deve falhar.
3. Pressione o botão local durante uma bomba; deve cortar.
4. Simule boia mínima; mistura/irrigação devem ser inibidas.
5. Simule boia máxima e confirme indicação.
6. Desconecte DHT22; clima deve entrar em política segura.
7. Desconecte pH/EC; correção química deve ser bloqueada.
8. Desligue Wi-Fi/notebook durante uma atuação; timeout local deve cortar.
9. Reinicie ESP32 e notebook; nenhuma saída deve voltar sozinha.
10. Tente irrigação e dreno simultâneos; a segunda ordem deve ser recusada.

## Teste prolongado

Opere somente com água e supervisão por pelo menos um ciclo completo das agendas.
Inspecione temperatura da fonte, módulos, fios, bombas, nível e vazamentos. Pare
imediatamente se houver cheiro, aquecimento, ruído novo, tubo solto ou leitura
instável.

## Gate

- [ ] Dez ciclos por dosadora registrados.
- [ ] Estanqueidade aprovada.
- [ ] Todas as falhas resultam em OFF.
- [ ] Fonte e fios sem aquecimento anormal.
- [ ] Volume de irrigação e drenagem medidos.
- [ ] Reboot seguro e sem repetição de comando.
- [ ] Operação completa com água aprovada.
