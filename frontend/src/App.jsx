import { useEffect, useState } from "react";
import CustomerSelector from "./components/CustomerSelector";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import api from "./services/api";
import Login from "./components/Login";
import { setAuthToken } from "./services/api";

const initialMessages = [
  {
    role: "assistant",
    text: "Hello! I'm Trendly AI. How can I help you today?",
  },
];

export default function App() {
  const [authToken, setAuthTokenState] = useState(null);
  const [role, setRole] = useState(null);

  const [customerId, setCustomerId] = useState("C-101");

  const [customerChats, setCustomerChats] = useState({
    "C-101": initialMessages,
  });

  const [loading, setLoading] = useState(false);

  // Load token from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedRole = localStorage.getItem("role");
    if (token) {
      setAuthToken(token);
      setAuthTokenState(token);
      setRole(storedRole);
    }
  }, []);

  const handleLogin = (token, userRole) => {
    localStorage.setItem("token", token);
    localStorage.setItem("role", userRole);
    setAuthToken(token);
    setAuthTokenState(token);
    setRole(userRole);
  };

  // Current customer's conversation
  const messages = customerChats[customerId] ?? initialMessages;

  // Create a chat history for a customer the first time they're selected
  useEffect(() => {
    setCustomerChats((prev) => {
      if (prev[customerId]) return prev;

      return {
        ...prev,
        [customerId]: initialMessages,
      };
    });
  }, [customerId]);

  const handleSend = async (message) => {
    // Show user message immediately
    setCustomerChats((prev) => ({
      ...prev,
      [customerId]: [
        ...(prev[customerId] ?? initialMessages),
        {
          role: "user",
          text: message,
        },
      ],
    }));

    setLoading(true);

    try {
      const { data } = await api.post("/chat", {
        message,
        customerId,
      });

      setCustomerChats((prev) => ({
        ...prev,
        [customerId]: [
          ...(prev[customerId] ?? initialMessages),
          {
            role: "assistant",
            text: data.response,
          },
        ],
      }));
    } catch (error) {
      console.error(error);

      setCustomerChats((prev) => ({
        ...prev,
        [customerId]: [
          ...(prev[customerId] ?? initialMessages),
          {
            role: "assistant",
            text: "Sorry, something went wrong while contacting the server.",
          },
        ],
      }));
    } finally {
      setLoading(false);
    }
  };

  // If not logged in, show login screen
  if (!authToken) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-[#F7F7F8] px-4 py-6 sm:px-6 lg:flex lg:items-center lg:px-8">
      <div className="mx-auto flex w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-[#E5E7EB] bg-white shadow-sm lg:h-[calc(100dvh-3rem)]">

        {/* Header */}
        <div className="border-b border-blue-700 bg-[#2563EB] px-6 py-4 text-white sm:px-7 sm:py-5">
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Trendly AI Support Assistant
          </h1>

          <p className="mt-1 text-sm text-blue-100">
            Agentic Customer Support powered by Gemini + MongoDB Atlas
          </p>
        </div>

        {/* Content */}
        <div className="flex min-h-0 flex-1 flex-col gap-4 px-5 pb-5 pt-4 sm:px-7 sm:pb-6 sm:pt-5">

          <CustomerSelector
            customerId={customerId}
            setCustomerId={setCustomerId}
          />

          <ChatWindow messages={messages} />

          <ChatInput
            onSend={handleSend}
            loading={loading}
          />

        </div>
      </div>
    </div>
  );
}
