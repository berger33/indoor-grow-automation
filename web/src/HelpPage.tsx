import { useState } from "react";

const topics = [
  { title: "Antes de iniciar", body: "Confira ausência de vazamento, níveis, dreno livre, recipientes identificados, calibrações válidas e botão de parada local acessível. Nunca ignore um controle inibido." },
  { title: "Falha ou leitura vencida", body: "O painel mostra idade e qualidade. Verifique alimentação, cabo e conector do sensor. Só rearme depois de obter leituras estáveis e coerentes; não substitua o valor por estimativa." },
  { title: "Vazamento", body: "Interrompa a operação, desligue a alimentação dos atuadores pelo meio seguro previsto, contenha o líquido e corrija a causa. A trava só pode ser rearmada após confirmação física de piso seco." },
  { title: "Nível baixo", body: "Bombas e umidificador ficam desligados. Inspecione o reservatório e o sensor, complete com líquido correto e só então solicite o rearme seguro." },
  { title: "pH e EC", body: "Use soluções padrão dentro da validade, confirme que as entradas analógicas não excedem 3,3 V e releia o padrão depois da calibração; nunca misture pH+ e pH-." },
  { title: "Batelada", body: "O status queued indica apenas pedido criado. Aguarde ACK do ESP32 e acompanhe cada etapa. Em falha, o estado local seguro prevalece e todas as saídas voltam desligadas." },
  { title: "Sensores econômicos", body: "DHT22 e módulos analógicos podem derivar ou sofrer ruído. Compare com referências, mantenha cabos longe dos motores e bloqueie a automação quando a leitura estiver inválida." },
  { title: "Tomadas EKAZA", body: "Desejado é o que a agenda pede; observado é o que o Home Assistant leu; confirmado exige coincidência entre ambos. A iluminação permanece fora do quadro elétrico do controlador." },
  { title: "Sem rede ou notebook", body: "O ESP32 mantém intertravamentos locais, rejeita comandos vencidos e reinicia com saídas desligadas. Corrija a rede sem contornar as proteções." },
  { title: "Instalação 127 V", body: "O projeto não inclui painel industrial. Nunca deixe bornes expostos; criação ou alteração de cabo, tomada ou circuito de rede deve ser feita por pessoa qualificada." },
];

export function HelpPage() {
  const [query, setQuery] = useState("");
  const visible = topics.filter((topic) => `${topic.title} ${topic.body}`.toLocaleLowerCase("pt-BR").includes(query.toLocaleLowerCase("pt-BR")));
  return <><section className="page-heading"><div><p className="eyebrow">Disponível offline após o primeiro acesso</p><h2>Ajuda de operação segura</h2></div></section><label className="help-search">Buscar orientação<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ex.: vazamento, pH, rede" /></label><section className="help-grid">{visible.map((topic, index) => <details key={topic.title} open={index === 0 && !query}><summary>{topic.title}</summary><p>{topic.body}</p></details>)}{visible.length === 0 && <p className="empty">Nenhuma orientação encontrada. Consulte os tutoriais completos e não opere em caso de dúvida.</p>}</section><aside className="safety-note help-emergency"><strong>Emergência</strong><p>Priorize pessoas, desligue pelo dispositivo de seccionamento previsto e não toque em partes molhadas ou energizadas. Procure profissional habilitado quando houver risco elétrico.</p></aside></>;
}
