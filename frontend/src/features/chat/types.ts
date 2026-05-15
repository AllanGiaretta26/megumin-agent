export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
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
