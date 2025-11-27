import { useState, useEffect, useRef } from "react";

interface SSEOptions {
  url: string;
  token?: string;
}

const useSSE = ({ url, token }: SSEOptions) => {
  const [messages, setMessages] = useState<string[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!eventSourceRef.current) {
      const fullUrl = token ? `${url}&auth=${token}` : url;
      const eventSource = new EventSource(fullUrl);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        console.log("message received on sse", event);
        setMessages((prev) => [...prev, event.data]);
      };

      eventSource.onerror = (error) => {
        console.error("❌ SSE error:", error);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
      };

      eventSource.onopen = () => {
        console.log("✅ SSE connection opened");
      };
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [url, token]);

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      console.log("SSE connection closed");
    }
  };

  return { messages, disconnect };
};

export default useSSE;
