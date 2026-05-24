import { request } from "@/lib/api-client";
import type { ChatMessage, ChatRequest, ChatResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type StreamEvent =
  | { type: "token"; content: string }
  | {
      type: "tool_call";
      tool: string;
      args: Record<string, unknown>;
      output: string;
      status: "ok" | "error";
    }
  | {
      type: "tool_result";
      tool: string;
      args: Record<string, unknown>;
      output: string;
      status: "ok" | "error";
    }
  | { type: "done"; session_id: string }
  | { type: "error"; message: string };

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createSession(): Promise<{ session_id: string }> {
  return request<{ session_id: string }>("/chat/new", { method: "POST" });
}

export async function* streamMessage(
  payload: ChatRequest,
  signal: AbortSignal
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${BASE_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok || !res.body) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail ?? `Erro ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop()!;
    for (const part of parts) {
      if (part.startsWith("data: ")) {
        yield JSON.parse(part.slice(6)) as StreamEvent;
      }
    }
  }
}

export async function getHistory(sessionId: string): Promise<ChatMessage[]> {
  const data = await request<{
    session_id: string;
    messages: { role: string; content: string }[];
  }>(`/chat/${sessionId}/history`);

  return data.messages.map((m) => ({
    id: crypto.randomUUID(),
    role: m.role as "user" | "assistant",
    content: m.content,
  }));
}
