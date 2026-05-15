"use client";

import { ChatContainer } from "@/features/chat/components/chat-container";
import { ChatInput } from "@/features/chat/components/chat-input";
import { useChat } from "@/features/chat/hooks/use-chat";
import { AGENT_MODES } from "@/features/modes/constants";
import { Menu } from "lucide-react";
import { useState } from "react";
import { Sidebar } from "./sidebar";

export function ChatLayout() {
  const { messages, sessionId, isLoading, activeMode, sendMessage, startNewConversation, setMode } = useChat();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const activeModeLabel =
    AGENT_MODES.find((m) => m.id === activeMode)?.label ?? activeMode;

  return (
    <div className="flex h-full overflow-hidden">
      <Sidebar
        activeMode={activeMode}
        onModeChange={setMode}
        onNewConversation={startNewConversation}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
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

          <div className="flex items-center gap-2 min-w-0">
            <span
              className="text-xs font-semibold uppercase tracking-wider text-megumin-text-muted"
            >
              Modo
            </span>
            <span
              className="text-sm font-medium text-megumin-primary"
            >
              {activeModeLabel}
            </span>
          </div>

          {sessionId && (
            <span className="ml-auto text-xs text-megumin-text-muted font-mono truncate max-w-32 hidden sm:block">
              {sessionId.slice(0, 8)}…
            </span>
          )}
        </header>

        {/* Mensagens */}
        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          activeMode={activeMode}
        />

        {/* Input */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
