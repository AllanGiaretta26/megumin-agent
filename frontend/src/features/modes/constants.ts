import type { AgentMode } from "./types";

export const AGENT_MODES: AgentMode[] = [
  {
    id: "agent",
    label: "Agente",
    description: "Executa tarefas autonomamente",
    icon: "Zap",
    requiresProjectPath: true,
  },
  {
    id: "planning",
    label: "Planejamento",
    description: "Planeja antes de executar",
    icon: "ClipboardList",
    requiresProjectPath: true,
  },
  {
    id: "autonomous_edit",
    label: "Edição Autônoma",
    description: "Edita código sem aprovação",
    icon: "Pencil",
    requiresProjectPath: true,
  },
  {
    id: "questions",
    label: "Dúvidas",
    description: "Responde sobre o projeto",
    icon: "MessageCircle",
    requiresProjectPath: true,
  },
  {
    id: "free_chat",
    label: "Conversa Livre",
    description: "Chat geral com a Megumin",
    icon: "MessageSquare",
    requiresProjectPath: false,
  },
];
