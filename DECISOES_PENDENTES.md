# Decisões e validações pendentes — versão DIY

## Já decidido

- [x] Usar notebook existente como hub; não comprar Raspberry Pi.
- [x] Manter hub, banco, painel, MQTT e Home Assistant/EKAZA.
- [x] Usar um ESP32 e GPIO direto.
- [x] Usar seis canais MOSFET para dosagem.
- [x] Usar seis canais do módulo relé de oito canais; dois ficam desconectados.
- [x] Usar pH/EC analógicos, DHT22, boias e sensores simples de vazamento.
- [x] Usar caixas organizadoras, potes de vidro e estante aramada.
- [x] Fazer agitação manual periódica dos concentrados.
- [x] Manter timeout, vazamento, parada local e interlocks básicos.
- [x] Arquivar a engenharia pesada sem apagar o histórico.

## Confirmar com o hardware recebido

- [ ] Variante e pinagem exatas do ESP32.
- [ ] Se o módulo relé é realmente compatível com 3,3 V e ativo em LOW.
- [ ] Se os MOSFETs desligam com entrada flutuante e suportam a corrente medida.
- [ ] Tensão máxima das saídas analógicas de pH/EC.
- [ ] Faixa real e repetibilidade do kit EC em solução nutritiva.
- [ ] Vazão e corrente de cada peristáltica.
- [ ] Vazão/altura das bombas de mistura, irrigação e dreno.
- [ ] Posição/orientação elétrica das duas boias.
- [ ] Detecção de água limpa pelos sensores de vazamento.
- [ ] Capacidade real da estante com as caixas no volume de trabalho.

## Confirmar no local

- [ ] Tomada aterrada e proteção DR existente.
- [ ] Zona seca elevada para notebook, fonte e caixa eletrônica.
- [ ] Distância e caminho dos tubos até o cultivo e dreno.
- [ ] Volume de irrigação necessário por evento.
- [ ] Destino seguro da drenagem.
- [ ] IDs reais das tomadas EKAZA no Home Assistant.

## Regras

- Nenhuma medição será substituída por suposição de anúncio.
- Nenhum nutriente será usado antes do teste completo com água.
- Nenhuma receita será tratada como recomendação agronômica universal.
- Nenhum cabo ou borne de 127 V ficará exposto.
- Se for necessário criar/alterar cabo, tomada ou circuito de rede, a execução é
  de pessoa qualificada e fica fora do orçamento-base.
