import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ConversationItem from "./ConversationItem";
import { useChatStore } from "../stores/chatStore";
import { useConversations } from "../hooks/useConversations";
import type { Conversation } from "../types";

export default function Sidebar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { conversations, refresh } = useConversations();
  const {
    activeSessionId,
    createConversation,
    deleteConversation,
    renameConversation,
  } = useChatStore();
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!search.trim()) return conversations;
    const q = search.toLowerCase();
    return conversations.filter(
      (c) =>
        c.title?.toLowerCase().includes(q) ||
        c.last_question?.toLowerCase().includes(q)
    );
  }, [conversations, search]);

  const grouped = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groups: { label: string; items: Conversation[] }[] = [
      { label: t("sidebar.today"), items: [] },
      { label: t("sidebar.yesterday"), items: [] },
      { label: t("sidebar.earlier"), items: [] },
    ];

    for (const c of filtered) {
      const d = new Date(c.updated_at);
      d.setHours(0, 0, 0, 0);
      if (d.getTime() === today.getTime()) {
        groups[0].items.push(c);
      } else if (d.getTime() === yesterday.getTime()) {
        groups[1].items.push(c);
      } else {
        groups[2].items.push(c);
      }
    }

    return groups.filter((g) => g.items.length > 0);
  }, [filtered, t]);

  const handleNew = () => {
    const id = createConversation();
    navigate(`/chat/${id}`);
  };

  return (
    <div className="h-full flex flex-col bg-sidebar">
      <div className="p-2">
        <input
          type="text"
          placeholder={t("sidebar.search")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-2 py-1.5 text-sm bg-gray-800 border border-border rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
      </div>

      <button
        onClick={handleNew}
        className="mx-2 mb-2 px-3 py-1.5 text-sm text-gray-300 bg-gray-800 hover:bg-gray-700 rounded cursor-pointer transition-colors flex items-center gap-1"
      >
        <span className="text-green-400">+</span> {t("sidebar.new")}
      </button>

      <div className="flex-1 overflow-y-auto px-1">
        {filtered.length === 0 && (
          <p className="text-gray-500 text-xs text-center mt-8 px-4">
            {conversations.length === 0
              ? t("sidebar.empty")
              : t("sidebar.noResults")}
          </p>
        )}

        {grouped.map((group) => (
          <div key={group.label} className="mb-2">
            <div className="px-2 py-1 text-xs text-gray-500 font-medium">
              📁 {group.label}
            </div>
            {group.items.map((c) => (
              <ConversationItem
                key={c.session_id}
                conversation={c}
                isActive={c.session_id === activeSessionId}
                onSelect={() => navigate(`/chat/${c.session_id}`)}
                onDelete={() => deleteConversation(c.session_id).then(refresh)}
                onRename={(title) =>
                  renameConversation(c.session_id, title).then(refresh)
                }
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
