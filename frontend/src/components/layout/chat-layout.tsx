"use client";

import { ChatContainer } from "@/features/chat/components/chat-container";
import { ChatInput } from "@/features/chat/components/chat-input";
import { useChat } from "@/features/chat/hooks/use-chat";
import { useConfig } from "@/features/config/hooks/use-config";
import { useOllamaStatus } from "@/features/config/hooks/use-ollama-status";
import { AGENT_MODES } from "@/features/modes/constants";
import type { AgentModeId } from "@/features/modes/types";
import { AlertTriangle, FolderOpen, Menu } from "lucide-react";
import { useEffect, useState } from "react";
import { Sidebar } from "./sidebar";

function truncatePath(path: string, maxLen = 32): string {
  if (path.length <= maxLen) return path;
  const parts = path.replace(/\\/g, "/").split("/");
  // Mostra início e final: C:/…/projeto
  return parts[0] + "/…/" + parts[parts.length - 1];
}

export function ChatLayout() {
  const { config } = useConfig();
  const { ollamaAvailable } = useOllamaStatus();
  const {
    messages,
    sessionId,
    isLoading,
    isStreaming,
    activeMode,
    sendMessage,
    stopStreaming,
    startNewConversation,
    setMode,
  } = useChat({ projectPath: config?.project_path ?? null });
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const activeModeConfig = AGENT_MODES.find((m) => m.id === activeMode);
  const activeModeLabel = activeModeConfig?.label ?? activeMode;
  const projectPath = config?.project_path ?? null;

  // Atalhos de teclado globais
  useEffect(() => {
    const modeKeys: Record<string, AgentModeId> = {
      "1": "agent",
      "2": "planning",
      "3": "autonomous_edit",
      "4": "questions",
      "5": "study",
    };
    const handler = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      if (!mod) return;
      if (e.key === "k") { e.preventDefault(); startNewConversation(); }
      if (modeKeys[e.key]) { e.preventDefault(); setMode(modeKeys[e.key]); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [startNewConversation, setMode]);

  return (
    <div className="flex h-full overflow-hidden">
      <Sidebar
        activeMode={activeMode}
        onModeChange={setMode}
        onNewConversation={startNewConversation}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        ollamaAvailable={ollamaAvailable}
      />

      {/* Área principal */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header da área de chat */}
        <header className="flex items-center gap-3 px-4 py-3 border-b border-megumin-border bg-megumin-surface">
          {/* Botão hamburguer mobile */}
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="text-megumin-text-muted hover:text-megumin-text-primary transition-colors md:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-2 min-w-0 flex-1 overflow-hidden">
            <span className="text-xs font-semibold uppercase tracking-wider text-megumin-text-muted shrink-0">
              Modo
            </span>
            <span className="text-sm font-medium text-megumin-primary shrink-0">
              {activeModeLabel}
            </span>

            {/* Indicador de project_path — só para modos que exigem */}
            {activeModeConfig?.requiresProjectPath && (
              <span className="flex items-center gap-1 text-xs min-w-0">
                <span className="text-megumin-text-muted shrink-0">•</span>
                {projectPath ? (
                  <>
                    <FolderOpen className="h-3 w-3 text-megumin-text-muted shrink-0" />
                    <span className="text-megumin-text-muted truncate" title={projectPath}>
                      {truncatePath(projectPath)}
                    </span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-3 w-3 text-amber-500 shrink-0" />
                    <span className="text-amber-500 shrink-0">Projeto não configurado</span>
                  </>
                )}
              </span>
            )}
          </div>

          {sessionId && (
            <span className="text-xs text-megumin-text-muted font-mono truncate max-w-20 hidden sm:block shrink-0">
              {sessionId.slice(0, 8)}…
            </span>
          )}
        </header>

        {/* Mensagens */}
        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          isStreaming={isStreaming}
          activeMode={activeMode}
          onModeChange={setMode}
        />

        {/* Input */}
        <ChatInput
          onSend={sendMessage}
          isLoading={isLoading}
          isStreaming={isStreaming}
          onStop={stopStreaming}
        />
      </div>
    </div>
  );
}
