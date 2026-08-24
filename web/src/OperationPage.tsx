import { FormEvent, useEffect, useState } from "react";
import { BatchRun, IrrigationWindow, loadBatchRuns, loadIrrigation, loadRecipes, loadSetpoints, Recipe, saveIrrigation, saveRecipe, saveSetpoints, sendCommand, Setpoints, Station } from "./api";

const initialSetpoints: Setpoints = { ph: 5.8, ecMsCm: 1.8, airTemperatureC: 25, humidityPercent: 65, vpdKpa: 1.1 };
const emptyWindow = (index: number): IrrigationWindow => ({ windowId: `window_${index + 1}`, startTime: "08:00", durationSeconds: 90, weekdays: [0, 1, 2, 3, 4, 5, 6], enabled: false });

export function OperationPage({ station, refreshKey }: { station: Station; refreshKey: number }) {
  const [setpoints, setSetpoints] = useState(initialSetpoints);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [windows, setWindows] = useState<IrrigationWindow[]>(Array.from({ length: 5 }, (_, index) => emptyWindow(index)));
  const [runs, setRuns] = useState<BatchRun[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [recipeDraft, setRecipeDraft] = useState({ recipeId: "vegetative", name: "Vegetativo", batchLiters: 20, targetPh: 5.8, targetEcMsCm: 1.8, volumes: [20, 20, 20, 20] });
  useEffect(() => {
    Promise.all([loadSetpoints(station.stationId), loadRecipes(station.stationId), loadIrrigation(station.stationId), loadBatchRuns(station.stationId)])
      .then(([points, recipeResponse, irrigation, batchResponse]) => {
        setSetpoints(points); setRecipes(recipeResponse.recipes); setRuns(batchResponse.runs);
        setWindows(Array.from({ length: 5 }, (_, index) => irrigation.windows[index] ?? emptyWindow(index)));
        setSelectedRecipe((current) => current || recipeResponse.recipes[0]?.recipeId || "");
      }).catch((reason: Error) => setMessage(reason.message));
  }, [station.stationId, refreshKey]);

  const updatePoint = (field: keyof Setpoints, value: string) => setSetpoints((current) => ({ ...current, [field]: Number(value) }));
  async function submitSetpoints(event: FormEvent) { event.preventDefault(); try { setSetpoints(await saveSetpoints(station.stationId, setpoints)); setMessage("Setpoints validados e salvos."); } catch (reason) { setMessage((reason as Error).message); } }
  async function submitRecipe(event: FormEvent) {
    event.preventDefault();
    const steps = recipeDraft.volumes.map((volumeMl, index) => ({ channel: index + 1, volumeMl, order: index + 1 })).filter((step) => step.volumeMl > 0);
    const recipe: Recipe = { ...recipeDraft, steps };
    try { await saveRecipe(station.stationId, recipe); setRecipes((current) => [...current.filter((item) => item.recipeId !== recipe.recipeId), recipe]); setSelectedRecipe(recipe.recipeId); setMessage("Receita salva. Nenhuma bomba foi acionada."); } catch (reason) { setMessage((reason as Error).message); }
  }
  async function submitIrrigation() { try { const response = await saveIrrigation(station.stationId, windows); setMessage(`${response.saved} agendas salvas. A execução ainda depende dos intertravamentos locais.`); } catch (reason) { setMessage((reason as Error).message); } }
  async function startBatch() { if (!confirmed || !selectedRecipe) return; try { const response = await sendCommand(station.stationId, "start_batch", selectedRecipe); setMessage(`${response.status}: ${response.explanation}`); setConfirmed(false); const latest = await loadBatchRuns(station.stationId); setRuns(latest.runs); } catch (reason) { setMessage((reason as Error).message); } }

  return <><section className="page-heading"><div><p className="eyebrow">Operação supervisionada</p><h2>Receita, batelada e irrigação</h2></div></section><p className="page-note">Salvar configurações não aciona saídas. “Iniciar” cria um comando e aguarda ACK/NACK do ESP32.</p>
    <section className="split-grid operation-grid"><form className="panel-card form-grid" onSubmit={(event) => void submitSetpoints(event)}><h3>Metas ambientais</h3>{([ ["ph", "pH"], ["ecMsCm", "EC (mS/cm)"], ["airTemperatureC", "Temperatura (°C)"], ["humidityPercent", "UR (%)"], ["vpdKpa", "VPD (kPa)"] ] as [keyof Setpoints, string][]).map(([field, label]) => <label key={field}>{label}<input type="number" step="0.01" value={setpoints[field]} onChange={(event) => updatePoint(field, event.target.value)} /></label>)}<button>Salvar metas</button></form>
    <form className="panel-card form-grid" onSubmit={(event) => void submitRecipe(event)}><h3>Receita de nutrientes</h3><label>ID estável<input value={recipeDraft.recipeId} pattern="[a-z][a-z0-9_-]*" onChange={(event) => setRecipeDraft({ ...recipeDraft, recipeId: event.target.value })} /></label><label>Nome<input value={recipeDraft.name} onChange={(event) => setRecipeDraft({ ...recipeDraft, name: event.target.value })} /></label><label>Volume da batelada (L)<input type="number" min="1" max="50" value={recipeDraft.batchLiters} onChange={(event) => setRecipeDraft({ ...recipeDraft, batchLiters: Number(event.target.value) })} /></label><div className="dose-grid">{["CalMag", "Micro", "Bloom", "Grow"].map((label, index) => <label key={label}>{label} (mL)<input type="number" min="0" max="500" value={recipeDraft.volumes[index]} onChange={(event) => { const volumes = [...recipeDraft.volumes]; volumes[index] = Number(event.target.value); setRecipeDraft({ ...recipeDraft, volumes }); }} /></label>)}</div><button>Salvar receita</button></form></section>
    <section className="panel-card schedule-panel"><div className="section-line"><div><h3>Até cinco irrigações diárias</h3><p>Horários locais; duração limitada a 30–600 segundos.</p></div><button onClick={() => void submitIrrigation()}>Salvar agendas</button></div><div className="irrigation-grid">{windows.map((window, index) => <fieldset key={window.windowId}><legend>Agenda {index + 1}</legend><label><input type="checkbox" checked={window.enabled} onChange={(event) => setWindows((current) => current.map((item, position) => position === index ? { ...item, enabled: event.target.checked } : item))} /> Ativa</label><label>Início<input type="time" value={window.startTime} onChange={(event) => setWindows((current) => current.map((item, position) => position === index ? { ...item, startTime: event.target.value } : item))} /></label><label>Duração (s)<input type="number" min="30" max="600" value={window.durationSeconds} onChange={(event) => setWindows((current) => current.map((item, position) => position === index ? { ...item, durationSeconds: Number(event.target.value) } : item))} /></label></fieldset>)}</div></section>
    <section className="split-grid"><article className="panel-card"><h3>Iniciar batelada</h3><label className="form-label">Receita<select value={selectedRecipe} onChange={(event) => setSelectedRecipe(event.target.value)}><option value="">Selecione</option>{recipes.map((recipe) => <option value={recipe.recipeId} key={recipe.recipeId}>{recipe.name} · {recipe.batchLiters} L</option>)}</select></label><label className="confirmation"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} /> Conferi água, estoques, dreno e ausência de vazamento.</label><button disabled={!confirmed || !selectedRecipe} onClick={() => void startBatch()}>Enviar início e aguardar ACK</button></article><article className="panel-card"><h3>Progresso das bateladas</h3>{runs.length === 0 ? <p className="no-inline-data">Nenhuma batelada registrada.</p> : <ul className="plain-list">{runs.map((run) => <li key={run.batchId}><span><strong>{run.recipeId}: {run.status}</strong><small>{run.currentStep} · {run.progressPercent.toFixed(0)}% · {new Date(run.startedAt).toLocaleString("pt-BR")}</small></span></li>)}</ul>}</article></section>
    {message && <p className="message sticky-message" role="status">{message}</p>}
  </>;
}
