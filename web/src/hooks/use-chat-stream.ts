import { useCallback, useRef, useState } from "react";
import axios from "axios";
import { parseSSE } from "@/lib/sse";

export interface ChatStreamSource {
  doc_id: string;
  title: string;
  chunk_id?: string;
}

export interface ChatStreamState {
  streaming: boolean;
  sources: ChatStreamSource[];
  error: string | null;
  conversationId: string | null;
  messageId: string | null;
}

// Mirrors the env-aware base path used in `lib/api.ts` so the SSE fetch and
// the axios refresh call land on the same backend origin.
const envBase = import.meta.env.VITE_API_BASE_URL;
const baseURL = envBase && envBase !== "/api/v1" ? envBase : "/api/v1";

async function refreshAccessCookie(): Promise<void> {
  await axios.post(`${baseURL}/auth/refresh`, null, { withCredentials: true });
}

async function postChatMessage(
  body: object,
  signal: AbortSignal,
): Promise<Response> {
  return fetch(`${baseURL}/chat/message`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
    signal,
  });
}

export function useChatStream() {
  const [state, setState] = useState<ChatStreamState>({
    streaming: false,
    sources: [],
    error: null,
    conversationId: null,
    messageId: null,
  });
  const controllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setState({
      streaming: false,
      sources: [],
      error: null,
      conversationId: null,
      messageId: null,
    });
  }, []);

  const send = useCallback(
    async (params: {
      message: string;
      conversationId?: string | null;
      onToken: (text: string) => void;
      // Fires on the SSE `done` frame with the server-returned ids. Callers
      // finalize the streaming bubble from here so they use the *real* id,
      // not a render-time capture (which used to be `null` because the hook's
      // `messageId` state hadn't updated yet — leading to a duplicated
      // assistant bubble in chat.store).
      onDone?: (info: {
        conversationId: string | null;
        messageId: string | null;
      }) => void;
    }) => {
      // Single-flight: abort any in-flight stream before starting a new one.
      // This makes React 18 StrictMode's double-invoke of the submit handler
      // safe — the second invocation aborts the first's controller before
      // opening a new POST, so we never get two parallel SSE connections
      // racing into the same store.
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setState((s) => ({
        ...s,
        streaming: true,
        sources: [],
        error: null,
      }));

      const payload = {
        message: params.message,
        conversation_id: params.conversationId ?? null,
        stream: true,
      };

      try {
        // Use fetch directly — axios + responseType:"stream" emits a deprecation
        // warning in browsers (XHR has no "stream" enum) and the stream never
        // reaches the page.
        let res = await postChatMessage(payload, controller.signal);

        // The SSE stream bypasses axios, so the refresh interceptor in
        // `lib/api.ts` doesn't see its 401s. Detect the access-cookie
        // expiry once at the start of the stream, refresh, and retry — once.
        // Mid-stream 401s are not recoverable because we can't rewind a
        // partially-consumed event stream.
        if (res.status === 401) {
          try {
            await refreshAccessCookie();
          } catch {
            // Refresh itself failed — let the user see the original 401.
            throw new Error("Session expired");
          }
          res = await postChatMessage(payload, controller.signal);
        }

        if (!res.ok || !res.body) {
          // Try to surface the FastAPI "detail" message.
          let detail = `Request failed with status code ${res.status}`;
          try {
            const j = await res.json();
            if (j?.detail) detail = String(j.detail);
          } catch {
            // ignore
          }
          throw new Error(detail);
        }

        for await (const frame of parseSSE(res as unknown as Response)) {
          let data: any;
          try {
            data = JSON.parse(frame.data);
          } catch {
            data = frame.data;
          }
          if (frame.event === "sources") {
            setState((s) => ({ ...s, sources: data as ChatStreamSource[] }));
          } else if (frame.event === "token") {
            params.onToken((data && data.text) || "");
          } else if (frame.event === "done") {
            const conversationId = data?.conversation_id ?? null;
            const messageId = data?.message_id ?? null;
            setState((s) => ({
              ...s,
              streaming: false,
              conversationId,
              messageId,
            }));
            // Surface the ids to the caller so it can finalize the streaming
            // bubble with the *actual* server ids, not a stale closure capture.
            params.onDone?.({ conversationId, messageId });
          } else if (frame.event === "error") {
            setState((s) => ({
              ...s,
              streaming: false,
              error: data?.message ?? "Chat error",
            }));
          }
        }
      } catch (err: any) {
        if (err?.name === "AbortError") return;
        setState((s) => ({
          ...s,
          streaming: false,
          error: err?.response?.data?.detail ?? err?.message ?? "Chat error",
        }));
      }
    },
    [],
  );

  const stop = useCallback(() => {
    controllerRef.current?.abort();
    setState((s) => ({ ...s, streaming: false }));
  }, []);

  return { ...state, send, stop, reset };
}