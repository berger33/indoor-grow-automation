export type LightState = "on" | "off";
export type LightStatus = "confirmed" | "divergent" | "unavailable";
export type Health = "healthy" | "degraded" | "failed";

export interface LightSchedule {
  onTime: string;
  offTime: string;
  weekdays: number[];
  timezone: string;
  enabled: boolean;
}

export interface LightOverride { state: LightState; expiresAt: string; }
export interface RemoteLight {
  entityId: string;
  label: string;
  desired: LightState;
  observed: LightState | null;
  status: LightStatus;
  source: "schedule" | "manual_override";
  schedule: LightSchedule;
  override: LightOverride | null;
  explanation: string;
}

export interface Station { stationId: string; name: string; timezone: string; health: Health; }
export interface SensorView {
  sensorId: string;
  label: string;
  value: number | null;
  unit: string | null;
  quality: string;
  ageSeconds: number | null;
  maximumAgeSeconds: number;
  health: Health;
  errorCode: string | null;
}
export interface HistorySample {
  sensorId: string;
  kind: string;
  value: number;
  unit: string;
  quality: string;
  observedAt: string;
}
export interface Setpoints { ph: number; ecMsCm: number; airTemperatureC: number; humidityPercent: number; vpdKpa: number; }
export interface RecipeStep { channel: number; volumeMl: number; order: number; }
export interface Recipe { recipeId: string; name: string; batchLiters: number; targetPh: number; targetEcMsCm: number; steps: RecipeStep[]; }
export interface IrrigationWindow { windowId: string; startTime: string; durationSeconds: number; weekdays: number[]; enabled: boolean; }
export interface BatchRun { batchId: string; recipeId: string; status: string; currentStep: string; progressPercent: number; startedAt: string; finishedAt: string | null; failureCode: string | null; }
export interface CalibrationRecord { calibrationId: string; deviceId: string; kind: string; coefficients: Record<string, unknown>; status: string; calibratedAt: string; calibratedBy: string; }
export interface Alarm { alarmId: string; code: string; severity: string; cause: string; procedure: string; raisedAt: string; latched: boolean; acknowledgedAt: string | null; acknowledgedBy: string | null; }

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) { super(message); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    let detail = `Grow Hub respondeu ${response.status}`;
    try {
      const payload = await response.json() as { detail?: string };
      if (payload.detail) detail = payload.detail;
    } catch { /* resposta sem JSON */ }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function login(userId: string, password: string): Promise<{ userId: string; displayName: string; role: string }> {
  return request("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ userId, password }) });
}
export function logout(): Promise<void> { return request("/api/v1/auth/logout", { method: "POST" }); }
export function loadStations(): Promise<{ stations: Station[] }> { return request("/api/v1/stations"); }
export function loadSensors(stationId: string): Promise<{ stationId: string; sensors: SensorView[] }> {
  return request(`/api/v1/stations/${encodeURIComponent(stationId)}/sensors`);
}
export function loadHistory(stationId: string, hours = 24): Promise<{ stationId: string; samples: HistorySample[] }> {
  return request(`/api/v1/stations/${encodeURIComponent(stationId)}/history?hours=${hours}`);
}
export function loadSetpoints(stationId: string): Promise<Setpoints> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/setpoints`); }
export function saveSetpoints(stationId: string, value: Setpoints): Promise<Setpoints> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/setpoints`, { method: "PUT", body: JSON.stringify(value) }); }
export function loadRecipes(stationId: string): Promise<{ recipes: Recipe[] }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/recipes`); }
export function saveRecipe(stationId: string, value: Recipe): Promise<{ recipeId: string; status: string }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/recipes`, { method: "POST", body: JSON.stringify(value) }); }
export function loadIrrigation(stationId: string): Promise<{ windows: IrrigationWindow[] }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/irrigation-schedules`); }
export function saveIrrigation(stationId: string, value: IrrigationWindow[]): Promise<{ saved: number }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/irrigation-schedules`, { method: "PUT", body: JSON.stringify(value) }); }
export function loadBatchRuns(stationId: string): Promise<{ runs: BatchRun[] }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/batch-runs`); }
export function sendCommand(stationId: string, action: string, target: string): Promise<{ auditId: string; status: string; explanation: string }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/commands`, { method: "POST", body: JSON.stringify({ action, target }) }); }
export function loadCalibrations(stationId: string): Promise<{ calibrations: CalibrationRecord[] }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/calibrations`); }
export function saveCalibration(stationId: string, payload: { deviceId: string; kind: string; measurements: Record<string, unknown> }): Promise<{ calibrationId: string; status: string; coefficients: Record<string, unknown>; explanation: string }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/calibrations`, { method: "POST", body: JSON.stringify(payload) }); }
export function loadAlarms(stationId: string): Promise<{ alarms: Alarm[] }> { return request(`/api/v1/stations/${encodeURIComponent(stationId)}/alarms`); }
export function acknowledgeAlarm(alarmId: string): Promise<{ alarmId: string; status: string }> { return request(`/api/v1/alarms/${encodeURIComponent(alarmId)}/ack`, { method: "POST" }); }
export function loadLighting(): Promise<{ channels: RemoteLight[]; reconciledAt: string | null }> {
  return request("/api/v1/lighting");
}
export function saveSchedule(entityId: string, schedule: LightSchedule): Promise<RemoteLight> {
  return request(`/api/v1/lighting/${encodeURIComponent(entityId)}/schedule`, { method: "PUT", body: JSON.stringify(schedule) });
}
export function setOverride(entityId: string, state: LightState | null, durationMinutes = 30): Promise<RemoteLight> {
  return request(`/api/v1/lighting/${encodeURIComponent(entityId)}/override`, { method: "POST", body: JSON.stringify({ state, durationMinutes }) });
}
