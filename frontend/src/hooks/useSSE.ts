import { useCallback, useRef } from "react";
import { useChatStore } from "../stores/chatStore";
import { sseStream } from "../api/sse";

export function useSSE() {
  const store = useChatStore();
  const storeRef = useRef(store);
  storeRef.current = store;

  const sendMessage = useCallback(
    async (content: string, sessionId: string) => {
      const s = storeRef.current;

      const userMsgId = `user-${Date.now()}`;
      const aiMsgId = `ai-${Date.now()}`;

      s.addMessage({
        id: userMsgId,
        role: "user",
        content,
        timestamp: Date.now(),
      });

      s.addMessage({
        id: aiMsgId,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
        isStreaming: true,
        toolCalls: [],
        agentSteps: [],
      });

      s.startStreaming(aiMsgId);

      const controller = new AbortController();
      s.setAbortController(controller);

      try {
        for await (const evt of sseStream(
          "agent/query",
          {
            question: content,
            session_id: sessionId,
          },
          controller.signal
        )) {
          if (controller.signal.aborted) break;

          const current = storeRef.current;
          switch (evt.event) {
            case "status": {
              const data = evt.data as Record<string, unknown>;
              const loop = data.loop_count as number;
              const maxLoops = data.max_loops as number;
              const phase = (data.phase as string) || "";
              const message = (data.message as string) || "";
              if (phase !== "starting") {
                current.addAgentStep({
                  loop,
                  maxLoops,
                  phase,
                  message,
                });
              }
              break;
            }

            case "tool_call": {
              const data = evt.data as Record<string, unknown>;
              const step = data.step as number;
              const tool = data.tool as string;
              const args = data.args as Record<string, unknown>;
              const reasoning = (data.reasoning as string) || "";

              current.addToolCallStep({
                step,
                tool,
                args,
                input: JSON.stringify(args),
                status: "calling",
                summary: reasoning,
              });
              break;
            }

            case "tool_result": {
              const data = evt.data as Record<string, unknown>;
              const step = data.step as number;
              const status = data.status as string;
              const summary = (data.summary as string) || "";
              const resultData = data.result as Record<string, unknown> | undefined;

              current.updateToolCallStep(step, {
                status: status === "success" ? "success" : "error",
                summary,
                resultData,
              });
              break;
            }

            case "reflection": {
              const data = evt.data as Record<string, unknown>;
              const step = data.step as number;
              const result = (data.result as string) || "";
              const message = (data.message as string) || result;
              current.addAgentStep({
                loop: step,
                maxLoops: 5,
                phase: "reflection",
                message: `反思: ${message}`,
              });
              break;
            }

            case "answer_start":
              current.addAgentStep({
                loop: 0,
                maxLoops: 0,
                phase: "answering",
                message: "正在生成答案...",
              });
              break;

            case "answer_chunk": {
              const data = evt.data as Record<string, unknown>;
              const chunk = (data.content as string) || "";
              current.appendStreamContent(chunk);
              break;
            }

            case "done": {
              const data = evt.data as Record<string, unknown>;
              const status = data.status as string;
              if (status === "failed") {
                const answer = (data.answer as string) || "无法完成查询，请重试";
                current.updateMessage(aiMsgId, {
                  content: answer,
                  isStreaming: false,
                });
              }
              current.finishStreaming(aiMsgId);
              current.setAbortController(null);
              current.loadConversations();
              return;
            }

            case "error": {
              const data = evt.data as Record<string, unknown>;
              current.setErrorOnMessage(aiMsgId, (data.error as string) || "Unknown error");
              current.setAbortController(null);
              return;
            }
          }
        }

        // If we got here without a done event (stream ended abruptly)
        const final = storeRef.current;
        if (final.isStreaming) {
          final.finishStreaming(aiMsgId);
          final.setAbortController(null);
          final.loadConversations();
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          const msg = err instanceof Error ? err.message : "Request failed";
          storeRef.current.setErrorOnMessage(aiMsgId, msg);
          storeRef.current.setAbortController(null);
        }
      }
    },
    []
  );

  return { sendMessage };
}
