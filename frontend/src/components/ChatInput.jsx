import { useState } from "react";

export default function ChatInput({ onSend, loading }) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!message.trim() || loading) return;

    onSend(message);
    setMessage("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="shrink-0 flex flex-col gap-3 border-t border-[#E5E7EB] pt-5 sm:flex-row sm:pt-6"
    >
      <input
        type="text"
        placeholder="Ask about your order..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="min-w-0 flex-1 rounded-xl border border-[#E5E7EB] bg-white px-5 py-3.5 text-base text-[#111827] placeholder:text-[#6B7280] transition-all duration-200 hover:bg-[#F9F9F9] focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
      />

      <button
        type="submit"
        disabled={loading}
        className="rounded-xl bg-[#2563EB] px-7 py-3.5 text-base font-semibold text-white shadow-sm transition-all duration-200 hover:bg-blue-700 active:scale-95 focus:outline-none focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-500 disabled:shadow-none"
      >
        {loading ? "Sending..." : "Send"}
      </button>
    </form>
  );
}
