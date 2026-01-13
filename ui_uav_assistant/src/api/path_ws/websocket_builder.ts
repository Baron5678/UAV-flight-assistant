import type { PathRequestDto } from "../path_http/dto";
import type { PathProgressEvent } from "./dto";

export interface StartPathProgressArgs {
  requestBody: PathRequestDto;                 // reused DTO
  onGeneration?: (msg: PathProgressEvent) => void;
  onFinal?: (msg: PathProgressEvent) => void;
  onError?: (err: string) => void;
  onDiagnostic?: (msg: PathProgressEvent) => void;
}

export function startPathProgressWS(args: StartPathProgressArgs): WebSocket {
  const ws = new WebSocket("ws://127.0.0.1:8000/ws/path_progress");

  ws.onopen = () => {
    ws.send(JSON.stringify(args.requestBody));
  };

  ws.onmessage = (event) => {
    let msg: any;
    try {
      msg = JSON.parse(event.data);
      console.log(msg)
    } catch {
      args.onError?.("WS parse error: non-JSON message received");
      return;
    }

    if (msg?.type === "generation") {
      args.onGeneration?.(msg);
      return;
    }

    if (msg?.type === "final") {
      args.onFinal?.(msg);
      ws.close();
      return;
    }
    if (msg?.type === "diagnostic") {
        args.onDiagnostic?.(msg);
        ws.close();
        return;
    }

    if (msg?.type === "error") {
      args.onError?.(String(msg.error ?? "Unknown WS error"));
      ws.close();
      return;
    }
  };

  ws.onerror = () => {
    args.onError?.("WebSocket error");
  };

  return ws;
}
