import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, StopCircle, Sparkles, Loader2 } from "lucide-react";
import { useAuthStore } from "@/store/auth.store";
import { useChatStore, type ChatMessage } from "@/store/chat.store";
import { useChatStream } from "@/hooks/use-chat-stream";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { firstName, cn } from "@/lib/utils";
import { RoleBadge } from "@/components/layout/RoleBadge";

const SUGGESTIONS: Record<string, string[]> = {
  admin: [
    "What is our current leave policy?",
    "Summarize our security incident response plan.",
    "How many days of vacation do I have?",
  ],
  hr: [
    "What's the onboarding checklist for a new hire?",
    "How many vacation days do employees get?",
    "What does the diversity policy say?",
  ],
  manager: [
    "What are my active projects?",
    "How do I request new equipment for my team?",
    "Tell me about the R&D budget policy.",
  ],
  employee: [
    "How many days of vacation do I have left?",
    "What's the policy on remote work?",
    "Where can I find the security training?",
  ],
};

export default function ChatPage() {
  const user = useAuthStore((s) => s.user);
  const role = (user?.role ?? "employee") as keyof typeof SUGGESTIONS;
  const suggestions = SUGGESTIONS[role] ?? SUGGESTIONS.employee;

  // Chat state lives in the store now so it survives navigation away from
  // /chat and so the TopBar reset button (3.8) can clear it. Previously
  // ChatPage owned local useState, which meant the buffer was lost on every
  // route change and "Reset conversation" silently did nothing visible.
  const messages = useChatStore((s) => s.messages);
  const sources = useChatStore((s) => s.sources);
  const streaming = useChatStore((s) => s.streaming);
  const activeConversationId = useChatStore((s) => s.activeConversationId);
  const startUserMessage = useChatStore((s) => s.startUserMessage);
  const appendToken = useChatStore((s) => s.appendToken);
  const setSources = useChatStore((s) => s.setSources);
  const finalizeAssistant = useChatStore((s) => s.finalizeAssistant);
  const failStream = useChatStore((s) => s.failStream);
  const setStreaming = useChatStore((s) => s.setStreaming);

  const [input, setInput] = useState("");
  const { send, stop, error } = useChatStream();
  const setActiveConversationId = useChatStore((s) => s.setActiveConversationId);
  const listRef = useRef<HTMLDivElement | null>(null);
  // React 18 StrictMode double-invokes event handlers in dev. Without a guard,
  // a single click would push two user bubbles AND open two parallel SSE
  // streams. The hook now aborts any in-flight stream before starting a new
  // one (single-flight), but we still need to prevent the second `submit`
  // invocation from creating a duplicate user bubble.
  const submitInFlightRef = useRef(false);

  // Auto-scroll on new content
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  // The `onDone` callback in `submit` mirrors the conversation id into the
  // store as soon as the SSE `done` frame arrives — no separate useEffect
  // needed, and avoids racing against a stale render-time `returnedConvId`.

  // Whenever the stream returns its first sources frame, push them into the
  // store so the chat UI can render citation chips.
  useEffect(() => {
    if (sources.length) setSources(sources);
  }, [sources, setSources]);

  // Reflect stream state in the store so TopBar's reset can stop a stream.
  useEffect(() => {
    setStreaming(streaming);
  }, [streaming, setStreaming]);

  async function submit(text: string) {
    const trimmed = text.trim();
    if (!trimmed || streaming) return;
    // StrictMode guard — second invocation no-ops so we don't push a duplicate
    // user bubble. The hook's single-flight abort already prevents a duplicate
    // SSE stream; this guard is the matching protection for the user bubble.
    if (submitInFlightRef.current) return;
    submitInFlightRef.current = true;
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    startUserMessage(userMsg);
    setInput("");
    try {
      await send({
        message: trimmed,
        conversationId: activeConversationId,
        onToken: (text) => appendToken(text),
        // Stamp the streaming bubble with the *real* server ids as soon as
        // the SSE `done` frame arrives. Doing this inside the hook's
        // `onDone` callback (instead of after `await send` resolves) means
        // we don't rely on a stale render-time `messageId` capture, which
        // used to be `null` here — pushing a duplicate assistant bubble.
        onDone: ({ conversationId, messageId }) => {
          const current = useChatStore.getState().messages;
          const last = current[current.length - 1];
          finalizeAssistant({
            id: messageId ?? last?.id ?? `a-${Date.now()}`,
            role: "assistant",
            content: last?.content ?? "",
            sources: useChatStore.getState().sources,
            created_at: last?.created_at ?? new Date().toISOString(),
          });
          // Mirror the conversation id into the store so the next submit
          // continues the same conversation.
          if (conversationId) {
            setActiveConversationId(conversationId);
          }
        },
      });
    } finally {
      submitInFlightRef.current = false;
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    submit(input);
  }

  return (
    <div className="flex h-[calc(100vh-6rem)] flex-col gap-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold">
            <Sparkles className="h-5 w-5 text-primary" /> AI Chat
          </h1>
          <p className="text-sm text-muted-foreground">
            Ask anything about HR policies, projects, or your profile.
          </p>
        </div>
        <RoleBadge role={role} />
      </header>

      <Card className="flex-1 overflow-hidden glass">
        <div ref={listRef} className="h-full overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="grid h-full place-items-center">
              <div className="max-w-md space-y-4 text-center">
                <Sparkles className="mx-auto h-8 w-8 text-primary" />
                <h2 className="text-lg font-semibold">
                  Welcome back, {firstName(user?.full_name)} 👋
                </h2>
                <p className="text-sm text-muted-foreground">
                  Ask anything — your responses are role-aware and grounded in
                  the documents available for your role.
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => submit(s)}
                      className="rounded-full border border-border bg-secondary/50 px-3 py-1 text-xs hover:bg-secondary"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          <AnimatePresence>
            {messages.map((m) => {
              const isStreaming = m.role === "assistant" && streaming;
              return (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "flex",
                    m.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  <div
                    className={cn(
                      "max-w-2xl rounded-2xl px-4 py-3 text-sm",
                      m.role === "user"
                        ? "bg-brand-gradient text-white rounded-tr-sm"
                        : "bg-card text-card-foreground border border-border rounded-tl-sm",
                    )}
                  >
                    <div className="whitespace-pre-wrap leading-relaxed">
                      {m.content || (isStreaming ? "" : " ")}
                    </div>
                    {isStreaming && (
                      <span className="mt-1 inline-flex items-center gap-1 text-xs opacity-70">
                        <Loader2 className="h-3 w-3 animate-spin" /> streaming…
                      </span>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {error && (
            <div className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
              {error}
            </div>
          )}
        </div>
      </Card>

      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={streaming}
          placeholder={
            streaming ? "Streaming response…" : "Ask the assistant anything…"
          }
          className="flex-1 rounded-xl border border-border bg-card/60 px-4 py-3 text-sm outline-none focus:border-primary"
        />
        {streaming ? (
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              stop();
              failStream();
            }}
          >
            <StopCircle className="mr-2 h-4 w-4" />
            Stop
          </Button>
        ) : (
          <Button type="submit" disabled={!input.trim()}>
            <Send className="mr-2 h-4 w-4" />
            Send
          </Button>
        )}
      </form>
    </div>
  );
}