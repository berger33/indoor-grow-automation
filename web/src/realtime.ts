export type RealtimeStatus = "connecting" | "online" | "offline";

export function connectRealtime(onStatus: (status: RealtimeStatus) => void, onEvent: () => void): () => void {
  let closed = false;
  let socket: WebSocket | null = null;
  let retry = 1000;
  let timer: number | null = null;

  const open = () => {
    onStatus("connecting");
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const lastEventId = window.sessionStorage.getItem("growhubLastEventId") ?? "0";
    socket = new WebSocket(`${protocol}//${window.location.host}/api/v1/realtime?last_event_id=${lastEventId}`);
    socket.onopen = () => { retry = 1000; onStatus("online"); };
    socket.onmessage = (message) => {
      const event = JSON.parse(message.data) as { eventId?: number };
      if (event.eventId) window.sessionStorage.setItem("growhubLastEventId", String(event.eventId));
      onEvent();
    };
    socket.onclose = () => {
      if (closed) return;
      onStatus("offline");
      timer = window.setTimeout(open, retry);
      retry = Math.min(retry * 2, 30_000);
    };
    socket.onerror = () => socket?.close();
  };
  open();
  return () => {
    closed = true;
    if (timer !== null) window.clearTimeout(timer);
    socket?.close();
  };
}
