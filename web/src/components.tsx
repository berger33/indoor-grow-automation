import { Health, HistorySample } from "./api";

export function StatusPill({ health }: { health: Health }) {
  const labels = { healthy: "Normal", degraded: "Degradado", failed: "Falha" };
  return <span className={`status status-${health}`}>{labels[health]}</span>;
}

export function TrendChart({ title, samples, accent }: { title: string; samples: HistorySample[]; accent: string }) {
  if (samples.length === 0) {
    return <article className="chart-card"><h3>{title}</h3><p className="no-data">Sem amostras no período. Nenhum valor foi estimado.</p></article>;
  }
  const values = samples.map((sample) => sample.value);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const range = maximum - minimum || 1;
  const points = samples.map((sample, index) => {
    const x = samples.length === 1 ? 50 : (index / (samples.length - 1)) * 100;
    const y = 92 - ((sample.value - minimum) / range) * 78;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
  const last = samples.at(-1)!;
  return (
    <article className="chart-card">
      <div className="chart-heading"><h3>{title}</h3><strong>{last.value.toFixed(2)} {last.unit}</strong></div>
      <svg viewBox="0 0 100 100" role="img" aria-label={`${title}: mínimo ${minimum.toFixed(2)}, máximo ${maximum.toFixed(2)}, atual ${last.value.toFixed(2)} ${last.unit}`} preserveAspectRatio="none">
        <line x1="0" y1="92" x2="100" y2="92" className="chart-axis" />
        <polyline points={points} fill="none" stroke={accent} strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="chart-range"><span>Mín. {minimum.toFixed(2)}</span><span>{samples.length} amostras</span><span>Máx. {maximum.toFixed(2)}</span></div>
    </article>
  );
}
