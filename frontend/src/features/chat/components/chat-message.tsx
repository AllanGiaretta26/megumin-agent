"use client";

import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import type { ChatMessage } from "../types";

interface ChatMessageProps {
  message: ChatMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 animate-fade-slide-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-megumin-user-bubble border border-megumin-border flex items-center justify-center text-sm font-medium text-megumin-text-secondary">
            U
          </div>
        ) : (
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
            style={{ boxShadow: "0 0 12px rgba(124,58,237,0.5)" }}
          >
            🧙‍♀️
          </div>
        )}
      </div>

      {/* Bubble */}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-megumin-user-bubble border border-megumin-primary/30 text-megumin-text-primary rounded-tr-sm"
            : "bg-megumin-agent-bubble border border-megumin-border text-megumin-text-primary rounded-tl-sm"
        )}
      >
        {!isUser && (
          <p className="text-xs font-medium text-megumin-primary mb-1">
            Megumin
          </p>
        )}

        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown
            components={{
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              code(props: any) {
                const { className, children, ...rest } = props;
                const match = /language-(\w+)/.exec(className || "");
                const isInline = !match;
                return isInline ? (
                  <code
                    {...rest}
                    className="bg-megumin-surface-raised px-1 py-0.5 rounded text-megumin-glow font-mono text-xs"
                  >
                    {children}
                  </code>
                ) : (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    className="rounded-lg text-xs my-2"
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

export function LoadingBubble() {
  return (
    <div className="flex gap-3 flex-row animate-fade-slide-in">
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-lg flex-shrink-0"
        style={{ boxShadow: "0 0 12px rgba(124,58,237,0.5)" }}
      >
        🧙‍♀️
      </div>
      <div className="bg-megumin-agent-bubble border border-megumin-border rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
        <span className="loading-dot" />
        <span className="loading-dot" />
        <span className="loading-dot" />
      </div>
    </div>
  );
}
