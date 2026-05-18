"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, FolderOpen, Globe, Info, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getRestartRequired, listModels, listModelsFromForm } from "../api";
import { useConfig } from "../hooks/use-config";
import type { AppConfig } from "../types";
import { PathPicker } from "./path-picker";

// Sentinel que o backend interpreta como "manter a api_key salva no disco".
// O GET /config nunca devolve a chave real — mascara como "***". Reenviar
// esse mesmo valor é o jeito correto de "não tocar" na chave.
const API_KEY_SENTINEL = "***";

// URLs default por provider. Aplicadas ao trocar o select de provider para
// evitar carregar base_url incompatível (ex.: ollama.com/v1 com provider=ollama
// faria a chamada /api/tags ir pro endpoint errado).
const DEFAULT_BASE_URLS: Record<string, string> = {
  ollama: "http://localhost:11434",
  openai_compatible: "https://ollama.com/v1",
};

interface SettingsFormProps {
  onCancel: () => void;
}

export function SettingsForm({ onCancel }: SettingsFormProps) {
  const { config, isLoading, saveConfig, validatePath } = useConfig();
  const [draft, setDraft] = useState<AppConfig | null>(null);
  const [models, setModels] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelsError, setModelsError] = useState<string | null>(null);
  const [newApiKey, setNewApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [restartInfo, setRestartInfo] = useState<{
    required: boolean;
    fields: string[];
  } | null>(null);
  // Vira true assim que o user edita provider/base_url/api_key no form.
  // Enquanto false, /models usa GET (config do disco) — sem race condition.
  // Quando true, /models usa POST com os valores ATUAIS do form.
  const [criticalFieldsTouched, setCriticalFieldsTouched] = useState(false);
  // Fallback manual quando /models não devolve uma lista usável (erro, vazio,
  // ou modelo salvo fora da lista). Permite digitar o nome do modelo a mão.
  const [manualModelEntry, setManualModelEntry] = useState(false);

  const refreshRestartInfo = useCallback(async () => {
    try {
      const data = await getRestartRequired();
      setRestartInfo({ required: data.restart_required, fields: data.changed_fields });
    } catch {
      setRestartInfo(null);
    }
  }, []);

  useEffect(() => {
    void refreshRestartInfo();
  }, [refreshRestartInfo]);

  useEffect(() => {
    if (config) setDraft(config);
  }, [config]);

  // Recarrega a lista de modelos quando provider, base_url ou api_key mudam.
  // Debounce de 500ms evita 1 request por tecla digitada.
  // Carga inicial: GET /models (config do disco, com chave real).
  // Após user editar: POST /models com valores do form (sem persistir).
  const provider = draft?.provider;
  const apiBaseUrl = draft?.api_base_url ?? null;
  const apiKeyConfigured = draft?.api_key_configured ?? false;
  useEffect(() => {
    if (!provider) return;
    const handle = setTimeout(() => {
      setModelsLoading(true);
      setModelsError(null);

      // Resolve api_key a enviar:
      // - user digitou nova chave  → usa essa chave
      // - tem chave salva no disco → sentinel API_KEY_SENTINEL (backend resolve)
      // - sem nada                  → string vazia (ok para ollama, erro 400 para openai_compat)
      const apiKeyToSend = newApiKey
        ? newApiKey
        : apiKeyConfigured
          ? API_KEY_SENTINEL
          : "";

      const fetchPromise = criticalFieldsTouched
        ? listModelsFromForm({
            provider,
            api_base_url: apiBaseUrl ?? "",
            api_key: apiKeyToSend,
          })
        : listModels();

      fetchPromise
        .then(({ models }) => setModels(models))
        .catch((err: unknown) => {
          setModels([]);
          setModelsError(err instanceof Error ? err.message : "Falha ao listar modelos.");
        })
        .finally(() => setModelsLoading(false));
    }, 500);
    return () => clearTimeout(handle);
  }, [provider, apiBaseUrl, apiKeyConfigured, newApiKey, criticalFieldsTouched]);

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
      // newApiKey vazio = manter chave existente (sentinel); preenchido = substituir
      await saveConfig({ ...draft, api_key: newApiKey.trim() || API_KEY_SENTINEL });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      void refreshRestartInfo();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Erro ao salvar.");
    } finally {
      setSaving(false);
    }
  };

  const FIELD_LABELS: Record<string, string> = {
    provider: "Provider",
    model_name: "Modelo",
    api_base_url: "Base URL",
    api_key: "API Key",
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {restartInfo?.required && (
        <div className="rounded-md border border-blue-500/40 bg-blue-500/10 px-4 py-3 flex items-start gap-3">
          <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-200">
            <p className="font-medium">
              Mudanças aplicadas a partir das próximas conversas.
            </p>
            <p className="text-xs text-blue-200/80 mt-0.5">
              Streams já abertos continuam com a configuração anterior até
              terminarem. Para garantir consistência total, considere reiniciar
              o backend.
            </p>
            {restartInfo.fields.length > 0 && (
              <p className="text-xs text-blue-200/80 mt-1">
                Campos alterados:{" "}
                {restartInfo.fields.map((f) => FIELD_LABELS[f] ?? f).join(", ")}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Projeto */}
      <section className="rounded-xl border border-megumin-border bg-megumin-surface p-5 space-y-3">
        <h2 className="text-sm font-semibold text-megumin-text-primary flex items-center gap-2">
          <FolderOpen className="h-4 w-4" /> Projeto
        </h2>
        <p className="text-xs text-megumin-text-muted">
          Diretório raiz do projeto que o agente poderá ler e modificar.
        </p>
        <PathPicker
          id="project-path"
          name="project-path"
          ariaLabel="Caminho do projeto"
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
            <label htmlFor="provider" className="text-xs text-megumin-text-muted">Provider</label>
            <select
              id="provider"
              name="provider"
              value={draft.provider}
              onChange={(e) => {
                const next = e.target.value;
                setCriticalFieldsTouched(true);
                // Reseta api_base_url para o default do novo provider — evita
                // arrastar URL incompatível (ex.: ollama.com/v1 ficando como
                // base de provider=ollama). User pode editar depois manualmente.
                update({
                  provider: next,
                  api_base_url: DEFAULT_BASE_URLS[next] ?? null,
                });
              }}
              className="w-full rounded-md border border-megumin-border bg-megumin-surface-raised px-3 py-2 text-sm text-megumin-text-primary focus:outline-none focus:ring-1 focus:ring-megumin-primary"
            >
              <option value="ollama">Ollama (local)</option>
              <option value="openai_compatible">OpenAI-compatible</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="model-name" className="text-xs text-megumin-text-muted">Modelo</label>
            {(() => {
              const savedMissing =
                !!draft.model_name && !models.includes(draft.model_name);
              const disabled =
                modelsLoading || !!modelsError || models.length === 0;
              const placeholder = modelsLoading
                ? "Carregando modelos..."
                : modelsError
                  ? "Erro ao carregar"
                  : models.length === 0
                    ? "Nenhum modelo encontrado"
                    : null;
              const fallbackAvailable = !modelsLoading && (disabled || savedMissing);

              if (manualModelEntry) {
                return (
                  <>
                    <Input
                      id="model-name"
                      name="model-name"
                      value={draft.model_name}
                      onChange={(e) => update({ model_name: e.target.value })}
                      placeholder="ex: qwen3.5:9b"
                      className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setManualModelEntry(false)}
                      className="text-xs text-megumin-primary hover:underline mt-1"
                    >
                      Voltar ao dropdown
                    </button>
                  </>
                );
              }

              return (
                <>
                  <select
                    id="model-name"
                    name="model-name"
                    value={draft.model_name}
                    onChange={(e) => update({ model_name: e.target.value })}
                    disabled={disabled}
                    className="w-full rounded-md border border-megumin-border bg-megumin-surface-raised px-3 py-2 text-sm text-megumin-text-primary focus:outline-none focus:ring-1 focus:ring-megumin-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {placeholder && <option value={draft.model_name}>{placeholder}</option>}
                    {savedMissing && !placeholder && (
                      <option value={draft.model_name}>
                        {draft.model_name} (não disponível)
                      </option>
                    )}
                    {models.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                  {modelsError && (
                    <p className="text-xs text-red-400 mt-1">{modelsError}</p>
                  )}
                  {fallbackAvailable && (
                    <button
                      type="button"
                      onClick={() => setManualModelEntry(true)}
                      className="text-xs text-megumin-primary hover:underline mt-1"
                    >
                      Inserir manualmente
                    </button>
                  )}
                </>
              );
            })()}
          </div>
        </div>

        {draft.provider === "openai_compatible" && (
          <div className="space-y-3 pt-2 border-t border-megumin-border">
            <div className="space-y-1.5">
              <label htmlFor="api-base-url" className="text-xs text-megumin-text-muted">Base URL</label>
              <Input
                id="api-base-url"
                name="api-base-url"
                value={draft.api_base_url ?? ""}
                onChange={(e) => {
                  setCriticalFieldsTouched(true);
                  update({ api_base_url: e.target.value || null });
                }}
                placeholder="https://api.openai.com/v1"
                className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="api-key" className="text-xs text-megumin-text-muted">API Key</label>
              <div className="relative">
                <Input
                  id="api-key"
                  name="api-key"
                  type={showApiKey ? "text" : "password"}
                  value={newApiKey}
                  onChange={(e) => {
                    setCriticalFieldsTouched(true);
                    setNewApiKey(e.target.value);
                  }}
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
            <label htmlFor="drama-level" className="text-xs text-megumin-text-muted">
              Nível de Drama
            </label>
            <span className="text-xs font-mono text-megumin-primary">
              {draft.personality.drama_level}
            </span>
          </div>
          <input
            id="drama-level"
            name="drama-level"
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
            <label htmlFor="temperature" className="text-xs text-megumin-text-muted">Temperature</label>
            <span className="text-xs font-mono text-megumin-primary">
              {draft.personality.temperature.toFixed(1)}
            </span>
          </div>
          <input
            id="temperature"
            name="temperature"
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
          id="language"
          name="language"
          aria-label="Idioma"
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
