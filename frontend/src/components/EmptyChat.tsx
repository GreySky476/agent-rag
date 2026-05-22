import { useTranslation } from "react-i18next";

interface Props {
  onSuggestionClick: (content: string) => void;
}

export default function EmptyChat({ onSuggestionClick }: Props) {
  const { t } = useTranslation();

  const suggestions = [
    t("empty.suggestion1"),
    t("empty.suggestion2"),
    t("empty.suggestion3"),
  ];

  return (
    <div className="h-full flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="text-5xl mb-6">🧠</div>
        <h2 className="text-xl font-semibold text-gray-200 mb-2">
          {t("empty.title")}
        </h2>
        <p className="text-gray-500 text-sm mb-8">{t("empty.desc")}</p>

        <div className="space-y-2">
          <p className="text-xs text-gray-600 mb-2">{t("empty.tryAsking")}</p>
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => onSuggestionClick(s)}
              className="block w-full text-left px-4 py-2 text-sm text-gray-400 bg-gray-800/50 hover:bg-gray-800 border border-border rounded-lg cursor-pointer transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
