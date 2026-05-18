"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Send, Square } from "lucide-react";
import { useRef, useState } from "react";

const MAX_CHARS = 2000;
const MAX_ROWS = 6;
const LINE_HEIGHT = 24; // px aproximado por linha

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  isStreaming?: boolean;
  onStop?: () => void;
}

export function ChatInput({ onSend, isLoading, isStreaming, onStop }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, MAX_ROWS * LINE_HEIGHT) + "px";
  };

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const remaining = MAX_CHARS - value.length;

  return (
    <div className="border-t border-megumin-border bg-megumin-surface p-4">
      <div
        className={cn(
          "flex items-end gap-2 rounded-xl border bg-megumin-surface-raised p-3 transition-all duration-200",
          isLoading
            ? "border-megumin-border opacity-60"
            : "border-megumin-border focus-within:border-megumin-primary focus-within:shadow-[0_0_0_2px_rgba(124,58,237,0.2)]"
        )}
      >
        <textarea
          ref={textareaRef}
          id="chat-message"
          name="chat-message"
          aria-label="Mensagem"
          value={value}
          onChange={(e) => {
            if (e.target.value.length <= MAX_CHARS) setValue(e.target.value);
          }}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Invoque seu feitiço..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-megumin-text-primary placeholder:text-megumin-text-muted outline-none leading-6 disabled:cursor-not-allowed"
          style={{ maxHeight: `${MAX_ROWS * LINE_HEIGHT}px` }}
        />

        <div className="flex items-center gap-2 flex-shrink-0">
          {value.length > MAX_CHARS * 0.8 && (
            <span
              className={cn(
                "text-xs",
                remaining < 100
                  ? "text-megumin-accent"
                  : "text-megumin-text-muted"
              )}
            >
              {remaining}
            </span>
          )}

          {isStreaming ? (
            <Button
              size="icon"
              onClick={onStop}
              title="Parar geração"
              className="h-8 w-8 rounded-lg bg-megumin-accent text-white hover:bg-megumin-accent/80 transition-all duration-200"
            >
              <Square className="h-4 w-4 fill-current" />
            </Button>
          ) : (
            <Button
              size="icon"
              onClick={handleSend}
              disabled={isLoading || !value.trim()}
              className={cn(
                "h-8 w-8 rounded-lg bg-megumin-primary text-white transition-all duration-200",
                "hover:bg-megumin-glow hover:shadow-[0_0_12px_rgba(124,58,237,0.6)]",
                "disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
              )}
            >
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      <p className="mt-1.5 text-center text-xs text-megumin-text-muted">
        Enter para enviar · Shift+Enter para nova linha
      </p>
    </div>
  );
}
