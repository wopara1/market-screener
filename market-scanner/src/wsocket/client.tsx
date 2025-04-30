import React, { useEffect, useState } from "react";
import WebSocketManager from "./manager";

interface Message {
  text: string;
}

const WebSocketComponent: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const wsManager = new WebSocketManager("ws://127.0.0.1:8000/ws");

  useEffect(() => {
    wsManager.connect();

    // Add a listener for the "message" event
    wsManager.addListener("message", (payload: Message) => {
      setMessages((prevMessages) => [...prevMessages, payload]);
    });

    return () => {
      wsManager.disconnect();
    };
  }, []);

  const sendMessage = () => {
    wsManager.sendMessage("message", { text: "Hello, server!" });
  };

  return (
    <div>
      <button
        onClick={sendMessage}
        style={{
          backgroundColor: "#0078D4", // Azure blue color
          color: "white",
          border: "1px solid #005A9E", // Darker blue border
          borderRadius: "4px",
          padding: "8px 16px",
          cursor: "pointer",
        }}
      >
        Send Message
      </button>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg.text}</li>
        ))}
      </ul>
    </div>
  );
};

export default WebSocketComponent;