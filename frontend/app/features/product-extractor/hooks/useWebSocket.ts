import React from "react";
import { useState, useEffect, useRef } from "react";

const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<string[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Only create a new connection if one doesn't exist
    if (!socketRef.current) {
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => console.log("✅ connected to Websocket");
      ws.onmessage = (event) => setMessages((prev) => [...prev, event.data]);
      ws.onclose = () => {
        console.log("❌ disconnected from Websocket");
        socketRef.current = null;
      };
      ws.onerror = (error) => {
        console.log("❌ error", error);
        socketRef.current = null;
      };
    }

    // Cleanup function
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [url]);

  const sendMessage = (message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    }
  };

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.close();
      console.log("❌ disconnected from Websocket");
      socketRef.current = null;
    }
  };

  return { messages, sendMessage, disconnect };
};

export default useWebSocket;
