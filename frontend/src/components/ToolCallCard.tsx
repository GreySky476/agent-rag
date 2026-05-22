import { useTranslation } from "react-i18next";
import type { ToolCallStep } from "../types";

interface Props {
  step: ToolCallStep;
}

const TOOL_ICONS: Record<string, string> = {
  sql_query: "🔧",
  lightrag_search: "🔍",
  python_calc: "🐍",
};

export default function ToolCallCard({ step }: Props) {
  const { t } = useTranslation();
  const icon = TOOL_ICONS[step.tool] || "🔧";

  return (
    <details className="bg-tool-card border border-border rounded p-2 text-xs">
      <summary className="cursor-pointer text-gray-400 hover:text-gray-200 select-none">
        {icon} <span className="font-mono text-blue-400">{step.tool}</span>
        {step.status === "calling" && (
          <span className="ml-2 text-yellow-400 animate-pulse">
            {t("tool.running")}
          </span>
        )}
        {step.status === "success" && (
          <span className="ml-2 text-green-400">✓</span>
        )}
        {step.status === "error" && (
          <span className="ml-2 text-red-400">✗</span>
        )}
      </summary>

      <div className="mt-1.5 pl-4 space-y-1">
        {step.input && (
          <div>
            <span className="text-gray-500">{t("tool.input")}</span>
            <pre className="text-gray-300 bg-gray-900/50 p-1 rounded mt-0.5 overflow-x-auto text-xs">
              {step.input}
            </pre>
          </div>
        )}

        {step.summary && (
          <div>
            <span className="text-gray-500">{t("tool.result")}</span>
            <span className="text-gray-300 ml-1">{step.summary}</span>
          </div>
        )}

        {step.resultData && (
          <div>
            <span className="text-gray-500">{t("tool.details")}</span>
            <pre className="text-gray-300 bg-gray-900/50 p-1 rounded mt-0.5 overflow-x-auto text-xs max-h-32 overflow-y-auto">
              {JSON.stringify(step.resultData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </details>
  );
}
