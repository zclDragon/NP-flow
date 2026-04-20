"use client";

import { BotIcon } from "lucide-react";

import { type Agent } from "@/core/agents";
import { cn } from "@/lib/utils";

import { Suggestion, Suggestions } from "../ai-elements/suggestion";

export function AgentWelcome({
  className,
  agent,
  agentName,
  onSuggestionClick,
}: {
  className?: string;
  agent: Agent | null | undefined;
  agentName: string;
  onSuggestionClick?: (suggestion: string) => void;
}) {
  const displayName = agent?.name ?? agentName;
  const description = agent?.description;
  const presetSuggestions =
    agent?.preset_suggestions?.filter((suggestion) => suggestion.trim().length > 0) ??
    [];

  return (
    <div
      className={cn(
        "mx-auto flex w-full flex-col items-center justify-center gap-3 px-8 py-4 text-center",
        className,
      )}
    >
      <div className="bg-primary/10 flex h-12 w-12 items-center justify-center rounded-full">
        <BotIcon className="text-primary h-6 w-6" />
      </div>
      <div className="text-2xl font-bold">{displayName}</div>
      {description && (
        <p className="text-muted-foreground max-w-sm text-sm">{description}</p>
      )}
      {presetSuggestions.length > 0 && (
        <Suggestions className="mt-2 min-h-0 w-full max-w-xl justify-center">
          {presetSuggestions.map((suggestion) => (
            <Suggestion
              key={suggestion}
              className="bg-background/80 text-foreground border-border/70"
              suggestion={suggestion}
              onClick={() => onSuggestionClick?.(suggestion)}
            />
          ))}
        </Suggestions>
      )}
    </div>
  );
}
