/** Parse an SSE text/event-stream response into a stream of {event, data}. */
export interface SSEEvent {
  event: string;
  data: string;
}

export async function* parseSSE(
  response: Response,
): AsyncGenerator<SSEEvent, void, void> {
  if (!response.body) return;
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const parsed = parseFrame(frame);
      if (parsed) yield parsed;
    }
  }

  if (buffer.trim()) {
    const parsed = parseFrame(buffer);
    if (parsed) yield parsed;
  }
}

function parseFrame(raw: string): SSEEvent | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (!line) continue;
    if (line.startsWith(":")) continue; // comment
    const colon = line.indexOf(":");
    if (colon === -1) continue;
    const field = line.slice(0, colon).trim();
    let value = line.slice(colon + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    else if (field === "data") dataLines.push(value);
  }
  if (!dataLines.length) return null;
  return { event, data: dataLines.join("\n") };
}