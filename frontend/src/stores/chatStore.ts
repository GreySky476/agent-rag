import { create } from "zustand";
import type { AgentStepInfo, Conversation, Message, ToolCallStep } from "../types";
import {
  listConversations,
  getConversation,
  deleteConversation as deleteConv,
  renameConversation as renameConv,
} from "../api/chat";

function generateId(): string {
  return crypto.randomUUID().replace(/-/g, "").slice(0, 16);
}

interface ChatStore {
  conversations: Conversation[];
  activeSessionId: string | null;
  messages: Message[];

  isStreaming: boolean;
  sidebarOpen: boolean;
  activePage: "chat" | "knowledge";

  streamingContent: string;
  toolCallSteps: ToolCallStep[];
  agentSteps: AgentStepInfo[];
  abortController: AbortController | null;
  streamingMessageId: string | null;

  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  createConversation: () => string;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, patch: Partial<Message>) => void;
  startStreaming: (id: string) => void;
  appendStreamContent: (chunk: string) => void;
  addAgentStep: (step: AgentStepInfo) => void;
  addToolCallStep: (step: ToolCallStep) => void;
  updateToolCallStep: (step: number, patch: Partial<ToolCallStep>) => void;
  finishStreaming: (id: string) => void;
  setErrorOnMessage: (id: string, error: string) => void;
  setAbortController: (ctrl: AbortController | null) => void;
  stopGeneration: () => void;
  deleteConversation: (id: string) => Promise<void>;
  renameConversation: (id: string, title: string) => Promise<void>;
  setActivePage: (page: "chat" | "knowledge") => void;
  toggleSidebar: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  conversations: [],
  activeSessionId: null,
  messages: [],

  isStreaming: false,
  sidebarOpen: true,
  activePage: "chat",

  streamingContent: "",
  toolCallSteps: [],
  agentSteps: [],
  abortController: null,
  streamingMessageId: null,

  loadConversations: async () => {
    try {
      const convs = await listConversations();
      set({ conversations: convs });
    } catch {
      // Silently fail — conversations will show empty
    }
  },

  selectConversation: async (id: string) => {
    try {
      const detail = await getConversation(id);
      const messages: Message[] = detail.messages
        .filter((t) => t.final_answer || t.question)
        .map((t) => ({
          id: `msg-${t.id}`,
          role: t.final_answer ? ("assistant" as const) : ("user" as const),
          content: t.final_answer || t.question || "",
          timestamp: new Date(t.created_at).getTime(),
        }));

      // Also add user messages from questions
      const userMessages: Message[] = [];
      for (const t of detail.messages) {
        if (t.question && t.action === "answer") {
          // Already handled above with final_answer
        } else if (t.question && t.final_answer) {
          // This trace has both - use question as user msg
          const exists = messages.find(
            (m) =>
              m.content === t.question && m.role === "user"
          );
          if (!exists && t.question) {
            userMessages.push({
              id: `msg-u-${t.id}`,
              role: "user",
              content: t.question,
              timestamp: new Date(t.created_at).getTime(),
            });
          }
        }
      }

      const allMsgs = [...userMessages, ...messages].sort(
        (a, b) => a.timestamp - b.timestamp
      );

      set({ activeSessionId: id, messages: allMsgs });
    } catch {
      set({ activeSessionId: id, messages: [] });
    }
  },

  createConversation: () => {
    const id = generateId();
    set({ activeSessionId: id, messages: [], streamingContent: "", toolCallSteps: [] });
    return id;
  },

  addMessage: (msg) => {
    set((s) => ({ messages: [...s.messages, msg] }));
  },

  updateMessage: (id, patch) => {
    set((s) => ({
      messages: s.messages.map((m) => (m.id === id ? { ...m, ...patch } : m)),
    }));
  },

  startStreaming: (id) => {
    set({
      isStreaming: true,
      streamingContent: "",
      toolCallSteps: [],
      agentSteps: [],
      streamingMessageId: id,
    });
  },

  appendStreamContent: (chunk) => {
    set((s) => ({
      streamingContent: s.streamingContent + chunk,
      messages: s.messages.map((m) =>
        m.id === s.streamingMessageId
          ? { ...m, content: s.streamingContent + chunk, isStreaming: true }
          : m
      ),
    }));
  },

  addAgentStep: (step) => {
    set((s) => ({
      agentSteps: [...s.agentSteps, step],
      messages: s.messages.map((m) =>
        m.id === s.streamingMessageId
          ? { ...m, agentSteps: [...s.agentSteps, step] }
          : m
      ),
    }));
  },

  addToolCallStep: (step) => {
    set((s) => ({
      toolCallSteps: [...s.toolCallSteps, step],
      messages: s.messages.map((m) =>
        m.id === s.streamingMessageId
          ? { ...m, toolCalls: [...s.toolCallSteps, step] }
          : m
      ),
    }));
  },

  updateToolCallStep: (stepNum, patch) => {
    set((s) => {
      const updated = s.toolCallSteps.map((st) =>
        st.step === stepNum ? { ...st, ...patch } : st
      );
      return {
        toolCallSteps: updated,
        messages: s.messages.map((m) =>
          m.id === s.streamingMessageId ? { ...m, toolCalls: updated } : m
        ),
      };
    });
  },

  finishStreaming: (id) => {
    set((s) => ({
      isStreaming: false,
      streamingContent: "",
      streamingMessageId: null,
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, isStreaming: false } : m
      ),
    }));
  },

  setErrorOnMessage: (id, error) => {
    set((s) => ({
      isStreaming: false,
      streamingContent: "",
      streamingMessageId: null,
      messages: s.messages.map((m) =>
        m.id === id
          ? { ...m, isStreaming: false, isError: true, content: error, retryable: true }
          : m
      ),
    }));
  },

  setAbortController: (ctrl) => {
    const prev = get().abortController;
    if (prev) prev.abort();
    set({ abortController: ctrl });
  },

  stopGeneration: () => {
    const ctrl = get().abortController;
    if (ctrl) ctrl.abort();
    const msgId = get().streamingMessageId;
    set({
      isStreaming: false,
      abortController: null,
      streamingContent: "",
      streamingMessageId: null,
    });
    if (msgId) {
      set((s) => ({
        messages: s.messages.map((m) =>
          m.id === msgId ? { ...m, isStreaming: false } : m
        ),
      }));
    }
  },

  deleteConversation: async (id) => {
    await deleteConv(id);
    set((s) => ({
      conversations: s.conversations.filter((c) => c.session_id !== id),
      messages: s.activeSessionId === id ? [] : s.messages,
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
    }));
  },

  renameConversation: async (id, title) => {
    await renameConv(id, { title });
    set((s) => ({
      conversations: s.conversations.map((c) =>
        c.session_id === id ? { ...c, title } : c
      ),
    }));
  },

  setActivePage: (page) => set({ activePage: page }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  clearMessages: () => set({ messages: [], toolCallSteps: [] }),
}));
