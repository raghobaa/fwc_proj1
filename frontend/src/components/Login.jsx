import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Login({ onLogin }) {
  const location = useLocation();
  const navigate = useNavigate();
  const initialEmail = typeof location.state?.email === "string" ? location.state.email : "";
  const [email, setEmail] = useState(initialEmail);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email });
      const token = data.access_token;
      let role = data.role;
      // fallback: decode from JWT payload
      if (!role) {
        try {
          const payload = JSON.parse(atob(token.split(".")[1]));
          role = payload.role;
        } catch (_) {}
      }
      onLogin(token, role);
    } catch (err) {
      console.error(err);
      setError("Could not sign in. Please check your email and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%)",
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
        padding: "1rem",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "rgba(255,255,255,0.95)",
          borderRadius: "20px",
          padding: "2.5rem 2rem",
          boxShadow: "0 25px 60px rgba(0,0,0,0.25)",
          backdropFilter: "blur(10px)",
          position: "relative",
        }}
      >
        {/* Back Button */}
        <button
          type="button"
          onClick={() => navigate("/")}
          style={{
            position: "absolute",
            top: "1.25rem",
            left: "1.25rem",
            background: "none",
            border: "none",
            color: "#6b7280",
            fontSize: "0.85rem",
            fontWeight: "600",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
          onMouseEnter={(e) => (e.target.style.color = "#2563eb")}
          onMouseLeave={(e) => (e.target.style.color = "#6b7280")}
        >
          ← Home
        </button>

        {/* Logo / Brand */}
        <div style={{ textAlign: "center", marginBottom: "2rem", marginTop: "0.5rem" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
              borderRadius: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 1rem",
              boxShadow: "0 8px 20px rgba(37,99,235,0.35)",
            }}
          >
            <span style={{ fontSize: "1.6rem" }}>🤖</span>
          </div>
          <h1
            style={{
              fontSize: "1.6rem",
              fontWeight: "800",
              color: "#111827",
              margin: "0 0 0.25rem",
            }}
          >
            Trendly AI
          </h1>
          <p style={{ color: "#6b7280", fontSize: "0.9rem", margin: 0 }}>
            Sign in with your email to continue
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <label
            htmlFor="email"
            style={{
              display: "block",
              fontSize: "0.85rem",
              fontWeight: "600",
              color: "#374151",
              marginBottom: "0.4rem",
            }}
          >
            Email address
          </label>
          <input
            id="email"
            type="email"
            required
            autoFocus
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: "100%",
              padding: "0.75rem 1rem",
              borderRadius: "12px",
              border: "1.5px solid #e5e7eb",
              fontSize: "1rem",
              outline: "none",
              transition: "border-color 0.2s",
              boxSizing: "border-box",
              marginBottom: "0.75rem",
            }}
            onFocus={(e) => (e.target.style.borderColor = "#2563eb")}
            onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
          />

          {error && (
            <p
              style={{
                color: "#dc2626",
                fontSize: "0.85rem",
                marginBottom: "0.75rem",
                background: "#fef2f2",
                border: "1px solid #fecaca",
                borderRadius: "8px",
                padding: "0.5rem 0.75rem",
              }}
            >
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.8rem",
              borderRadius: "12px",
              border: "none",
              background: loading
                ? "#93c5fd"
                : "linear-gradient(135deg, #2563eb, #1d4ed8)",
              color: "#fff",
              fontSize: "1rem",
              fontWeight: "700",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "opacity 0.2s, transform 0.1s",
              boxShadow: "0 4px 14px rgba(37,99,235,0.35)",
            }}
            onMouseEnter={(e) => {
              if (!loading) e.target.style.opacity = "0.9";
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = "1";
            }}
          >
            {loading ? "Signing in…" : "Continue →"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "1.5rem",
            fontSize: "0.78rem",
            color: "#9ca3af",
          }}
        >
          Use <strong>admin@trendly.com</strong> for admin access
        </p>
      </div>
    </div>
  );
}
