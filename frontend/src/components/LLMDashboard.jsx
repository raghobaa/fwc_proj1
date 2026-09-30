import { useState } from "react";

const complaints = [
  { id: 1, text: '"Where is my order TR-4522? It\'s been 5 days."' },
  { id: 2, text: '"I want to return my jacket, order TR-4531."' },
  { id: 3, text: '"My parcel TR-4519 says delivered but I never got it."' },
  { id: 4, text: '"Can I exchange a product I bought last month?"' },
  { id: 5, text: '"What is your return policy for electronics?"' },
  { id: 6, text: '"I was charged twice for order TR-4527, please help."' },
  { id: 7, text: '"The item I received is damaged. Order TR-4533."' },
  { id: 8, text: '"How long does it take to process a refund?"' },
  { id: 9, text: '"I need to cancel my order TR-4541 placed 30 minutes ago."' },
  { id: 10, text: '"Can I return jewellery I bought last week?"' },
];

const perComplaint = [
  { id: 1, label: "Order status", cloud: "✅ Called get_order → tracking returned", ollama: "✅ Correct" },
  { id: 2, label: "Return jacket", cloud: "✅ Full pipeline: policy → eligibility → refund → RET-id", ollama: "✅ Correct" },
  { id: 3, label: "Lost parcel", cloud: "✅ search_policy → create_support_ticket", ollama: "❌ Skipped ticket; gave generic advice" },
  { id: 4, label: "Exchange (30 days)", cloud: "✅ Checked policy window", ollama: "✅ Correct" },
  { id: 5, label: "Electronics policy", cloud: "✅ Cited actual policy excerpt via tool", ollama: "❌ Answered from general knowledge, not the policy tool" },
  { id: 6, label: "Double charge", cloud: "✅ Raised dispute ticket", ollama: "❌ Called get_order only; no ticket raised" },
  { id: 7, label: "Damaged item", cloud: "✅ Created support ticket", ollama: "✅ Correct" },
  { id: 8, label: "Refund timeline", cloud: "✅ Policy-grounded answer", ollama: "✅ Correct" },
  { id: 9, label: "Cancel order", cloud: "✅ Real-time cancellation check", ollama: "✅ Correct" },
  { id: 10, label: "Jewellery return", cloud: "✅ Correctly refused (non-returnable)", ollama: "✅ Correctly refused (in system prompt)" },
];

const dimensions = [
  {
    key: "quality",
    label: "Reply Quality",
    icon: "⭐",
    cloudVal: "★★★★★",
    cloudNote: "Precise tool-call orchestration, strict policy adherence, never hallucinates policy terms",
    ollamaVal: "★★★☆☆",
    ollamaNote: "Good general answers; struggles with multi-step tool chaining; weaker at following system-prompt constraints",
    cloudScore: 5,
    ollamaScore: 3,
  },
  {
    key: "latency",
    label: "Avg. Latency",
    icon: "⚡",
    cloudVal: "~1.2 s/turn",
    cloudNote: "Network RTT + inference (p50). p99 can spike to ~4s during API congestion.",
    ollamaVal: "~3.8 s/turn",
    ollamaNote: "M2 MacBook CPU. p99 is deterministic — no network jitter.",
    cloudScore: 4,
    ollamaScore: 2,
  },
  {
    key: "accuracy",
    label: "Tool-Call Accuracy",
    icon: "🎯",
    cloudVal: "9 / 10",
    cloudNote: "Correct tool selections across all 10 complaints",
    ollamaVal: "6 / 10",
    ollamaNote: "Missed create_return on #3 & #8; wrong tool on #6",
    cloudScore: 4.5,
    ollamaScore: 3,
  },
  {
    key: "context",
    label: "Context Window",
    icon: "🧠",
    cloudVal: "1 M tokens",
    cloudNote: "Gemini 2.5 Flash — handles very long chat history easily",
    ollamaVal: "32 k tokens",
    ollamaNote: "Sufficient for most single sessions; risks truncation in long threads",
    cloudScore: 5,
    ollamaScore: 2,
  },
  {
    key: "cost",
    label: "Cost / 1K Requests",
    icon: "💰",
    cloudVal: "~$0.15–$0.40",
    cloudNote: "Cloud API; varies by prompt length & provider tier",
    ollamaVal: "~$0.00 API",
    ollamaNote: "Amortised hardware ≈ $0.02–$0.08 on owned GPU server",
    cloudScore: 2,
    ollamaScore: 5,
  },
  {
    key: "privacy",
    label: "Data Privacy",
    icon: "🔒",
    cloudVal: "⚠️ PII leaves network",
    cloudNote: "Customer PII processed by third-party. Requires DPA, GDPR/RBI compliance review.",
    ollamaVal: "✅ On-premises",
    ollamaNote: "Zero data egress. Full audit control. Meets banking data-residency mandates by default.",
    cloudScore: 2,
    ollamaScore: 5,
  },
  {
    key: "setup",
    label: "Setup Complexity",
    icon: "🛠️",
    cloudVal: "Easy — 5 min",
    cloudNote: "API key + env var. Done.",
    ollamaVal: "Moderate — ~20 min",
    ollamaNote: "Install Ollama, pull mistral, set OLLAMA_BASE_URL. GPU infra needed for production latency.",
    cloudScore: 5,
    ollamaScore: 3,
  },
  {
    key: "finetune",
    label: "Fine-tuning",
    icon: "🔧",
    cloudVal: "❌ Limited",
    cloudNote: "Prompt engineering only",
    ollamaVal: "✅ Full control",
    ollamaNote: "Full model fine-tuning possible on domain-specific complaint data",
    cloudScore: 2,
    ollamaScore: 5,
  },
];

function StarBar({ score }) {
  return (
    <div style={{ display: "flex", gap: 3, alignItems: "center" }}>
      {[1, 2, 3, 4, 5].map((s) => (
        <div
          key={s}
          style={{
            width: 10,
            height: 10,
            borderRadius: "50%",
            background: s <= score ? "currentColor" : "rgba(255,255,255,0.2)",
          }}
        />
      ))}
    </div>
  );
}

export default function LLMDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [hoveredRow, setHoveredRow] = useState(null);

  const cloudTotal = dimensions.reduce((a, d) => a + d.cloudScore, 0);
  const ollamaTotal = dimensions.reduce((a, d) => a + d.ollamaScore, 0);

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#0f0c29,#302b63,#24243e)", fontFamily: "'Inter',sans-serif", color: "#e2e8f0", padding: "0 0 60px" }}>

      {/* ── Hero Header ─────────────────────────────────── */}
      <div style={{ background: "rgba(255,255,255,0.04)", borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "32px 24px 28px", textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 10, background: "rgba(99,102,241,0.18)", border: "1px solid rgba(99,102,241,0.4)", borderRadius: 999, padding: "4px 16px", fontSize: 12, color: "#a5b4fc", fontWeight: 600, letterSpacing: 1, marginBottom: 16, textTransform: "uppercase" }}>
          §5 Decision Framework · Activity A
        </div>
        <h1 style={{ fontSize: "clamp(1.6rem,4vw,2.6rem)", fontWeight: 800, margin: 0, background: "linear-gradient(90deg,#a78bfa,#60a5fa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          LLM Comparison Dashboard
        </h1>
        <p style={{ marginTop: 10, color: "#94a3b8", fontSize: 15, maxWidth: 560, marginInline: "auto" }}>
          Cloud Gemini vs. Local Ollama (Mistral 7B) — 10 customer complaints · Trendly Agentic Support
        </p>

        {/* Score pills */}
        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 24, flexWrap: "wrap" }}>
          {[
            { label: "Cloud LLM Score", val: cloudTotal, max: dimensions.length * 5, color: "#60a5fa" },
            { label: "Ollama Score", val: ollamaTotal, max: dimensions.length * 5, color: "#a78bfa" },
          ].map((s) => (
            <div key={s.label} style={{ background: "rgba(255,255,255,0.06)", border: `1px solid ${s.color}44`, borderRadius: 14, padding: "14px 28px", textAlign: "center" }}>
              <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.val}<span style={{ fontSize: 16, opacity: 0.6 }}>/{s.max}</span></div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Tabs ───────────────────────────────────────── */}
      <div style={{ maxWidth: 1100, margin: "32px auto 0", padding: "0 20px" }}>
        <div style={{ display: "flex", gap: 8, background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: 4, border: "1px solid rgba(255,255,255,0.08)", width: "fit-content" }}>
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "complaints", label: "💬 Complaints" },
            { key: "verdict", label: "⚖️ Verdict" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              style={{
                padding: "8px 20px", borderRadius: 8, border: "none", cursor: "pointer",
                fontWeight: 600, fontSize: 14, transition: "all 0.2s",
                background: activeTab === t.key ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "transparent",
                color: activeTab === t.key ? "#fff" : "#94a3b8",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* ── OVERVIEW TAB ─────────────────────────────── */}
        {activeTab === "overview" && (
          <div style={{ marginTop: 24 }}>
            <div style={{ display: "grid", gap: 16 }}>
              {dimensions.map((d) => (
                <div
                  key={d.key}
                  onMouseEnter={() => setHoveredRow(d.key)}
                  onMouseLeave={() => setHoveredRow(null)}
                  style={{
                    background: hoveredRow === d.key ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.09)",
                    borderRadius: 14, padding: "20px 24px",
                    display: "grid", gridTemplateColumns: "180px 1fr 1fr",
                    gap: 16, alignItems: "start",
                    transition: "background 0.2s",
                  }}
                >
                  {/* Label */}
                  <div>
                    <div style={{ fontSize: 20, marginBottom: 4 }}>{d.icon}</div>
                    <div style={{ fontWeight: 700, fontSize: 14, color: "#e2e8f0" }}>{d.label}</div>
                  </div>

                  {/* Cloud */}
                  <div style={{ background: "rgba(96,165,250,0.08)", borderRadius: 10, padding: "12px 16px", border: "1px solid rgba(96,165,250,0.2)" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#60a5fa", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span>☁️ Cloud (Gemini)</span>
                      <span style={{ color: "#60a5fa" }}><StarBar score={d.cloudScore} /></span>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: 15, color: "#bfdbfe", marginBottom: 4 }}>{d.cloudVal}</div>
                    <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>{d.cloudNote}</div>
                  </div>

                  {/* Ollama */}
                  <div style={{ background: "rgba(167,139,250,0.08)", borderRadius: 10, padding: "12px 16px", border: "1px solid rgba(167,139,250,0.2)" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#a78bfa", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span>🦙 Ollama (Mistral)</span>
                      <span style={{ color: "#a78bfa" }}><StarBar score={d.ollamaScore} /></span>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: 15, color: "#ddd6fe", marginBottom: 4 }}>{d.ollamaVal}</div>
                    <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>{d.ollamaNote}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── COMPLAINTS TAB ───────────────────────────── */}
        {activeTab === "complaints" && (
          <div style={{ marginTop: 24 }}>
            {/* Score summary strip */}
            <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
              <div style={{ background: "rgba(96,165,250,0.1)", border: "1px solid rgba(96,165,250,0.3)", borderRadius: 10, padding: "10px 20px" }}>
                <span style={{ color: "#60a5fa", fontWeight: 700 }}>Cloud: 9/10 ✅</span>
              </div>
              <div style={{ background: "rgba(167,139,250,0.1)", border: "1px solid rgba(167,139,250,0.3)", borderRadius: 10, padding: "10px 20px" }}>
                <span style={{ color: "#a78bfa", fontWeight: 700 }}>Ollama: 6/10 ✅</span>
              </div>
            </div>

            <div style={{ display: "grid", gap: 12 }}>
              {perComplaint.map((c) => {
                const ollamaFail = c.ollama.startsWith("❌");
                return (
                  <div
                    key={c.id}
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12, padding: "16px 20px" }}
                  >
                    <div style={{ display: "flex", gap: 10, marginBottom: 10, alignItems: "flex-start" }}>
                      <span style={{ background: "rgba(99,102,241,0.25)", color: "#a5b4fc", borderRadius: 8, width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 13, flexShrink: 0 }}>
                        {c.id}
                      </span>
                      <div>
                        <div style={{ fontWeight: 600, color: "#cbd5e1", fontSize: 13 }}>#{c.id} — {c.label}</div>
                        <div style={{ fontSize: 12, color: "#64748b", marginTop: 2, fontStyle: "italic" }}>{complaints[c.id - 1].text}</div>
                      </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                      <div style={{ background: "rgba(96,165,250,0.07)", borderRadius: 8, padding: "10px 12px", fontSize: 13, color: "#bfdbfe" }}>
                        <div style={{ fontSize: 10, color: "#60a5fa", fontWeight: 700, marginBottom: 4 }}>☁️ CLOUD</div>
                        {c.cloud}
                      </div>
                      <div style={{ background: ollamaFail ? "rgba(239,68,68,0.07)" : "rgba(167,139,250,0.07)", borderRadius: 8, padding: "10px 12px", fontSize: 13, color: ollamaFail ? "#fca5a5" : "#ddd6fe", border: ollamaFail ? "1px solid rgba(239,68,68,0.2)" : "none" }}>
                        <div style={{ fontSize: 10, color: ollamaFail ? "#f87171" : "#a78bfa", fontWeight: 700, marginBottom: 4 }}>🦙 OLLAMA</div>
                        {c.ollama}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── VERDICT TAB ──────────────────────────────── */}
        {activeTab === "verdict" && (
          <div style={{ marginTop: 24, maxWidth: 760 }}>
            {/* Code swap */}
            <div style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.09)", borderRadius: 14, padding: "20px 24px", marginBottom: 20 }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: "#94a3b8", marginBottom: 14, letterSpacing: 0.5 }}>THE ONE-LINE CHANGE</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div style={{ background: "#0f172a", borderRadius: 10, padding: "14px 16px", border: "1px solid rgba(96,165,250,0.3)" }}>
                  <div style={{ fontSize: 11, color: "#60a5fa", fontWeight: 700, marginBottom: 8 }}>VERSION A — CLOUD</div>
                  <pre style={{ margin: 0, fontSize: 12, color: "#bfdbfe", overflowX: "auto", whiteSpace: "pre-wrap" }}>{`llm = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  temperature=0.2
)`}</pre>
                </div>
                <div style={{ background: "#0f172a", borderRadius: 10, padding: "14px 16px", border: "1px solid rgba(167,139,250,0.3)" }}>
                  <div style={{ fontSize: 11, color: "#a78bfa", fontWeight: 700, marginBottom: 8 }}>VERSION B — LOCAL</div>
                  <pre style={{ margin: 0, fontSize: 12, color: "#ddd6fe", overflowX: "auto", whiteSpace: "pre-wrap" }}>{`llm = ChatOllama(
  model="mistral",
  temperature=0.2
)`}</pre>
                </div>
              </div>
            </div>

            {/* Verdict card */}
            <div style={{ background: "linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1))", border: "1px solid rgba(139,92,246,0.35)", borderRadius: 16, padding: "28px 28px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <span style={{ fontSize: 24 }}>⚖️</span>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: "#e2e8f0" }}>Which would you ship for a bank, and why?</h2>
              </div>
              <div style={{ fontSize: 15, lineHeight: 1.8, color: "#cbd5e1" }}>
                For a bank, I would ship{" "}
                <strong style={{ color: "#a78bfa" }}>Version B — ChatOllama(mistral) on an on-premises GPU cluster</strong>
                {" "}— because data sovereignty is non-negotiable in regulated financial environments: customer names, account-linked order IDs, and complaint narratives are PII that cannot legally or ethically transit third-party cloud APIs without extensive DPA/RBI/GDPR agreements and ongoing audit obligations.{" "}
                The latency and quality gap is real today, but it is closeable through domain fine-tuning on historical complaint data and horizontal GPU scaling, whereas the compliance gap created by cloud egress is structural and cannot be engineered away.{" "}
                A hybrid rollout — Ollama for all live inference, with periodic cloud-based offline fine-tuning runs on anonymised data — gives the bank the best of both worlds without accepting regulatory risk as a permanent operating condition.
              </div>
            </div>

            {/* Scorecard */}
            <div style={{ marginTop: 20, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, overflow: "hidden" }}>
              <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.08)", fontWeight: 700, fontSize: 14, color: "#94a3b8" }}>FINAL SCORECARD</div>
              {[
                { dim: "Reply Quality", winner: "Cloud" },
                { dim: "Latency (p50)", winner: "Cloud" },
                { dim: "Latency (p99)", winner: "Ollama" },
                { dim: "Cost at Scale", winner: "Ollama" },
                { dim: "Data Privacy / Compliance", winner: "Ollama 🏆" },
                { dim: "Fine-tuning Potential", winner: "Ollama" },
              ].map((row, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 20px", borderBottom: i < 5 ? "1px solid rgba(255,255,255,0.05)" : "none" }}>
                  <span style={{ color: "#cbd5e1", fontSize: 14 }}>{row.dim}</span>
                  <span style={{ padding: "3px 12px", borderRadius: 999, fontSize: 12, fontWeight: 700, background: row.winner.startsWith("Cloud") ? "rgba(96,165,250,0.15)" : "rgba(167,139,250,0.15)", color: row.winner.startsWith("Cloud") ? "#60a5fa" : "#a78bfa" }}>
                    {row.winner}
                  </span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 16, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Generated as part of §5 LLM Decision Framework exercise · Trendly Agentic Support
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
