import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div className="min-h-[220px] flex-1 overflow-y-auto rounded-xl border border-[#E5E7EB] bg-[#F9F9F9] p-5 sm:min-h-[260px] sm:p-6">
      <div className="space-y-5">
        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            role={message.role}
            text={message.text}
          />
        ))}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
