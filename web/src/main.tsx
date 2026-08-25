import { FormEvent, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ApiError, login, loadStations, logout, Station } from "./api";
import { ChartsPage } from "./ChartsPage";
import { HomePage } from "./HomePage";
import { LightingPage } from "./LightingPage";
import { OperationPage } from "./OperationPage";
import { CalibrationPage } from "./CalibrationPage";
import { AlarmsPage } from "./AlarmsPage";
import { HelpPage } from "./HelpPage";
import { connectRealtime, RealtimeStatus } from "./realtime";
import "./styles.css";

type Page = "home" | "charts" | "operation" | "calibration" | "lighting" | "alarms" | "help";
const pages: { id: Page; label: string }[] = [
  { id: "home", label: "Visão geral" }, { id: "charts", label: "Gráficos" },
  { id: "operation", label: "Operação" }, { id: "calibration", label: "Calibração" },
  { id: "lighting", label: "Tomadas Wi-Fi" }, { id: "alarms", label: "Alarmes" }, { id: "help", label: "Ajuda" },
];

function LoginPanel({ onLogin }: { onLogin: () => void }) {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setMessage(null);
    try { await login(userId, password); setPassword(""); onLogin(); }
    catch (reason) { setMessage(reason instanceof Error ? reason.message : "Não foi possível entrar."); }
    finally { setBusy(false); }
  }
  return <main className="login-shell"><section className="login-card"><div className="brand-mark" aria-hidden="true">GH</div><p className="eyebrow">Grow Hub local</p><h1>Acesso ao painel</h1><p>Use uma conta cadastrada no Raspberry Pi. A sessão expira automaticamente e não é salva no navegador.</p><form onSubmit={(event) => void submit(event)}><label>Usuário<input autoComplete="username" value={userId} onChange={(event) => setUserId(event.target.value)} required /></label><label>Senha<input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label><button disabled={busy}>{busy ? "Entrando…" : "Entrar"}</button></form>{message && <p className="form-error" role="alert">{message}</p>}</section></main>;
}

function App() {
  const [page, setPage] = useState<Page>("home");
  const [stations, setStations] = useState<Station[]>([]);
  const [stationId, setStationId] = useState("");
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [realtime, setRealtime] = useState<RealtimeStatus>("connecting");
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshStations = useCallback(async () => {
    try {
      const response = await loadStations(); setStations(response.stations);
      setStationId((current) => current || response.stations[0]?.stationId || "");
      setAuthenticated(true); setError(null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) setAuthenticated(false);
      else setError(reason instanceof Error ? reason.message : "Grow Hub indisponível.");
    }
  }, []);
  useEffect(() => { void refreshStations(); }, [refreshStations]);
  useEffect(() => {
    if (!authenticated) return;
    return connectRealtime(setRealtime, () => setRefreshKey((current) => current + 1));
  }, [authenticated]);

  if (authenticated === null) return <div className="loading-screen">Abrindo painel seguro…</div>;
  if (!authenticated) return <LoginPanel onLogin={() => void refreshStations()} />;
  const station = stations.find((item) => item.stationId === stationId);
  return <div className="app-shell">
    <a className="skip-link" href="#content">Pular para o conteúdo</a>
    <header><div className="brand-mark" aria-hidden="true">GH</div><div><p className="eyebrow">Grow Hub · estação local</p><h1>Painel de cultivo</h1></div><div className="header-actions"><label>Estação<select value={stationId} onChange={(event) => setStationId(event.target.value)}>{stations.map((item) => <option value={item.stationId} key={item.stationId}>{item.name}</option>)}</select></label><div className="hub-status"><span className={`dot dot-${realtime}`} /><div><strong>{realtime === "online" ? "Tempo real conectado" : realtime === "connecting" ? "Reconectando" : "Modo offline"}</strong><small>{realtime === "offline" ? "Eventos serão retomados pelo número de sequência" : "Canal autenticado"}</small></div></div><button className="ghost-button" onClick={() => void logout().then(() => setAuthenticated(false))}>Sair</button></div></header>
    <nav aria-label="Seções do painel">{pages.map((item) => <button key={item.id} className={page === item.id ? "active" : ""} aria-current={page === item.id ? "page" : undefined} onClick={() => setPage(item.id)}>{item.label}</button>)}</nav>
    <main id="content" tabIndex={-1}>{error && <div className="alert" role="alert">{error}<button onClick={() => void refreshStations()}>Tentar novamente</button></div>}{station && page === "home" && <HomePage station={station} refreshKey={refreshKey} />}{station && page === "charts" && <ChartsPage station={station} refreshKey={refreshKey} />}{page === "lighting" && <LightingPage refreshKey={refreshKey} />}{station && page === "operation" && <OperationPage station={station} refreshKey={refreshKey} />}{station && page === "calibration" && <CalibrationPage station={station} refreshKey={refreshKey} />}{station && page === "alarms" && <AlarmsPage station={station} refreshKey={refreshKey} />}{page === "help" && <HelpPage />}{!station && page !== "lighting" && page !== "help" && <section className="empty"><h2>Nenhuma estação cadastrada</h2><p>Cadastre a estação no banco antes de habilitar a operação.</p></section>}</main>
  </div>;
}

createRoot(document.getElementById("root")!).render(<App />);
if ("serviceWorker" in navigator) window.addEventListener("load", () => void navigator.serviceWorker.register("/service-worker.js"));
