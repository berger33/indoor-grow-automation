import { FormEvent, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  LightSchedule,
  RemoteLight,
  loadLighting,
  saveSchedule,
  setOverride,
} from "./api";
import "./styles.css";

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
    setSaving(true);
    setMessage(null);
    try {
      onChanged(await setOverride(light.entityId, state));
      setMessage(state === null ? "Override cancelado." : "Override aplicado por 30 minutos.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível enviar o comando.");
    } finally {
      setSaving(false);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      onChanged(await saveSchedule(light.entityId, schedule));
      setMessage("Agenda salva e enviada para reconciliação.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar a agenda.");
    } finally {
      setSaving(false);
    }
  }

  function toggleDay(day: number) {
    const selected = schedule.weekdays.includes(day);
    setSchedule({
      ...schedule,
      weekdays: selected
        ? schedule.weekdays.filter((item) => item !== day)
        : [...schedule.weekdays, day].sort(),
    });
  }

  return (
    <article className="light-card">
      <div className="card-heading">
        <div>
          <p className="eyebrow">Tomada remota</p>
          <h2>{light.label}</h2>
          <code>{light.entityId}</code>
        </div>
        <span className={`status status-${light.status}`}>{statusLabel(light)}</span>
      </div>

      <div className="state-grid" aria-label="Estado da tomada">
        <div><span>Desejado</span><strong>{light.desired === "on" ? "Ligada" : "Desligada"}</strong></div>
        <div><span>Observado</span><strong>{light.observed === null ? "Sem resposta" : light.observed === "on" ? "Ligada" : "Desligada"}</strong></div>
        <div><span>Origem</span><strong>{light.source === "schedule" ? "Agenda" : "Override"}</strong></div>
      </div>
      <p className="explanation">{light.explanation}</p>

      <div className="quick-actions" aria-label="Override temporário">
        <button disabled={saving} onClick={() => updateOverride("on")}>Ligar 30 min</button>
        <button disabled={saving} className="secondary" onClick={() => updateOverride("off")}>Desligar 30 min</button>
        <button disabled={saving || !light.override} className="ghost" onClick={() => updateOverride(null)}>Cancelar</button>
      </div>

      <form onSubmit={submit}>
        <div className="schedule-title">
          <h3>Agenda semanal</h3>
          <label className="switch-label">
            <input type="checkbox" checked={schedule.enabled} onChange={(event) => setSchedule({ ...schedule, enabled: event.target.checked })} />
            Ativa
          </label>
        </div>
        <div className="time-row">
          <label>Ligar<input type="time" value={schedule.onTime} onChange={(event) => setSchedule({ ...schedule, onTime: event.target.value })} /></label>
          <label>Desligar<input type="time" value={schedule.offTime} onChange={(event) => setSchedule({ ...schedule, offTime: event.target.value })} /></label>
        </div>
        <div className="weekday-row" aria-label="Dias da semana">
          {weekdays.map((label, day) => (
            <button key={label} type="button" aria-pressed={schedule.weekdays.includes(day)} className={schedule.weekdays.includes(day) ? "day-selected" : "day"} onClick={() => toggleDay(day)}>{label}</button>
          ))}
        </div>
        <button className="save" disabled={saving || schedule.weekdays.length === 0}>{saving ? "Salvando…" : "Salvar agenda"}</button>
      </form>
      {message && <p className="message" role="status">{message}</p>}
    </article>
  );
}

function App() {
  const [lights, setLights] = useState<RemoteLight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reconciledAt, setReconciledAt] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const response = await loadLighting();
      setLights(response.channels);
      setReconciledAt(response.reconciledAt);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Grow Hub indisponível.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = window.setInterval(() => void refresh(), 30_000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  function replaceLight(updated: RemoteLight) {
    setLights((current) => current.map((light) => light.entityId === updated.entityId ? updated : light));
  }

  return (
    <div className="app-shell">
      <header>
        <div className="brand-mark" aria-hidden="true">GH</div>
        <div>
          <p className="eyebrow">Grow Hub · estação local</p>
          <h1>Iluminação remota</h1>
        </div>
        <div className="hub-status">
          <span className={error ? "dot dot-error" : "dot"}></span>
          <div><strong>{error ? "Hub indisponível" : "Hub conectado"}</strong><small>{reconciledAt ? `Última confirmação ${new Date(reconciledAt).toLocaleTimeString("pt-BR")}` : "Aguardando confirmação"}</small></div>
        </div>
      </header>

      <nav aria-label="Seções do painel">
        <span>Visão geral</span><span>Calibração</span><span>Controle</span><span>Agenda</span><strong>Tomadas Wi‑Fi</strong><span>Alarmes</span>
      </nav>

      <main>
        <section className="intro">
          <div><p className="eyebrow">Home Assistant + EKAZA</p><h2>Quatro luminárias, nenhum circuito de luz no controlador</h2></div>
          <p>O Raspberry Pi envia comandos ao Home Assistant e só mostra sucesso quando a tomada confirma o estado. Falhas remotas não interrompem clima, irrigação ou dosagem.</p>
        </section>

        {error && <div className="alert" role="alert"><strong>Não foi possível carregar as tomadas.</strong><span>{error} Verifique o serviço do Grow Hub e o Home Assistant.</span><button onClick={() => void refresh()}>Tentar novamente</button></div>}
        {loading ? <div className="loading">Carregando estados confirmados…</div> : !error && lights.length === 0 ? <div className="empty"><h2>Nenhuma tomada configurada</h2><p>Conclua o pareamento no Home Assistant e cadastre as entidades <code>switch.*</code>.</p></div> : <section className="cards" aria-label="Tomadas de iluminação">{lights.map((light) => <LightCard key={light.entityId} light={light} onChanged={replaceLight} />)}</section>}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
