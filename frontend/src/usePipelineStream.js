import { useCallback, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

/**
 * Streams the multi-agent pipeline via fetch() + ReadableStream.
 *
 * Why fetch() instead of the native EventSource API: EventSource only
 * supports GET requests, but our backend needs a POST body (the user's
 * message), so we parse the text/event-stream format ourselves.
 *
 * Returns:
 *  - stages: ordered list of { node, output, status } as they arrive
 *  - finalOutput: the pipeline's final result text (once done)
 *  - isStreaming: true while a request is in flight
 *  - error: any stream-level error message
 *  - run(message, threadId): starts a new streaming run
 */
export function usePipelineStream() {
  const [stages, setStages] = useState([]);
  const [finalOutput, setFinalOutput] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const run = useCallback(async (message, threadId) => {
    // Reset state for a fresh run
    setStages([]);
    setFinalOutput(null);
    setError(null);
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_BASE}/api/agent/auto/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, thread_id: threadId }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE events are separated by a blank line
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const rawEvent of events) {
          if (!rawEvent.trim()) continue;
          const eventTypeMatch = rawEvent.match(/^event:\s*(.+)$/m);
          const dataMatch = rawEvent.match(/^data:\s*(.+)$/m);
          if (!dataMatch) continue;

          const eventType = eventTypeMatch ? eventTypeMatch[1].trim() : "message";
          let payload;
          try {
            payload = JSON.parse(dataMatch[1]);
          } catch {
            continue;
          }

          handleEvent(eventType, payload, setStages, setFinalOutput, setError);
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message || "Stream connection failed");
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { stages, finalOutput, isStreaming, error, run, cancel };
}

function handleEvent(eventType, payload, setStages, setFinalOutput, setError) {
  switch (eventType) {
    case "start":
      // Pipeline acknowledged - nothing to render yet
      break;

    case "node_update": {
      const { node, output } = payload;
      setStages((prev) => {
        const next = [...prev];
        const existingIndex = next.findIndex((s) => s.node === node);
        const stage = { node, output, status: "done" };
        if (existingIndex >= 0) {
          next[existingIndex] = stage;
        } else {
          next.push(stage);
        }
        return next;
      });
      break;
    }

    case "final":
      setFinalOutput(payload.final_output || "");
      break;

    case "error":
      setError(payload.message || "Pipeline error");
      break;

    case "done":
      // Stream finished - isStreaming flips in the finally block
      break;

    default:
      break;
  }
}
