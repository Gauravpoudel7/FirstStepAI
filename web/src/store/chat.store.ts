import { create } from "zustand";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Array<{ doc_id: string; title: string; chunk_id?: string }>;
  feedback?: "up" | "down" | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatState {
  activeConversationId: string | null;
  messages: ChatMessage[];
  streaming: boolean;
  sources: Array<{ doc_id: string; title: string }>;
  setActiveConversationId: (id: string | null) => void;
  reset: () => void;
  startUserMessage: (msg: ChatMessage) => void;
  appendToken: (text: string) => void;
  setSources: (sources: ChatState["sources"]) => void;
  finalizeAssistant: (msg: ChatMessage) => void;
  setMessages: (m: ChatMessage[]) => void;
  setStreaming: (s: boolean) => void;
  failStream: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  activeConversationId: null,
  messages: [],
  streaming: false,
  sources: [],
  setActiveConversationId: (id) => set({ activeConversationId: id }),
  reset: () =>
    set({
      activeConversationId: null,
      messages: [],
      streaming: false,
      sources: [],
    }),
  startUserMessage: (msg) =>
    set((s) => ({
      messages: [...s.messages, msg],
      streaming: true,
      sources: [],
    })),
  appendToken: (text) =>
    set((s) => {
      const messages = [...s.messages];
      const last = messages[messages.length - 1];
      if (last && last.role === "assistant") {
        messages[messages.length - 1] = {
          ...last,
          content: last.content + text,
        };
      } else {
        messages.push({
          id: crypto.randomUUID(),
          role: "assistant",
          content: text,
          created_at: new Date().toISOString(),
        });
      }
      return { messages };
    }),
  setSources: (sources) => set({ sources }),
  finalizeAssistant: (msg) =>
    set((s) => {
      // Stamp the server-returned id/conversation onto the trailing assistant
      // bubble (the one `appendToken` created and grew during streaming).
      // Matching by `msg.id` here used to fail because the streamed bubble's
      // id was generated inside `appendToken` via `crypto.randomUUID()` while
      // `msg.id` came from a render-time capture — so the lookup missed and
      // the store pushed a duplicate. Index-based finalize is robust to that
      // and to StrictMode double-invokes that race a second finalize against
      // the same trailing bubble.
      const messages = [...s.messages];
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === "assistant") {
          messages[i] = { ...messages[i], ...msg };
          return { messages, streaming: false };
        }
      }
      // No streaming bubble to stamp (e.g. `done` fired before any token) —
      // push the server message as-is so the assistant still shows.
      messages.push(msg);
      return { messages, streaming: false };
    }),
  setMessages: (m) => set({ messages: m }),
  setStreaming: (streaming) => set({ streaming }),
  failStream: () => set({ streaming: false }),
}));