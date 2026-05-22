import type { AgentStepInfo } from "../types";

interface Props {
  steps: AgentStepInfo[];
}

const PHASE_ICON: Record<string, string> = {
  deciding: "🔄",
  schema_query: "📋",
  sql_query: "🗄️",
  lightrag_search: "🔍",
  python_calc: "🐍",
  reflection: "🤔",
  answering: "✍️",
};

export default function AgentProgress({ steps }: Props) {
  if (steps.length === 0) return null;

  const visible = steps.filter(
    (s) => s.phase === "deciding" || s.phase === "reflection" || s.phase === "answering"
  );

  if (visible.length === 0) return null;

  return (
    <div className="mb-3 space-y-1">
      {visible.map((step, i) => (
        <div
          key={`${step.loop}-${step.phase}-${i}`}
          className={`flex items-center gap-2 text-xs px-3 py-1 rounded ${
            step.phase === "answering"
              ? "bg-green-900/20 text-green-300"
              : step.phase === "reflection"
                ? "bg-purple-900/20 text-purple-300"
                : "bg-blue-900/20 text-blue-300"
          }`}
        >
          <span>{PHASE_ICON[step.phase] || "🔄"}</span>
          <span>
            {step.message}
            {step.phase === "deciding" && (
              <span className="inline-block w-2 h-3 bg-blue-400 ml-1 animate-pulse rounded-sm align-middle" />
            )}
          </span>
        </div>
      ))}
    </div>
  );
}
