import { useEffect, useMemo, useState } from "react";
import { loadSensors, SensorView, Station } from "./api";
import { StatusPill } from "./components";

function ageLabel(value: number | null) {
  if (value === null) return "sem leitura";
  if (value < 60) return `${Math.round(value)} s`;
  return `${Math.round(value / 60)} min`;
}

export function HomePage({ station, refreshKey }: { station: Station; refreshKey: number }) {
  const [sensors, setSensors] = useState<SensorView[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    loadSensors(station.stationId)
      .then((response) => { setSensors(response.sensors); setError(null); })
      .catch((reason: Error) => setError(reason.message));
  }, [station.stationId, refreshKey]);

  const failed = sensors.filter((sensor) => sensor.health === "failed");
  const degraded = sensors.filter((sensor) => sensor.health === "degraded");
  const inhibition = useMemo(() => {
    const unavailable = new Set([...failed, ...degraded].map((sensor) => sensor.sensorId));
    return [
      { name: "Dosagem pH/EC", inhibited: [...unavailable].some((id) => id.includes("ph") || id.includes("ec")), reason: "Exige pH, EC e temperatura da água válidos." },
      { name: "Irrigação automática", inhibited: [...unavailable].some((id) => id.includes("level") || id.includes("leak")), reason: "Exige nível e detector de vazamento válidos." },
      { name: "Clima automático", inhibited: [...unavailable].some((id) => id.includes("air") || id.includes("humidity")), reason: "Exige temperatura e umidade válidas." },
    ];
  }, [failed, degraded]);

  return (
    <>
      <section className="page-heading"><div><p className="eyebrow">Visão geral segura</p><h2>{station.name}</h2></div><StatusPill health={station.health} /></section>
      {error && <div className="alert" role="alert">{error}</div>}
      <section className="metric-grid" aria-label="Leituras atuais">
        {sensors.map((sensor) => <article className={`metric-card metric-${sensor.health}`} key={sensor.sensorId}>
          <div><p>{sensor.label}</p><StatusPill health={sensor.health} /></div>
          <strong>{sensor.value === null ? "—" : sensor.value.toFixed(2)} <small>{sensor.unit}</small></strong>
          <span>idade {ageLabel(sensor.ageSeconds)} · qualidade {sensor.quality}</span>
          {sensor.errorCode && <em>{sensor.errorCode}</em>}
        </article>)}
        {!error && sensors.length === 0 && <div className="empty">Nenhum sensor cadastrado nesta estação.</div>}
      </section>
      <section className="split-grid">
        <article className="panel-card"><h3>Sensores que exigem atenção</h3>
          {failed.length + degraded.length === 0 ? <p className="success-copy">Nenhuma degradação detectada.</p> :
            <ul className="plain-list">{[...failed, ...degraded].map((sensor) => <li key={sensor.sensorId}><StatusPill health={sensor.health} /><span><strong>{sensor.label}</strong><small>{sensor.errorCode ?? `leitura com ${ageLabel(sensor.ageSeconds)}`}</small></span></li>)}</ul>}
        </article>
        <article className="panel-card"><h3>Controles e intertravamentos</h3><ul className="plain-list">
          {inhibition.map((control) => <li key={control.name}><span className={`control-dot ${control.inhibited ? "inhibited" : "released"}`} aria-hidden="true" /><span><strong>{control.name}: {control.inhibited ? "inibido" : "liberado"}</strong><small>{control.inhibited ? control.reason : "Sensores necessários disponíveis; demais intertravamentos continuam ativos."}</small></span></li>)}
          <li><span className="control-dot monitor" aria-hidden="true" /><span><strong>CO₂: não instalado</strong><small>O conjunto DIY mede temperatura e umidade pelo DHT22; o domínio legado continua compatível com sensores opcionais.</small></span></li>
        </ul></article>
      </section>
    </>
  );
}
