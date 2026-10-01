import { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import api from "./services/api";
import Login from "./components/Login";
import { setAuthToken } from "./services/api";
import LLMDashboard from "./components/LLMDashboard";
import Landing from "./components/Landing";

const getInitialMessages = (userRole) => [
  {
    role: "assistant",
    text:
      userRole === "admin"
        ? "Hello Admin! I am your Trendly Admin Assistant. I can help you review and approve high-value pending returns (> ₹20,000), lookup any customer order, check support tickets, or search policies. How can I help you today?"
        : "Hello! I'm Trendly AI. How can I help you today?",
  },
];

// ── Chat page (protected) ──────────────────────────
function ChatApp({ onLogout, role, messages, onSend, loading }) {
  return (
    <div className="min-h-screen bg-[#F7F7F8] px-4 py-6 sm:px-6 lg:flex lg:items-center lg:px-8">
      <div className="mx-auto flex w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-[#E5E7EB] bg-white shadow-sm lg:h-[calc(100dvh-3rem)]">
        <div className="border-b border-blue-700 bg-[#2563EB] px-6 py-4 text-white sm:px-7 sm:py-5 flex justify-between items-center">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">Trendly AI Support Assistant</h1>
              {role === "admin" && (
                <span className="rounded-full bg-amber-400 text-blue-950 px-2.5 py-0.5 text-xs font-extrabold uppercase tracking-wider shadow-sm">
                  Admin Console
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-blue-100">
              {role === "admin"
                ? "Administrative Operations & Return Approval Console"
                : "Agentic Customer Support powered by Gemini + MongoDB Atlas"}
            </p>
          </div>
          <button onClick={onLogout} className="rounded-lg bg-blue-700 hover:bg-blue-800 px-4 py-2 text-sm font-semibold transition cursor-pointer">
            Logout
          </button>
        </div>
        <div className="flex min-h-0 flex-1 flex-col gap-4 px-5 pb-5 pt-4 sm:px-7 sm:pb-6 sm:pt-5">
          <ChatWindow messages={messages} />
          <ChatInput onSend={onSend} loading={loading} />
        </div>
      </div>
    </div>
  );
}

// ── Root app with state ────────────────────────────
export default function App() {
  const [authToken, setAuthTokenState] = useState(null);
  const [role, setRole] = useState(null);
  const [customerChats, setCustomerChats] = useState({ "C-101": getInitialMessages(null) });
  const [loading, setLoading] = useState(false);
  const customerId = "C-101";

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedRole = localStorage.getItem("role");
    if (token) {
      setAuthToken(token);
      setAuthTokenState(token);
      setRole(storedRole);
      setCustomerChats({ [customerId]: getInitialMessages(storedRole) });
    }
  }, []);

  useEffect(() => {
    if (authToken) {
      api.get("/chat/history").then(({ data }) => {
        const msgs = data.messages || [];
        setCustomerChats((prev) => ({
          ...prev,
          [customerId]: msgs.length > 0
            ? msgs.map((m) => ({ role: m.role === "human" ? "user" : "assistant", text: m.text }))
            : getInitialMessages(role),
        }));
      }).catch(() => {});
    }
  }, [authToken, role]);

  const handleLogin = (token, userRole) => {
    localStorage.setItem("token", token);
    localStorage.setItem("role", userRole);
    setAuthToken(token);
    setAuthTokenState(token);
    setRole(userRole);
    setCustomerChats({ [customerId]: getInitialMessages(userRole) });
  };

  const handleLogout = (navigate) => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setAuthToken(null);
    setAuthTokenState(null);
    setRole(null);
    setCustomerChats({ [customerId]: getInitialMessages(null) });
    navigate("/");
  };

  const handleSend = async (message) => {
    setCustomerChats((prev) => ({
      ...prev,
      [customerId]: [...(prev[customerId] ?? getInitialMessages(role)), { role: "user", text: message }],
    }));
    setLoading(true);
    try {
      const { data } = await api.post("/chat", { message, customerId });
      setCustomerChats((prev) => ({
        ...prev,
        [customerId]: [...(prev[customerId] ?? getInitialMessages(role)), { role: "assistant", text: data.response }],
      }));
    } catch {
      setCustomerChats((prev) => ({
        ...prev,
        [customerId]: [...(prev[customerId] ?? getInitialMessages(role)), { role: "assistant", text: "Sorry, something went wrong while contacting the server." }],
      }));
    } finally {
      setLoading(false);
    }
  };

  const messages = customerChats[customerId] ?? getInitialMessages(role);

  return (
    <Routes>
      {/* Public landing */}
      <Route path="/" element={<LandingGate authToken={authToken} />} />

      {/* Public LLM report */}
      <Route path="/llm-report" element={<LLMDashboard />} />

      {/* Login page */}
      <Route path="/login" element={<LoginGate authToken={authToken} onLogin={handleLogin} />} />

      {/* Protected chat */}
      <Route
        path="/chat"
        element={
          authToken
            ? <ChatGate role={role} messages={messages} onSend={handleSend} loading={loading} onLogout={handleLogout} />
            : <RedirectTo to="/login" />
        }
      />
    </Routes>
  );
}

// ── Small helper components with navigate access ───
function LandingGate({ authToken }) {
  const navigate = useNavigate();
  return (
    <Landing
      onLaunchChat={() => {
        if (authToken) {
          navigate("/chat");
        } else {
          navigate("/login");
        }
      }}
      onGoToLogin={(prefillEmail) => {
        if (typeof prefillEmail === "string") {
          navigate("/login", { state: { email: prefillEmail } });
        } else if (authToken) {
          navigate("/chat");
        } else {
          navigate("/login");
        }
      }}
    />
  );
}

function LoginGate({ authToken, onLogin }) {
  const navigate = useNavigate();
  if (authToken) { navigate("/chat"); return null; }
  return (
    <Login
      onLogin={(token, role) => {
        onLogin(token, role);
        navigate("/chat");
      }}
    />
  );
}

function ChatGate({ role, messages, onSend, loading, onLogout }) {
  const navigate = useNavigate();
  return <ChatApp role={role} messages={messages} onSend={onSend} loading={loading} onLogout={() => onLogout(navigate)} />;
}

function RedirectTo({ to }) {
  const navigate = useNavigate();
  useEffect(() => { navigate(to); }, []);
  return null;
}



