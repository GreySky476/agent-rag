import { useTranslation } from "react-i18next";

export default function LanguageToggle() {
  const { i18n, t } = useTranslation();

  const toggle = () => {
    const next = i18n.language === "zh" ? "en" : "zh";
    i18n.changeLanguage(next);
  };

  return (
    <button
      onClick={toggle}
      title={t("lang.tooltip")}
      className="text-xs text-gray-400 hover:text-gray-200 bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded cursor-pointer transition-colors"
    >
      🌐 {t("lang.label")}
    </button>
  );
}
