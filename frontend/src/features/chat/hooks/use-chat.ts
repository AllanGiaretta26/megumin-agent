"use client";

import { AGENT_MODES } from "@/features/modes/constants";
import { useCallback, useEffect, useRef, useState } from "react";
import { createSession, sendMessage, streamMessage } from "../api";
import type { ChatMessage } from "../types";

interface UseChatOptions {
  projectPath?: string | null;
}

export function useChat({ projectPath }: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeMode, setActiveMode] = useState<string>("free_chat");
  const abortRef = useRef<AbortController | null>(null);

  // Cria sessão automaticamente ao montar
  useEffect(() => {
    createSession()
      .then(({ session_id }) => setSessionId(session_id))
      .catch(console.error);
  }, []);

  const sendUserMessage = useCallback(
    async (content: string) => {
      if (isLoading || !content.trim()) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);

      // Aviso inline se modo requer project_path e ele não está configurado
      const modeConfig = AGENT_MODES.find((m) => m.id === activeMode);
      if (modeConfig?.requiresProjectPath && !projectPath) {
        const warnMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "⚠️ Este modo precisa de um projeto configurado. Acesse **Configurações** para definir o caminho.",
        };
        setMessages((prev) => [...prev, warnMsg]);
        return;
      }

      setIsLoading(true);

      const agentMsgId = crypto.randomUUID();
      // Adiciona placeholder de streaming imediatamente
      setMessages((prev) => [
        ...prev,
        { id: agentMsgId, role: "assistant", content: "", isStreaming: true },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const gen = streamMessage(
          { message: content, session_id: sessionId, mode: activeMode, project_path: projectPath ?? null },
          controller.signal
        );

        for await (const event of gen) {
          if (event.type === "token") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId ? { ...m, content: m.content + event.content } : m
              )
            );
          } else if (event.type === "tool_call" || event.type === "tool_result") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId
                  ? {
                      ...m,
                      toolCalls: [
                        ...(m.toolCalls ?? []),
                        {
                          tool: event.tool,
                          args: event.args,
                          output: event.output,
                          status: event.status,
                        },
                      ],
                    }
                  : m
              )
            );
          } else if (event.type === "done") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId ? { ...m, isStreaming: false } : m
              )
            );
            if (event.session_id !== sessionId) {
              setSessionId(event.session_id);
            }
          } else if (event.type === "error") {
            throw new Error(event.message);
          }
        }

        // Segurança: se o stream terminou sem evento "done" (queda de rede, etc),
        // garante que o cursor não fique preso piscando indefinidamente.
        setMessages((prev) =>
          prev.map((m) =>
            m.id === agentMsgId && m.isStreaming ? { ...m, isStreaming: false } : m
          )
        );
      } catch (err) {
        const isAbort = err instanceof Error && err.name === "AbortError";

        if (isAbort) {
          // Stream cancelado — mantém conteúdo parcial, só fecha o streaming
          setMessages((prev) =>
            prev.map((m) =>
              m.id === agentMsgId ? { ...m, isStreaming: false } : m
            )
          );
        } else {
          // Erro real — tenta fallback com POST /chat normal
          try {
            const response = await sendMessage({
              message: content,
              session_id: sessionId,
              mode: activeMode,
              project_path: projectPath ?? null,
            });
            if (response.session_id !== sessionId) setSessionId(response.session_id);
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId
                  ? { ...m, content: response.response, isStreaming: false }
                  : m
              )
            );
          } catch {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId
                  ? {
                      ...m,
                      content: `⚠️ Não consegui alcançar o servidor. Verifique se o backend está rodando.\n\`\`\`\n${err instanceof Error ? err.message : String(err)}\n\`\`\``,
                      isStreaming: false,
                    }
                  : m
              )
            );
          }
        }
      } finally {
        setIsLoading(false);
        abortRef.current = null;
      }
    },
    [isLoading, sessionId, activeMode, projectPath]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const startNewConversation = useCallback(async () => {
    abortRef.current?.abort();
    try {
      const { session_id } = await createSession();
      setSessionId(session_id);
      setMessages([]);
    } catch (err) {
      console.error("Falha ao criar nova sessão:", err);
    }
  }, []);

  const isStreaming = messages.some((m) => m.isStreaming);

  return {
    messages,
    sessionId,
    isLoading,
    isStreaming,
    activeMode,
    sendMessage: sendUserMessage,
    stopStreaming,
    startNewConversation,
    setMode: setActiveMode,
  };
}
