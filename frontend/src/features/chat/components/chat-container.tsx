"use client";

import { Badge } from "@/components/ui/badge";
import type { AgentModeId } from "@/features/modes/types";
import Image from "next/image";
import { useEffect, useRef } from "react";
import { AGENT_MODES } from "../../modes/constants";
import type { ChatMessage as ChatMessageType } from "../types";
import { ChatMessage, LoadingBubble } from "./chat-message";

interface ChatContainerProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  isStreaming: boolean;
  activeMode: string;
  onModeChange: (mode: AgentModeId) => void;
  assistantName?: string;
}

function WelcomeScreen({
  activeMode,
  onModeChange,
}: {
  activeMode: string;
  onModeChange: (mode: AgentModeId) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-8 text-center">
      <div className="relative h-28 w-28 overflow-hidden rounded-full border border-megumin-primary/70 shadow-[0_0_42px_rgba(245,158,11,0.32)]">
        <Image
          src="/assets/megumin-profile.png"
          alt="Megumin"
          fill
          sizes="112px"
          className="object-cover"
          priority
        />
      </div>

      <div>
        <h1
          className="text-3xl font-bold text-megumin-text-primary tracking-wide"
          style={{ fontFamily: "serif" }}
        >
          Megumin
        </h1>
        <p className="text-sm text-megumin-primary mt-1 font-medium">
          Crimson Demon · Explosion Magic
        </p>
      </div>

      <p className="text-sm text-megumin-text-secondary max-w-sm">
        Assistente de programação pronto para canalizar foco, precisão e
        explosões controladas. Selecione um modo e envie sua primeira mensagem.
      </p>

      <div className="flex flex-wrap gap-2 justify-center max-w-xs">
        {AGENT_MODES.map((mode) => (
          <Badge
            key={mode.id}
            variant="outline"
            onClick={() => onModeChange(mode.id)}
            className={
              mode.id === activeMode
                ? "border-megumin-primary text-megumin-primary bg-megumin-primary/12 cursor-pointer hover:bg-megumin-primary/20 transition-colors"
                : "border-megumin-border text-megumin-text-muted cursor-pointer hover:border-megumin-primary hover:text-megumin-primary hover:bg-megumin-surface-raised transition-colors"
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
  isStreaming,
  activeMode,
  onModeChange,
  assistantName,
}: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll ao final quando novas mensagens chegam
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return <WelcomeScreen activeMode={activeMode} onModeChange={onModeChange} />;
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} assistantName={assistantName} />
      ))}
      {/* LoadingBubble só quando loading sem streaming ativo — streaming tem seu próprio cursor na mensagem */}
      {isLoading && !isStreaming && <LoadingBubble />}
      <div ref={bottomRef} />
    </div>
  );
}
