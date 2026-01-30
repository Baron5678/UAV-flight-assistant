import {ResponseSuccessUAV, ResponseErrorUAV, ROUTES, RouteKey, SERVER_URL, Url} from "./entity";

export type ResponseUAV<T> = ResponseSuccessUAV<T> | ResponseErrorUAV;

async function parseBody<T>(text: string): Promise<T> {
  if (!text) return {} as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    return (text as unknown) as T;
  }
}

export function parseErrorBody(
  text: string,
  fallback?: string
): string {
  if (!text) {
    return fallback ?? "Unknown error";
  }

  try {
    const parsed = JSON.parse(text);

    if (parsed && typeof parsed === "object" && "detail" in parsed) {
      const detail = (parsed as any).detail;
      if (typeof detail === "string") {
        return detail;
      }
      if (Array.isArray(detail)) {
        return detail
          .map((e) => {
            const loc = Array.isArray(e.loc) ? e.loc.join(".") : "unknown";
            const msg = e.msg ?? "invalid value";
            return `${loc}: ${msg}`;
          })
          .join("; ");
      }
      return JSON.stringify(detail);
    }
  } catch {
    return "NOT JSON ERROR";
  }
  return text;
}

export async function make_request<TResponse, TRequestBody>(key: RouteKey,
                                                            body: TRequestBody,
                                                            pathParams?: Record<string, string | number>,
                                                            queryParams?: Record<string, string | number | undefined>)
    :Promise<ResponseUAV<TResponse>> {
    const route = ROUTES[key];

    let path = route.path;
    if (pathParams) {
        for (const [k, v] of Object.entries(pathParams)) {
            path = path.replaceAll(`{${k}}`, encodeURIComponent(String(v)));
        }
    }
    if (queryParams) {
        const qs = Object.entries(queryParams)
            .filter(([, v]) => v !== undefined)
            .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
            .join("&");

        if (qs.length > 0) {
            path += `?${qs}`;
        }
    }
    const url = `${SERVER_URL}${path}`;

    const init: RequestInit = {
        method: route.method,
        headers: { "Content-Type": "application/json" },
    };

    if (route.method !== "GET" && route.method !== "HEAD" && body !== undefined) {
        init.body = JSON.stringify(body);
    }

    const res = await fetch(url, init);
    const text = await res.text();

    if (res.ok) {
     const data= await parseBody<TResponse>(text);
     return {failed:false, http_status: res.status, body: data };
    }
    const message = parseErrorBody(text, res.statusText);
    return { failed:true, http_status: res.status, error: message };
}
