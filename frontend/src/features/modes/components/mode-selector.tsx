"use client";

import { cn } from "@/lib/utils";
import {
  ClipboardList,
  MessageCircle,
  MessageSquare,
  Pencil,
  Zap,
} from "lucide-react";
import { AGENT_MODES } from "../constants";
import type { AgentModeId } from "../types";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Zap,
  ClipboardList,
  Pencil,
  MessageCircle,
  MessageSquare,
};

interface ModeSelectorProps {
  activeMode: string;
  onModeChange: (mode: AgentModeId) => void;
}

export function ModeSelector({ activeMode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="space-y-0.5">
      {AGENT_MODES.map((mode) => {
        const Icon = ICONS[mode.icon];
        const isActive = mode.id === activeMode;

        return (
          <button
            key={mode.id}
            onClick={() => onModeChange(mode.id)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-150",
              isActive
                ? "bg-megumin-primary/15 border-l-2 border-megumin-primary text-megumin-text-primary"
                : "border-l-2 border-transparent text-megumin-text-secondary hover:bg-megumin-surface-raised hover:text-megumin-text-primary"
            )}
          >
            {Icon && (
              <Icon
                className={cn(
                  "h-4 w-4 flex-shrink-0",
                  isActive ? "text-megumin-primary" : "text-megumin-text-muted"
                )}
              />
            )}
            <div className="min-w-0">
              <p className="text-sm font-medium leading-none mb-0.5">
                {mode.label}
              </p>
              <p className="text-xs text-megumin-text-muted truncate">
                {mode.description}
              </p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
