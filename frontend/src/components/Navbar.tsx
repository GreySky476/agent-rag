import { useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useChatStore } from "../stores/chatStore";
import LanguageToggle from "./LanguageToggle";

export default function Navbar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { toggleSidebar, setActivePage } = useChatStore();

  const isChat = location.pathname.startsWith("/chat");
  const isKnowledge = location.pathname.startsWith("/knowledge");

  const navigateTo = (page: "chat" | "knowledge") => {
    setActivePage(page);
    navigate(page === "chat" ? "/chat" : "/knowledge");
  };

  return (
    <header className="h-12 flex items-center justify-between px-4 bg-gray-900 border-b border-border flex-shrink-0">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="text-gray-400 hover:text-gray-200 text-lg cursor-pointer"
          title="Toggle sidebar"
        >
          ☰
        </button>
        <span className="font-semibold text-gray-200 text-sm">
          🧠 {t("app.title")}
        </span>
      </div>

      <nav className="flex gap-1">
        <button
          onClick={() => navigateTo("chat")}
          className={`px-3 py-1 text-sm rounded cursor-pointer transition-colors ${
            isChat
              ? "bg-blue-600 text-white"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
          }`}
        >
          {t("nav.chat")}
        </button>
        <button
          onClick={() => navigateTo("knowledge")}
          className={`px-3 py-1 text-sm rounded cursor-pointer transition-colors ${
            isKnowledge
              ? "bg-blue-600 text-white"
              : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
          }`}
        >
          {t("nav.knowledge")}
        </button>
      </nav>

      <div className="flex items-center gap-2">
        <LanguageToggle />
      </div>
    </header>
  );
}
