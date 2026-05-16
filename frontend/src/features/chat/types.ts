export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  output: string;
  status: "ok" | "error";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean; // true enquanto tokens ainda chegam do SSE
  toolCalls?: ToolCall[]; // ferramentas executadas durante esta resposta
}

export interface ChatRequest {
  message: string;
  session_id: string | null;
  mode: string;
  project_path?: string | null;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}
