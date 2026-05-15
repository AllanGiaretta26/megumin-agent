"use client";

import { useEffect, useState } from "react";
import { request } from "@/lib/api-client";

export function useOllamaStatus() {
  const [ollamaAvailable, setOllamaAvailable] = useState(false);

  useEffect(() => {
    const check = () =>
      request<{ ollama_available: boolean }>("/health")
        .then((data) => setOllamaAvailable(data.ollama_available))
        .catch(() => setOllamaAvailable(false));

    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  return { ollamaAvailable };
}
