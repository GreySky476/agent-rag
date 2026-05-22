import { useEffect } from "react";
import { useChatStore } from "../stores/chatStore";

export function useConversations() {
  const loadConversations = useChatStore((s) => s.loadConversations);
  const conversations = useChatStore((s) => s.conversations);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return { conversations, refresh: loadConversations };
}
