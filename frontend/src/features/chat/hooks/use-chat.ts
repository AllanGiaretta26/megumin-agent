"use client";

import { useCallback, useEffect, useState } from "react";
import { createSession, sendMessage } from "../api";
import type { ChatMessage } from "../types";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeMode, setActiveMode] = useState<string>("study");

  // Cria sessão automaticamente ao montar
  useEffect(() => {
    createSession()
      .then(({ session_id }) => setSessionId(session_id))
      .catch(console.error);
  }, []);

  const sendUserMessage = useCallback(
    async (content: string) => {
      if (isLoading || !content.trim()) return;

      // Adiciona mensagem do usuário otimisticamente
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const response = await sendMessage({
          message: content,
          session_id: sessionId,
          mode: activeMode,
        });

        if (response.session_id !== sessionId) {
          setSessionId(response.session_id);
        }

        const agentMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.response,
        };
        setMessages((prev) => [...prev, agentMsg]);
      } catch (err) {
        const errMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `⚠️ Não consegui alcançar o servidor. Verifique se o backend está rodando.\n\`\`\`\n${err instanceof Error ? err.message : String(err)}\n\`\`\``,
        };
        setMessages((prev) => [...prev, errMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, sessionId, activeMode]
  );

  const startNewConversation = useCallback(async () => {
    try {
      const { session_id } = await createSession();
      setSessionId(session_id);
      setMessages([]);
    } catch (err) {
      console.error("Falha ao criar nova sessão:", err);
    }
  }, []);

  return {
    messages,
    sessionId,
    isLoading,
    activeMode,
    sendMessage: sendUserMessage,
    startNewConversation,
    setMode: setActiveMode,
  };
}
