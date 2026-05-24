"use client";

import { useState } from "react";
import { Check, ChevronDown, ChevronRight, Wrench, X } from "lucide-react";
import type { ToolCall } from "../types";

interface Props {
  toolCall: ToolCall;
}

export function ToolCallBlock({ toolCall }: Props) {
  const [expanded, setExpanded] = useState(false);
  const Chevron = expanded ? ChevronDown : ChevronRight;
  const StatusIcon = toolCall.status === "ok" ? Check : X;
  const statusColor = toolCall.status === "ok" ? "text-emerald-400" : "text-megumin-accent";

  return (
    <div className="my-2 rounded-md border border-megumin-border bg-megumin-surface-raised/70 text-sm shadow-[inset_0_1px_0_rgba(245,158,11,0.06)]">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 hover:bg-megumin-primary/10 transition-colors"
      >
        <Chevron className="h-4 w-4 text-megumin-text-muted" />
        <Wrench className="h-4 w-4 text-megumin-text-muted" />
        <span className="font-mono text-megumin-primary">{toolCall.tool}</span>
        <StatusIcon className={`h-4 w-4 ${statusColor}`} />
      </button>

      {expanded && (
        <div className="border-t border-megumin-border px-3 py-2 space-y-2">
          <div>
            <div className="text-xs uppercase text-megumin-text-muted mb-1">args</div>
            <pre className="text-xs bg-background rounded p-2 overflow-x-auto">
              {JSON.stringify(toolCall.args, null, 2)}
            </pre>
          </div>
          <div>
            <div className="text-xs uppercase text-megumin-text-muted mb-1">output</div>
            <pre className="text-xs bg-background rounded p-2 overflow-x-auto whitespace-pre-wrap">
              {toolCall.output || "(empty)"}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
