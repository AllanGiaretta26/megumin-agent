"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { CheckCircle, Loader2, XCircle } from "lucide-react";
import { useState } from "react";

interface PathPickerProps {
  value: string;
  onChange: (value: string) => void;
  onValidate: (path: string) => Promise<{ valid: boolean; error: string | null }>;
}

type ValidationState = "idle" | "loading" | "valid" | "invalid";

export function PathPicker({ value, onChange, onValidate }: PathPickerProps) {
  const [validationState, setValidationState] = useState<ValidationState>("idle");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleValidate = async () => {
    if (!value.trim()) return;
    setValidationState("loading");
    try {
      const result = await onValidate(value.trim());
      setValidationState(result.valid ? "valid" : "invalid");
      setValidationError(result.error);
    } catch {
      setValidationState("invalid");
      setValidationError("Erro ao validar o caminho.");
    }
  };

  const handleChange = (v: string) => {
    onChange(v);
    setValidationState("idle");
    setValidationError(null);
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <Input
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          placeholder="Ex: C:\dev\meu-projeto"
          className="bg-megumin-surface-raised border-megumin-border text-megumin-text-primary placeholder:text-megumin-text-muted focus-visible:ring-megumin-primary"
        />
        <Button
          type="button"
          variant="outline"
          onClick={handleValidate}
          disabled={!value.trim() || validationState === "loading"}
          className="border-megumin-border hover:bg-megumin-surface-raised shrink-0"
        >
          {validationState === "loading" ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            "Validar"
          )}
        </Button>
      </div>

      {validationState === "valid" && (
        <p className="flex items-center gap-1.5 text-xs text-green-400">
          <CheckCircle className="h-3.5 w-3.5" />
          Caminho válido
        </p>
      )}
      {validationState === "invalid" && (
        <p className={cn("flex items-center gap-1.5 text-xs text-red-400")}>
          <XCircle className="h-3.5 w-3.5" />
          {validationError ?? "Caminho inválido"}
        </p>
      )}
    </div>
  );
}
