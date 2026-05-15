"use client";

import { Button, buttonVariants } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ModeSelector } from "@/features/modes/components/mode-selector";
import type { AgentModeId } from "@/features/modes/types";
import { cn } from "@/lib/utils";
import { Plus, Settings, X } from "lucide-react";
import Link from "next/link";

interface SidebarProps {
  activeMode: string;
  onModeChange: (mode: AgentModeId) => void;
  onNewConversation: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({
  activeMode,
  onModeChange,
  onNewConversation,
  isOpen,
  onClose,
}: SidebarProps) {
  return (
    <>
      {/* Backdrop mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 flex flex-col",
          "border-r border-megumin-border bg-megumin-surface",
          "transition-transform duration-300 md:relative md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header com gradiente */}
        <div
          className="px-4 py-5 relative"
          style={{
            background:
              "linear-gradient(180deg, #1a0a2e 0%, #12121a 100%)",
          }}
        >
          {/* Botão fechar mobile */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-megumin-text-muted hover:text-megumin-text-primary transition-colors md:hidden"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Avatar */}
          <div className="flex items-center gap-3">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
              style={{
                background:
                  "radial-gradient(circle, #3b0764 0%, #1a0a2e 100%)",
                boxShadow: "0 0 20px rgba(124,58,237,0.4)",
              }}
            >
              🧙‍♀️
            </div>
            <div>
              <h2
                className="text-base font-bold text-megumin-text-primary leading-none"
                style={{ fontFamily: "serif" }}
              >
                Megumin
              </h2>
              <p className="text-xs text-megumin-primary mt-0.5">
                Arch-wizard · Crimson Demon
              </p>
            </div>
          </div>
        </div>

        <Separator className="bg-megumin-border" />

        {/* Modos */}
        <div className="flex-1 overflow-y-auto px-2 py-3">
          <p className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-megumin-text-muted">
            Modos
          </p>
          <ModeSelector activeMode={activeMode} onModeChange={onModeChange} />
        </div>

        <Separator className="bg-megumin-border" />

        {/* Ações */}
        <div className="px-2 py-3 space-y-1">
          <Button
            variant="ghost"
            onClick={onNewConversation}
            className="w-full justify-start gap-2 text-sm text-megumin-text-secondary hover:text-megumin-text-primary hover:bg-megumin-surface-raised"
          >
            <Plus className="h-4 w-4" />
            Nova Conversa
          </Button>

          <Link
            href="/settings"
            className={cn(
              buttonVariants({ variant: "ghost" }),
              "w-full justify-start gap-2 text-sm text-megumin-text-secondary hover:text-megumin-text-primary hover:bg-megumin-surface-raised"
            )}
          >
            <Settings className="h-4 w-4" />
            Configurações
          </Link>
        </div>
      </aside>
    </>
  );
}
