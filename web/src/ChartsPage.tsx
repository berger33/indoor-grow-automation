import { useEffect, useState } from "react";
import { HistorySample, loadHistory, Station } from "./api";
import { TrendChart } from "./components";

const metrics = [
  ["ph", "pH", "#52e6a3"], ["ec", "EC", "#62d9df"], ["mass", "Massa", "#b999ff"],
  ["reservoir_level", "Água", "#58a6ff"], ["air_temperature", "Temperatura", "#ff9b73"],
  ["humidity", "Umidade relativa", "#6de0c1"], ["vpd", "VPD", "#ffc866"],
] as const;

export function ChartsPage({ station, refreshKey }: { station: Station; refreshKey: number }) {
  const [samples, setSamples] = useState<HistorySample[]>([]);
  const [hours, setHours] = useState(24);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    loadHistory(station.stationId, hours)
      .then((response) => { setSamples(response.samples); setError(null); })
      .catch((reason: Error) => setError(reason.message));
  }, [station.stationId, hours, refreshKey]);
  return <>
    <section className="page-heading"><div><p className="eyebrow">Histórico real</p><h2>Gráficos ambientais e de solução</h2></div><label className="compact-field">Período<select value={hours} onChange={(event) => setHours(Number(event.target.value))}><option value={6}>6 horas</option><option value={24}>24 horas</option><option value={168}>7 dias</option><option value={720}>30 dias</option></select></label></section>
    <p className="page-note">Somente amostras persistidas são exibidas. Lacunas e falhas não são interpoladas.</p>
    {error && <div className="alert" role="alert">{error}</div>}
    <section className="chart-grid">{metrics.map(([kind, title, accent]) => <TrendChart key={kind} title={title} accent={accent} samples={samples.filter((sample) => sample.kind === kind && sample.quality === "valid")} />)}</section>
  </>;
}
