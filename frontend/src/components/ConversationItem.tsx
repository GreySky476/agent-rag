import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import type { Conversation } from "../types";

interface Props {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (title: string) => void;
}

export default function ConversationItem({
  conversation,
  isActive,
  onSelect,
  onDelete,
  onRename,
}: Props) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(
    conversation.title || conversation.last_question?.slice(0, 20) || ""
  );
  const [showMenu, setShowMenu] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const handleDoubleClick = () => {
    setEditValue(
      conversation.title || conversation.last_question?.slice(0, 20) || ""
    );
    setEditing(true);
  };

  const commitRename = () => {
    setEditing(false);
    if (editValue.trim() && editValue !== conversation.title) {
      onRename(editValue.trim());
    }
  };

  const title =
    conversation.title ||
    conversation.last_question?.slice(0, 20) ||
    t("sidebar.untitled");

  return (
    <div
      onClick={onSelect}
      onDoubleClick={handleDoubleClick}
      onContextMenu={(e) => {
        e.preventDefault();
        setShowMenu(true);
      }}
      className={`group relative px-2 py-1.5 mx-1 rounded cursor-pointer text-sm transition-colors ${
        isActive
          ? "bg-blue-600/30 text-gray-100"
          : "text-gray-400 hover:bg-sidebar-hover hover:text-gray-200"
      }`}
    >
      {editing ? (
        <input
          ref={inputRef}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={commitRename}
          onKeyDown={(e) => {
            if (e.key === "Enter") commitRename();
            if (e.key === "Escape") setEditing(false);
          }}
          onClick={(e) => e.stopPropagation()}
          className="w-full bg-gray-800 border border-blue-500 rounded px-1 py-0.5 text-gray-200 text-sm focus:outline-none"
        />
      ) : (
        <div className="truncate pr-6 flex items-center gap-1.5">
          <span className="text-xs shrink-0">
            {conversation.message_count > 1 ? "💬" : "💭"}
          </span>
          <span className="truncate">{title}</span>
        </div>
      )}

      {!editing && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 text-xs cursor-pointer transition-opacity"
          title={t("sidebar.delete")}
        >
          🗑️
        </button>
      )}

      {showMenu && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute right-0 top-full mt-1 z-50 bg-gray-800 border border-border rounded shadow-lg py-1 min-w-[120px]">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(false);
                handleDoubleClick();
              }}
              className="w-full text-left px-3 py-1 text-sm text-gray-300 hover:bg-gray-700 cursor-pointer"
            >
              {t("sidebar.rename")}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(false);
                onDelete();
              }}
              className="w-full text-left px-3 py-1 text-sm text-red-400 hover:bg-gray-700 cursor-pointer"
            >
              {t("sidebar.delete")}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
