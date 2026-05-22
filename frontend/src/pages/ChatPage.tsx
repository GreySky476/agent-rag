import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useChatStore } from "../stores/chatStore";
import { useSSE } from "../hooks/useSSE";
import MessageList from "../components/MessageList";
import ChatInput from "../components/ChatInput";
import EmptyChat from "../components/EmptyChat";

export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { sendMessage } = useSSE();

  const {
    activeSessionId,
    messages,
    isStreaming,
    selectConversation,
    createConversation,
    stopGeneration,
  } = useChatStore();

  useEffect(() => {
    if (sessionId && sessionId !== activeSessionId) {
      selectConversation(sessionId);
    } else if (!sessionId && activeSessionId) {
      // No session in URL but we have an active one
      navigate(`/chat/${activeSessionId}`, { replace: true });
    }
  }, [sessionId, activeSessionId, selectConversation, navigate]);

  const handleSend = async (content: string) => {
    let currentSession = activeSessionId;
    if (!currentSession) {
      currentSession = createConversation();
      navigate(`/chat/${currentSession}`, { replace: true });
    }
    await sendMessage(content, currentSession);
  };

  const showEmpty = messages.length === 0 && !isStreaming;

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto">
        {showEmpty ? (
          <EmptyChat onSuggestionClick={handleSend} />
        ) : (
          <MessageList messages={messages} />
        )}
      </div>
      <ChatInput onSend={handleSend} onStop={stopGeneration} isStreaming={isStreaming} />
    </div>
  );
}
