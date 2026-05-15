"use client";

import { useCallback, useEffect, useState } from "react";
import { getConfig, updateConfig, validatePath as validatePathApi } from "../api";
import type { AppConfig } from "../types";

export function useConfig() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const saveConfig = useCallback(async (partial: Partial<AppConfig>) => {
    if (!config) return;
    const updated = await updateConfig({ ...config, ...partial });
    setConfig(updated);
  }, [config]);

  const validatePath = useCallback(
    (path: string) => validatePathApi(path),
    []
  );

  return { config, isLoading, saveConfig, validatePath };
}
