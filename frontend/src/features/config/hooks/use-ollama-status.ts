"use client";

import { useEffect, useState } from "react";
import { request } from "@/lib/api-client";

export function useOllamaStatus() {
  const [backendAvailable, setBackendAvailable] = useState(false);
  const [ollamaAvailable, setOllamaAvailable] = useState(false);

  useEffect(() => {
    const check = () =>
      request<{ ollama_available: boolean }>("/health")
        .then((data) => {
          setBackendAvailable(true);
          setOllamaAvailable(data.ollama_available);
        })
        .catch(() => {
          setBackendAvailable(false);
          setOllamaAvailable(false);
        });

    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  return { backendAvailable, ollamaAvailable };
}
