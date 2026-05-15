"use client";

import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
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
            remarkPlugins={[remarkGfm]}
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
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              table(props: any) {
                return (
                  <div className="overflow-x-auto my-3">
                    <table className="w-full border-collapse text-xs">{props.children}</table>
                  </div>
                );
              },
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              thead(props: any) {
                return <thead className="bg-megumin-surface-raised">{props.children}</thead>;
              },
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              tbody(props: any) {
                return <tbody>{props.children}</tbody>;
              },
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              tr(props: any) {
                return (
                  <tr className="border-b border-megumin-border even:bg-megumin-surface-raised/50">
                    {props.children}
                  </tr>
                );
              },
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              th(props: any) {
                return (
                  <th className="px-3 py-2 text-left font-semibold text-megumin-primary border-b border-megumin-border">
                    {props.children}
                  </th>
                );
              },
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              td(props: any) {
                return (
                  <td className="px-3 py-2 text-left text-megumin-text-primary border-r border-megumin-border/50 last:border-r-0">
                    {props.children}
                  </td>
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
