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
export function loadLighting(): Promise<{ channels: RemoteLight[]; reconciledAt: string | null }> {
  return request("/api/v1/lighting");
}
export function saveSchedule(entityId: string, schedule: LightSchedule): Promise<RemoteLight> {
  return request(`/api/v1/lighting/${encodeURIComponent(entityId)}/schedule`, { method: "PUT", body: JSON.stringify(schedule) });
}
export function setOverride(entityId: string, state: LightState | null, durationMinutes = 30): Promise<RemoteLight> {
  return request(`/api/v1/lighting/${encodeURIComponent(entityId)}/override`, { method: "POST", body: JSON.stringify({ state, durationMinutes }) });
}
