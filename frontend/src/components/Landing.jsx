import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

const features = [
  { icon: "🤖", title: "Agentic AI", desc: "LangChain agent with dynamic tool-calling for orders, returns & policy" },
  { icon: "🔍", title: "RAG-Powered", desc: "MongoDB Vector Search grounds every answer in official Trendly policy" },
  { icon: "⚡", title: "Gemini + Groq", desc: "Primary cloud LLM with automatic Groq fallback on quota exhaustion" },
  { icon: "🦙", title: "Ollama Ready", desc: "Swap to local Mistral 7B in one line — zero data egress, full privacy" },
  { icon: "🔒", title: "JWT Auth", desc: "Role-based access: Customer, Support Agent, and Admin consoles" },
  { icon: "📊", title: "LLM Benchmark", desc: "Live comparison: Cloud vs Local — quality, latency, cost, privacy" },
];

const accounts = [
  { role: "Admin", email: "admin@trendly.com", color: "#f59e0b", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.3)" },
  { role: "Agent", email: "agent@trendly.com", color: "#34d399", bg: "rgba(52,211,153,0.12)", border: "rgba(52,211,153,0.3)" },
  { role: "Customer", email: "marcus.bell@example.com", color: "#60a5fa", bg: "rgba(96,165,250,0.12)", border: "rgba(96,165,250,0.3)" },
];

export default function Landing({ onGoToLogin, onLaunchChat }) {
  const navigate = useNavigate();
  const [tick, setTick] = useState(0);

  // Animate the rotating badge
  useEffect(() => {
    const t = setInterval(() => setTick((x) => x + 1), 3000);
    return () => clearInterval(t);
  }, []);

  const badges = ["Gemini 2.5 Flash", "Ollama Mistral 7B", "Groq LLaMA 3.3", "MongoDB RAG"];

  const handleLaunch = () => {
    if (onLaunchChat) {
      onLaunchChat();
    } else if (onGoToLogin) {
      onGoToLogin();
    } else {
      navigate("/chat");
    }
  };

  const handleSignIn = () => {
    if (onGoToLogin) {
      onGoToLogin();
    } else {
      navigate("/login");
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#0f0c29 0%,#1a1040 40%,#0d1b3e 100%)", fontFamily: "'Inter',sans-serif", color: "#e2e8f0", overflowX: "hidden" }}>

      {/* ── NAV ─────────────────────────────────────── */}
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 32px", borderBottom: "1px solid rgba(255,255,255,0.07)", position: "sticky", top: 0, zIndex: 100, background: "rgba(15,12,41,0.85)", backdropFilter: "blur(12px)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🤖</div>
          <span style={{ fontWeight: 800, fontSize: 18, background: "linear-gradient(90deg,#a78bfa,#60a5fa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Trendly AI</span>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={() => navigate("/llm-report")}
            style={{ padding: "8px 18px", borderRadius: 10, border: "1px solid rgba(167,139,250,0.4)", background: "transparent", color: "#a78bfa", fontWeight: 600, fontSize: 13, cursor: "pointer", transition: "all 0.2s" }}
            onMouseEnter={e => { e.target.style.background = "rgba(167,139,250,0.1)"; }}
            onMouseLeave={e => { e.target.style.background = "transparent"; }}
          >
            📊 LLM Report
          </button>
          <button
            onClick={handleSignIn}
            style={{ padding: "8px 20px", borderRadius: 10, border: "none", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", color: "#fff", fontWeight: 700, fontSize: 13, cursor: "pointer", boxShadow: "0 4px 14px rgba(99,102,241,0.4)", transition: "opacity 0.2s" }}
            onMouseEnter={e => { e.target.style.opacity = "0.85"; }}
            onMouseLeave={e => { e.target.style.opacity = "1"; }}
          >
            Sign In →
          </button>
        </div>
      </nav>

      {/* ── HERO ────────────────────────────────────── */}
      <section style={{ textAlign: "center", padding: "80px 24px 60px", position: "relative" }}>
        {/* glow blobs */}
        <div style={{ position: "absolute", top: 60, left: "20%", width: 300, height: 300, background: "rgba(99,102,241,0.15)", borderRadius: "50%", filter: "blur(80px)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", top: 40, right: "20%", width: 250, height: 250, background: "rgba(139,92,246,0.12)", borderRadius: "50%", filter: "blur(70px)", pointerEvents: "none" }} />

        {/* rotating badge */}
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.35)", borderRadius: 999, padding: "6px 18px", fontSize: 12, color: "#a5b4fc", fontWeight: 600, marginBottom: 28, letterSpacing: 0.5 }}>
          <span style={{ width: 7, height: 7, background: "#6ee7b7", borderRadius: "50%", display: "inline-block", animation: "pulse 1.5s infinite" }} />
          Now running · {badges[tick % badges.length]}
        </div>

        <h1 style={{ fontSize: "clamp(2rem,5vw,3.6rem)", fontWeight: 900, lineHeight: 1.15, margin: "0 0 20px", maxWidth: 700, marginInline: "auto" }}>
          <span style={{ background: "linear-gradient(90deg,#a78bfa,#60a5fa,#34d399)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Trendly AI
          </span>
          <br />
          <span style={{ color: "#e2e8f0" }}>Agentic Support Assistant</span>
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "clamp(15px,2vw,17px)", maxWidth: 540, marginInline: "auto", lineHeight: 1.7, marginBottom: 40 }}>
          An AI-powered customer support agent built with LangChain, FastAPI, RAG, and swappable LLMs — from cloud Gemini to local Mistral.
        </p>

        {/* CTA buttons */}
        <div style={{ display: "flex", gap: 14, justifyContent: "center", flexWrap: "wrap" }}>
          <button
            onClick={handleLaunch}
            style={{ padding: "14px 36px", borderRadius: 14, border: "none", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", color: "#fff", fontWeight: 800, fontSize: 16, cursor: "pointer", boxShadow: "0 6px 24px rgba(99,102,241,0.45)", transition: "transform 0.15s, box-shadow 0.15s" }}
            onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 10px 30px rgba(99,102,241,0.5)"; }}
            onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 6px 24px rgba(99,102,241,0.45)"; }}
          >
            🚀 Launch Chat App
          </button>
          <button
            onClick={() => navigate("/llm-report")}
            style={{ padding: "14px 36px", borderRadius: 14, border: "1px solid rgba(167,139,250,0.4)", background: "rgba(167,139,250,0.08)", color: "#ddd6fe", fontWeight: 700, fontSize: 16, cursor: "pointer", transition: "all 0.15s" }}
            onMouseEnter={e => { e.currentTarget.style.background = "rgba(167,139,250,0.16)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "rgba(167,139,250,0.08)"; e.currentTarget.style.transform = "translateY(0)"; }}
          >
            📊 View LLM Comparison
          </button>
        </div>
      </section>

      {/* ── FEATURES GRID ───────────────────────────── */}
      <section style={{ maxWidth: 1000, margin: "0 auto", padding: "0 24px 70px" }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: "#e2e8f0", margin: 0 }}>What's inside</h2>
          <p style={{ color: "#64748b", fontSize: 14, marginTop: 8 }}>Everything wired up and ready to explore</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 16 }}>
          {features.map((f) => (
            <div
              key={f.title}
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: "22px 22px", transition: "border-color 0.2s, transform 0.2s" }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(99,102,241,0.5)"; e.currentTarget.style.transform = "translateY(-3px)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{ fontSize: 28, marginBottom: 10 }}>{f.icon}</div>
              <div style={{ fontWeight: 700, fontSize: 15, color: "#e2e8f0", marginBottom: 6 }}>{f.title}</div>
              <div style={{ fontSize: 13, color: "#64748b", lineHeight: 1.6 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── TEST ACCOUNTS ───────────────────────────── */}
      <section style={{ maxWidth: 680, margin: "0 auto", padding: "0 24px 80px" }}>
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 18, padding: "28px 28px" }}>
          <h2 style={{ margin: "0 0 6px", fontSize: 18, fontWeight: 800, color: "#e2e8f0" }}>🔐 Demo Accounts</h2>
          <p style={{ margin: "0 0 22px", color: "#64748b", fontSize: 13 }}>No password required — just enter the email and sign in</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {accounts.map((a) => (
              <div
                key={a.role}
                onClick={() => onGoToLogin(a.email)}
                style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: a.bg, border: `1px solid ${a.border}`, borderRadius: 12, padding: "12px 16px", cursor: "pointer", transition: "opacity 0.15s" }}
                onMouseEnter={e => { e.currentTarget.style.opacity = "0.8"; }}
                onMouseLeave={e => { e.currentTarget.style.opacity = "1"; }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: 13, color: a.color }}>{a.role}</div>
                  <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 2 }}>{a.email}</div>
                </div>
                <span style={{ color: a.color, fontSize: 18 }}>→</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────── */}
      <div style={{ textAlign: "center", color: "#334155", fontSize: 12, paddingBottom: 32 }}>
        Trendly AI Support · §5 LLM Decision Framework · Built with LangChain + FastAPI + React
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}
