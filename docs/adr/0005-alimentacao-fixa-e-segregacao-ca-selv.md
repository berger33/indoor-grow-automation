# ADR 0005 — Alimentação fixa e segregação entre CA e SELV

- Status: aceito
- Data: 2026-08-22

## Contexto

A instalação informada é 127 V. O conjunto padrão possui quatro painéis Yuxinou
de 120 W, 120 W, 85 W e 65 W, totalizando 390 W. O exaustor atual aparece apenas
em uma instrução genérica de ligação com quatro fios e enrolamentos configuráveis
para 110/220 V; a imagem não identifica modelo, corrente, potência ou interface
de controle de velocidade.

Uma chave 127/220 V no equipamento ampliaria o número de contatos, combinações
de ligação e falhas possíveis. Cargas conectadas na posição errada podem ser
danificadas, e o software não consegue provar a tensão física selecionada.

## Decisão

1. A variante instalada será **127 V, 60 Hz, fase-neutro-terra**, sujeita à
   conferência por profissional habilitado e medição antes do comissionamento.
2. Não haverá seletor 127/220 V no gabinete nem chaveamento de tensão comandado
   pelo ESP32.
3. O cadastro de cargas aceitará 127 V ou 220 V para reutilização do software em
   outras instalações, mas a tensão será parâmetro de projeto somente leitura
   para o operador comum.
4. Fontes de controle podem ter entrada universal 85–264 VCA, sem converter a
   tensão disponível para as cargas.
5. Nenhuma tensão de rede passará pela PCB controladora. Ela trabalhará em
   24 VCC/5 VCC/3,3 VCC SELV e comandará contatores externos com bobina 24 VCC.
6. O exaustor atual será somente liga/desliga. PWM, triac ou 0–10 V ficam
   inibidos até existir manual/plaqueta que declare expressamente a interface.
7. Cada luminária será cadastrada separadamente. Liga/desliga usará contatores
   externos; dimerização só será habilitada após identificar o driver e sua
   interface documentada (0–10 V, PWM, resistor ou protocolo digital).

## Consequências

- reduz risco de sobretensão por seleção incorreta;
- permite usar a mesma aplicação em instalações 127/220 V sem tornar o quadro
  comutável em campo;
- exige uma variante elétrica documentada para cada tensão;
- preserva separação física e elétrica entre rede CA e lógica;
- mantém pendentes a corrente de placa, o fator de potência, a corrente de
  partida e o método de dimerização dos drivers Yuxinou;
- mantém pendente a plaqueta do exaustor atual e do futuro substituto.

## Alternativas rejeitadas

- **Chave manual 127/220 V:** simples apenas em aparência; não impede posição
  incompatível com cargas já conectadas.
- **Comutação automática de enrolamentos:** requer detecção independente de
  tensão, contatores intertravados e validação do motor, sem benefício para a
  instalação fixa.
- **Controle de motor CA por dimmer genérico:** rejeitado sem declaração de
  compatibilidade do fabricante.
