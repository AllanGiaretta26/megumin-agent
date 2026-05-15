import { request } from "@/lib/api-client";
import type { ChatMessage, ChatRequest, ChatResponse } from "./types";

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createSession(): Promise<{ session_id: string }> {
  return request<{ session_id: string }>("/chat/new", { method: "POST" });
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
