import { useTranslation } from "react-i18next";
import type { Message } from "../types";
import ToolCallCard from "./ToolCallCard";

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const { t } = useTranslation();
  const isUser = message.role === "user";
  const isError = message.isError;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-bubble-user text-white"
            : isError
              ? "bg-red-900/40 border border-red-700 text-red-200"
              : "bg-bubble-ai text-gray-200"
        }`}
      >
        {!isUser && (
          <div className="text-xs text-gray-400 mb-1 font-medium">
            {isError ? `⚠️ ${t("chat.error")}` : `🤖 ${t("chat.assistant")}`}
          </div>
        )}

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mb-3 space-y-1">
            {message.toolCalls.map((tc) => (
              <ToolCallCard key={tc.step} step={tc} />
            ))}
          </div>
        )}

        <div className="whitespace-pre-wrap break-words">
          {message.content || (message.isStreaming && <StreamingCursor />)}
        </div>

        {isError && message.retryable && (
          <button className="mt-2 text-xs text-red-300 hover:text-red-100 underline cursor-pointer">
            {t("chat.retry")}
          </button>
        )}
      </div>
    </div>
  );
}

function StreamingCursor() {
  return (
    <span className="inline-block w-2 h-4 bg-blue-400 ml-0.5 animate-pulse rounded-sm" />
  );
}
