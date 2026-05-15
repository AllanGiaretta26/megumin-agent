import { request } from "@/lib/api-client";
import type { AppConfig } from "./types";

export async function getConfig(): Promise<AppConfig> {
  return request<AppConfig>("/config");
}

export async function updateConfig(partial: Partial<AppConfig>): Promise<AppConfig> {
  return request<AppConfig>("/config", {
    method: "PUT",
    body: JSON.stringify(partial),
  });
}

export async function validatePath(
  path: string
): Promise<{ valid: boolean; error: string | null }> {
  return request<{ valid: boolean; error: string | null }>("/config/validate-path", {
    method: "POST",
    body: JSON.stringify({ path }),
  });
}

export async function listModels(): Promise<{
  models: string[];
  ollama_available: boolean;
}> {
  return request<{ models: string[]; ollama_available: boolean }>("/models");
}
