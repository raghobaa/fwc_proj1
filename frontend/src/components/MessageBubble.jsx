export default function MessageBubble({ role, text }) {
  const isUser = role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm sm:max-w-[58%] ${
          isUser
            ? "rounded-br-md bg-[#2563EB] text-white shadow-blue-200"
            : "rounded-bl-md border border-[#E5E7EB] bg-white text-[#111827]"
        }`}
      >
        <p className="whitespace-pre-wrap">
          {text}
        </p>
      </div>
    </div>
  );
}
