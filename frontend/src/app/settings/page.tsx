"use client";

import { SettingsForm } from "@/features/config/components/settings-form";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-megumin-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-megumin-border bg-megumin-surface/90 backdrop-blur-sm shadow-[0_1px_0_rgba(245,158,11,0.08)]">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm text-megumin-text-muted hover:text-megumin-text-primary transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar ao Chat
          </Link>
          <h1 className="text-base font-semibold text-megumin-text-primary">
            Configurações
          </h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">
        <SettingsForm onCancel={() => window.history.back()} />
      </main>
    </div>
  );
}
