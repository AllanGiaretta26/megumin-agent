"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, FolderOpen, Globe, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { listModels } from "../api";
import { useConfig } from "../hooks/use-config";
import type { AppConfig } from "../types";
import { PathPicker } from "./path-picker";

interface SettingsFormProps {
  onCancel: () => void;
}

export function SettingsForm({ onCancel }: SettingsFormProps) {
  const { config, isLoading, saveConfig, validatePath } = useConfig();
  const [draft, setDraft] = useState<AppConfig | null>(null);
  const [models, setModels] = useState<string[]>([]);
  const [newApiKey, setNewApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (config) setDraft(config);
  }, [config]);

  useEffect(() => {
    listModels().then(({ models }) => setModels(models)).catch(() => {});
  }, []);

  if (isLoading || !draft) {
    return (
      <div className="flex items-center justify-center h-40 text-megumin-text-muted text-sm">
        Carregando configurações...
      </div>
    );
  }

  const update = (patch: Partial<AppConfig>) =>
    setDraft((prev) => (prev ? { ...prev, ...patch } : prev));

  const updatePersonality = (patch: Partial<AppConfig["personality"]>) =>
    setDraft((prev) =>
      prev ? { ...prev, personality: { ...prev.personality, ...patch } } : prev
    );

  const handleSave = async () => {
    if (!draft) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      // newApiKey vazio = manter chave existente (sentinel "***"); preenchido = substituir
      await saveConfig({ ...draft, api_key: newApiKey.trim() || "***" });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Erro ao salvar.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Projeto */}
      <section className="rounded-xl border border-megumin-border bg-megumin-surface p-5 space-y-3">
        <h2 className="text-sm font-semibold text-megumin-text-primary flex items-center gap-2">
          <FolderOpen className="h-4 w-4" /> Projeto
        </h2>
        <p className="text-xs text-megumin-text-muted">
          Diretório raiz do projeto que o agente poderá ler e modificar.
        </p>
        <PathPicker
          value={draft.project_path ?? ""}
          onChange={(v) => update({ project_path: v || null })}
          onValidate={validatePath}
        />
      </section>

      {/* Modelo */}
      <section className="rounded-xl border border-megumin-border bg-megumin-surface p-5 space-y-4">
        <h2 className="text-sm font-semibold text-megumin-text-primary flex items-center gap-2">
          <Bot className="h-4 w-4" /> Modelo
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs text-megumin-text-muted">Provider</label>
            <select
              value={draft.provider}
              onChange={(e) => update({ provider: e.target.value })}
              className="w-full rounded-md border border-megumin-border bg-megumin-surface-raised px-3 py-2 text-sm text-megumin-text-primary focus:outline-none focus:ring-1 focus:ring-megumin-primary"
            >
              <option value="ollama">Ollama (local)</option>
              <option value="openai_compatible">OpenAI-compatible</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs text-megumin-text-muted">Modelo</label>
            {models.length > 0 ? (
              <select
                value={draft.model_name}
                onChange={(e) => update({ model_name: e.target.value })}
                className="w-full rounded-md border border-megumin-border bg-megumin-surface-raised px-3 py-2 text-sm text-megumin-text-primary focus:outline-none focus:ring-1 focus:ring-megumin-primary"
              >
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            ) : (
              <Input
                value={draft.model_name}
                onChange={(e) => update({ model_name: e.target.value })}
                placeholder="ex: qwen3.5:9b"
                className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary"
              />
            )}
          </div>
        </div>

        {draft.provider === "openai_compatible" && (
          <div className="space-y-3 pt-2 border-t border-megumin-border">
            <div className="space-y-1.5">
              <label className="text-xs text-megumin-text-muted">Base URL</label>
              <Input
                value={draft.api_base_url ?? ""}
                onChange={(e) => update({ api_base_url: e.target.value || null })}
                placeholder="https://api.openai.com/v1"
                className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-megumin-text-muted">API Key</label>
              <div className="relative">
                <Input
                  type={showApiKey ? "text" : "password"}
                  value={newApiKey}
                  onChange={(e) => setNewApiKey(e.target.value)}
                  placeholder={draft.api_key_configured ? "••••••••" : "sk-..."}
                  className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary pr-16"
                />
                {newApiKey.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowApiKey((v) => !v)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-megumin-text-muted hover:text-megumin-text-primary transition-colors text-xs"
                  >
                    {showApiKey ? "Ocultar" : "Mostrar"}
                  </button>
                )}
              </div>
              {draft.api_key_configured && (
                <p className="text-xs text-megumin-text-muted">
                  Chave configurada. Deixe em branco para manter a atual.
                </p>
              )}
            </div>
          </div>
        )}
      </section>

      {/* Personalidade */}
      <section className="rounded-xl border border-megumin-border bg-megumin-surface p-5 space-y-5">
        <h2 className="text-sm font-semibold text-megumin-text-primary flex items-center gap-2">
          <Sparkles className="h-4 w-4" /> Personalidade
        </h2>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-xs text-megumin-text-muted">
              Nível de Drama
            </label>
            <span className="text-xs font-mono text-megumin-primary">
              {draft.personality.drama_level}
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            step={1}
            value={draft.personality.drama_level}
            onChange={(e) =>
              updatePersonality({ drama_level: Number(e.target.value) })
            }
            className="w-full accent-megumin-primary"
          />
          <div className="flex justify-between text-xs text-megumin-text-muted">
            <span>Objetivo</span>
            <span>EXPLOSÃO!!!</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-xs text-megumin-text-muted">Temperature</label>
            <span className="text-xs font-mono text-megumin-primary">
              {draft.personality.temperature.toFixed(1)}
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={2}
            step={0.1}
            value={draft.personality.temperature}
            onChange={(e) =>
              updatePersonality({ temperature: Number(e.target.value) })
            }
            className="w-full accent-megumin-primary"
          />
          <div className="flex justify-between text-xs text-megumin-text-muted">
            <span>0.0 — determinístico</span>
            <span>2.0 — caótico</span>
          </div>
        </div>
      </section>

      {/* Idioma */}
      <section className="rounded-xl border border-megumin-border bg-megumin-surface p-5 space-y-3">
        <h2 className="text-sm font-semibold text-megumin-text-primary flex items-center gap-2">
          <Globe className="h-4 w-4" /> Idioma
        </h2>
        <select
          value={draft.personality.language}
          onChange={(e) => updatePersonality({ language: e.target.value })}
          className="w-full rounded-md border border-megumin-border bg-megumin-surface-raised px-3 py-2 text-sm text-megumin-text-primary focus:outline-none focus:ring-1 focus:ring-megumin-primary"
        >
          <option value="pt-BR">Português (BR)</option>
          <option value="en">English</option>
        </select>
      </section>

      {/* Feedback + Botões */}
      {saveError && (
        <p className="text-sm text-red-400 text-center">{saveError}</p>
      )}
      {saveSuccess && (
        <p className="text-sm text-green-400 text-center">
          Configurações salvas com sucesso.
        </p>
      )}

      <div className="flex justify-end gap-3 pb-8">
        <Button variant="ghost" onClick={onCancel} className="text-megumin-text-secondary hover:text-megumin-text-primary">
          Cancelar
        </Button>
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-megumin-primary hover:bg-megumin-primary/90 text-white"
        >
          {saving ? "Salvando..." : "💾 Salvar"}
        </Button>
      </div>
    </div>
  );
}
