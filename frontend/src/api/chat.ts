import { request } from "./client";
import type {
  AgentQueryRequest,
  AgentQueryResponse,
  AgentTrace,
  Conversation,
  ConversationDetail,
  ConversationUpdate,
  StatsResponse,
} from "../types";

export function queryAgentSync(
  body: AgentQueryRequest
): Promise<AgentQueryResponse> {
  return request<AgentQueryResponse>("/agent/query/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function getTraces(sessionId: string): Promise<AgentTrace[]> {
  return request<AgentTrace[]>(`/agent/traces/${sessionId}`);
}

export function listConversations(): Promise<Conversation[]> {
  return request<Conversation[]>("/conversations");
}

export function getConversation(
  sessionId: string
): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/conversations/${sessionId}`);
}

export function renameConversation(
  sessionId: string,
  body: ConversationUpdate
): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/conversations/${sessionId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function deleteConversation(sessionId: string): Promise<void> {
  return request<void>(`/conversations/${sessionId}`, {
    method: "DELETE",
  });
}

export function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/stats");
}
