export interface Conversation {
  session_id: string;
  title: string | null;
  last_question: string | null;
  message_count: number;
  updated_at: string;
}

export interface AgentTrace {
  id: number;
  session_id: string;
  question: string | null;
  title: string | null;
  step: number | null;
  action: string | null;
  tool_input: Record<string, unknown> | null;
  tool_output: Record<string, unknown> | null;
  reflection: string | null;
  final_answer: string | null;
  status: string;
  created_at: string;
  updated_at: string | null;
}

export interface ConversationDetail {
  session_id: string;
  title: string | null;
  messages: AgentTrace[];
}

export interface ConversationUpdate {
  title: string;
}

export interface AgentQueryRequest {
  question: string;
  session_id?: string;
}

export interface AgentQueryResponse {
  session_id: string;
  answer: string;
  sources: string[];
  status: "completed" | "failed";
  loop_count: number;
}

export interface DocumentResponse {
  id: number;
  file_path: string;
  title: string | null;
  entities: Record<string, unknown> | null;
  has_tables: boolean;
  data_fields: Record<string, unknown> | null;
  time_range: [string, string] | null;
  hash_checksum: string;
  importance: string;
  domain_id: number | null;
  created_at: string | null;
  processing_status: string;
}

export interface DocumentUploadResponse {
  id: number;
  file_path: string;
  title: string | null;
  importance: string;
  chunk_count: number;
}

export interface KnowledgeDomain {
  id: number;
  name: string;
  description: string | null;
  entry_point: string | null;
  file_count: number;
  updated_at: string;
}

export interface KnowledgeDomainCreate {
  name: string;
  description?: string;
  entry_point?: string;
}

export interface StatsResponse {
  total_documents: number;
  total_domains: number;
  last_processed_date: string | null;
}

export interface ToolCallStep {
  step: number;
  tool: string;
  args: Record<string, unknown>;
  input: string;
  status: "calling" | "success" | "error";
  summary: string;
  resultData?: Record<string, unknown>;
}

export interface AgentStepInfo {
  loop: number;
  maxLoops: number;
  phase: string;
  message: string;
  reasoning?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  toolCalls?: ToolCallStep[];
  agentSteps?: AgentStepInfo[];
  isStreaming?: boolean;
  isError?: boolean;
  retryable?: boolean;
}

export type SSEEventType =
  | "status"
  | "tool_call"
  | "tool_result"
  | "reflection"
  | "answer_start"
  | "answer_chunk"
  | "done"
  | "error";

export interface SSEEvent {
  event: SSEEventType;
  data: Record<string, unknown>;
}
