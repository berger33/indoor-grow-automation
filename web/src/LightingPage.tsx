import { FormEvent, useCallback, useEffect, useState } from "react";
import { LightSchedule, RemoteLight, loadLighting, saveSchedule, setOverride } from "./api";

const weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
function statusLabel(light: RemoteLight) {
  if (light.status === "confirmed") return "Confirmada";
  if (light.status === "divergent") return "Divergente";
  return "Indisponível";
}

function LightCard({ light, onChanged }: { light: RemoteLight; onChanged: (light: RemoteLight) => void }) {
  const [schedule, setSchedule] = useState<LightSchedule>(light.schedule);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  useEffect(() => setSchedule(light.schedule), [light.schedule]);

  async function updateOverride(state: "on" | "off" | null) {
    setSaving(true); setMessage(null);
    try {
      onChanged(await setOverride(light.entityId, state));
      setMessage(state === null ? "Override cancelado." : "Override aplicado por 30 minutos.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível enviar o comando."); }
    finally { setSaving(false); }
  }
  async function submit(event: FormEvent) {
    event.preventDefault(); setSaving(true); setMessage(null);
    try { onChanged(await saveSchedule(light.entityId, schedule)); setMessage("Agenda salva e enviada para reconciliação."); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível salvar a agenda."); }
    finally { setSaving(false); }
  }
  function toggleDay(day: number) {
    const selected = schedule.weekdays.includes(day);
    setSchedule({ ...schedule, weekdays: selected ? schedule.weekdays.filter((item) => item !== day) : [...schedule.weekdays, day].sort() });
  }
  return <article className="light-card">
    <div className="card-heading"><div><p className="eyebrow">Tomada remota</p><h3>{light.label}</h3><code>{light.entityId}</code></div><span className={`status status-${light.status}`}>{statusLabel(light)}</span></div>
    <div className="state-grid" aria-label="Estado da tomada"><div><span>Desejado</span><strong>{light.desired === "on" ? "Ligada" : "Desligada"}</strong></div><div><span>Observado</span><strong>{light.observed === null ? "Sem resposta" : light.observed === "on" ? "Ligada" : "Desligada"}</strong></div><div><span>Origem</span><strong>{light.source === "schedule" ? "Agenda" : "Override"}</strong></div></div>
    <p className="explanation">{light.explanation}</p>
    <div className="quick-actions" aria-label="Override temporário"><button disabled={saving} onClick={() => void updateOverride("on")}>Ligar 30 min</button><button disabled={saving} className="secondary" onClick={() => void updateOverride("off")}>Desligar 30 min</button><button disabled={saving || !light.override} className="ghost" onClick={() => void updateOverride(null)}>Cancelar</button></div>
    <form onSubmit={(event) => void submit(event)}><div className="schedule-title"><h3>Agenda semanal</h3><label className="switch-label"><input type="checkbox" checked={schedule.enabled} onChange={(event) => setSchedule({ ...schedule, enabled: event.target.checked })} />Ativa</label></div><div className="time-row"><label>Ligar<input type="time" value={schedule.onTime} onChange={(event) => setSchedule({ ...schedule, onTime: event.target.value })} /></label><label>Desligar<input type="time" value={schedule.offTime} onChange={(event) => setSchedule({ ...schedule, offTime: event.target.value })} /></label></div><div className="weekday-row" aria-label="Dias da semana">{weekdays.map((label, day) => <button key={label} type="button" aria-pressed={schedule.weekdays.includes(day)} className={schedule.weekdays.includes(day) ? "day-selected" : "day"} onClick={() => toggleDay(day)}>{label}</button>)}</div><button className="save" disabled={saving || schedule.weekdays.length === 0}>{saving ? "Salvando…" : "Salvar agenda"}</button></form>
    {message && <p className="message" role="status">{message}</p>}
  </article>;
}

export function LightingPage({ refreshKey }: { refreshKey: number }) {
  const [lights, setLights] = useState<RemoteLight[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [reconciledAt, setReconciledAt] = useState<string | null>(null);
  const refresh = useCallback(async () => {
    try { const response = await loadLighting(); setLights(response.channels); setReconciledAt(response.reconciledAt); setError(null); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Grow Hub indisponível."); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh, refreshKey]);
  const replace = (updated: RemoteLight) => setLights((current) => current.map((light) => light.entityId === updated.entityId ? updated : light));
  return <><section className="page-heading"><div><p className="eyebrow">Home Assistant + EKAZA</p><h2>Iluminação remota</h2></div><p className="page-note">{reconciledAt ? `Última reconciliação ${new Date(reconciledAt).toLocaleString("pt-BR")}` : "Aguardando confirmação real"}</p></section><p className="page-note">A iluminação não passa pelo quadro do controlador. Sucesso só aparece após releitura do estado no Home Assistant.</p>{error && <div className="alert" role="alert">{error}<button onClick={() => void refresh()}>Tentar novamente</button></div>}<section className="cards">{lights.map((light) => <LightCard key={light.entityId} light={light} onChanged={replace} />)}</section></>;
}
