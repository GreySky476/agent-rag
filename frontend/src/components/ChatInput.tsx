import { useState, useRef, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  onSend: (content: string) => void;
  onStop: () => void;
  isStreaming: boolean;
}

export default function ChatInput({ onSend, onStop, isStreaming }: Props) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 150)}px`;
    }
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border bg-gray-900 px-4 py-3">
      <div className="max-w-3xl mx-auto flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("chat.placeholder")}
          rows={1}
          className="flex-1 bg-gray-800 border border-border rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500 max-h-[150px]"
        />

        {isStreaming ? (
          <button
            onClick={onStop}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg cursor-pointer transition-colors flex-shrink-0"
          >
            ⏹ {t("chat.stop")}
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!value.trim()}
            className={`px-4 py-2 text-sm rounded-lg cursor-pointer transition-colors flex-shrink-0 ${
              value.trim()
                ? "bg-blue-600 hover:bg-blue-700 text-white"
                : "bg-gray-700 text-gray-500 cursor-not-allowed"
            }`}
          >
            ⬆ {t("chat.send")}
          </button>
        )}
      </div>
    </div>
  );
}
