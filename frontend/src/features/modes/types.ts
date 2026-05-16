export type AgentModeId =
  | "agent"
  | "planning"
  | "autonomous_edit"
  | "questions"
  | "free_chat";

export interface AgentMode {
  id: AgentModeId;
  label: string;
  description: string;
  icon: string; // nome do ícone lucide-react
  requiresProjectPath: boolean;
}
