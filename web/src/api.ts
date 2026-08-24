export type LightState = "on" | "off";
export type LightStatus = "confirmed" | "divergent" | "unavailable";

export interface LightSchedule {
  onTime: string;
  offTime: string;
  weekdays: number[];
  timezone: string;
  enabled: boolean;
}

export interface LightOverride {
  state: LightState;
  expiresAt: string;
}

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

interface LightingResponse {
  channels: RemoteLight[];
  reconciledAt: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`Grow Hub respondeu ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function loadLighting(): Promise<LightingResponse> {
  return request<LightingResponse>("/api/v1/lighting");
}

export function saveSchedule(
  entityId: string,
  schedule: LightSchedule,
): Promise<RemoteLight> {
  return request<RemoteLight>(
    `/api/v1/lighting/${encodeURIComponent(entityId)}/schedule`,
    { method: "PUT", body: JSON.stringify(schedule) },
  );
}

export function setOverride(
  entityId: string,
  state: LightState | null,
  durationMinutes = 30,
): Promise<RemoteLight> {
  return request<RemoteLight>(
    `/api/v1/lighting/${encodeURIComponent(entityId)}/override`,
    { method: "POST", body: JSON.stringify({ state, durationMinutes }) },
  );
}
