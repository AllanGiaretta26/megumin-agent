"use client";

import { Badge } from "@/components/ui/badge";
import { useEffect, useRef } from "react";
import { AGENT_MODES } from "../../modes/constants";
import type { ChatMessage as ChatMessageType } from "../types";
import { ChatMessage, LoadingBubble } from "./chat-message";

interface ChatContainerProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  activeMode: string;
}

function WelcomeScreen({ activeMode }: { activeMode: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-8 text-center">
      <div
        className="text-6xl select-none"
        style={{ filter: "drop-shadow(0 0 20px rgba(124,58,237,0.6))" }}
      >
        🧙‍♀️
      </div>

      <div>
        <h1
          className="text-3xl font-bold text-megumin-text-primary"
          style={{ fontFamily: "serif" }}
        >
          Megumin
        </h1>
        <p className="text-sm text-megumin-primary mt-1 font-medium">
          Arch-wizard · Crimson Demon
        </p>
      </div>

      <p className="text-sm text-megumin-text-secondary max-w-sm">
        Assistente de programação pronto para invocar soluções. Selecione um
        modo e envie sua primeira mensagem.
      </p>

      <div className="flex flex-wrap gap-2 justify-center max-w-xs">
        {AGENT_MODES.map((mode) => (
          <Badge
            key={mode.id}
            variant="outline"
            className={
              mode.id === activeMode
                ? "border-megumin-primary text-megumin-primary bg-megumin-primary/10"
                : "border-megumin-border text-megumin-text-muted"
            }
          >
            {mode.label}
          </Badge>
        ))}
      </div>
    </div>
  );
}

export function ChatContainer({
  messages,
  isLoading,
  activeMode,
}: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll ao final quando novas mensagens chegam
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return <WelcomeScreen activeMode={activeMode} />;
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      {isLoading && <LoadingBubble />}
      <div ref={bottomRef} />
    </div>
  );
}
