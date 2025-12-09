export function startPathProgress({
  requestBody,    // same JSON you would send to POST /path (PathRequest)
  onGeneration,   // (msg) => void
  onFinal,        // (msg) => void
  onError,        // (err) => void
}) {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `ws://127.0.0.1:8000/ws/path_progress`;

  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    // first message: exactly the PathRequest JSON
    ws.send(JSON.stringify(requestBody));
  };

  ws.onmessage = (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (e) {
      console.error("WS parse error", e);
      return;
    }

    if (msg.type === "generation") {
      // per-generation update
      onGeneration && onGeneration(msg);
    } else if (msg.type === "final") {
      // final path + cost
      onFinal && onFinal(msg);
      ws.close();
    }
  };

  ws.onerror = (e) => {
    console.error("WS error", e);
    onError && onError(e);
  };

  ws.onclose = () => {
    // optional: notify UI about closed stream
  };

  return ws;
}