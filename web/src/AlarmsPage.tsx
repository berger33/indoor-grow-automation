import { useEffect, useState } from "react";
import { acknowledgeAlarm, Alarm, loadAlarms, Station } from "./api";

export function AlarmsPage({ station, refreshKey }: { station: Station; refreshKey: number }) {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const refresh = () => loadAlarms(station.stationId).then((response) => { setAlarms(response.alarms); setMessage(null); }).catch((reason: Error) => setMessage(reason.message));
  useEffect(() => { void refresh(); }, [station.stationId, refreshKey]);
  async function acknowledge(alarmId: string) {
    try { await acknowledgeAlarm(alarmId); setMessage("Alarme reconhecido. A causa e a trava de segurança não foram apagadas."); await refresh(); }
    catch (reason) { setMessage((reason as Error).message); }
  }
  const active = alarms.filter((alarm) => alarm.latched && !alarm.acknowledgedAt);
  return <><section className="page-heading"><div><p className="eyebrow">Central de alarmes retidos</p><h2>{active.length} alarme(s) aguardando ação</h2></div></section><p className="page-note">Reconhecer significa “li e assumo o atendimento”. Não rearma saída, não limpa vazamento e não confirma correção.</p><section className="alarm-list">{alarms.map((alarm) => <article className={`alarm-card alarm-${alarm.severity}`} key={alarm.alarmId}><div className="alarm-title"><div><span>{alarm.severity}</span><h3>{alarm.code}</h3></div><time dateTime={alarm.raisedAt}>{new Date(alarm.raisedAt).toLocaleString("pt-BR")}</time></div><dl><div><dt>Causa identificada</dt><dd>{alarm.cause}</dd></div><div><dt>Procedimento seguro</dt><dd>{alarm.procedure}</dd></div></dl>{alarm.acknowledgedAt ? <p className="acknowledged">Reconhecido por {alarm.acknowledgedBy} em {new Date(alarm.acknowledgedAt).toLocaleString("pt-BR")}</p> : <button onClick={() => void acknowledge(alarm.alarmId)}>Reconhecer sem limpar trava</button>}</article>)}{alarms.length === 0 && <div className="empty"><h3>Nenhum alarme registrado</h3><p>Isso não substitui a inspeção física antes de operar.</p></div>}</section>{message && <p className="message sticky-message" role="status">{message}</p>}</>;
}
