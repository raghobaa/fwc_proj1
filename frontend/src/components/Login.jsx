import { useState } from "react";
import api from "../services/api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post("/auth/login", {
        username: email,
        password,
      });
      const token = data.access_token;
      // Decode token payload to extract role (simple base64 decode, no verification needed client‑side)
      let role = null;
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        role = payload.role;
      } catch (_) {}
      onLogin(token, role);
    } catch (err) {
      console.error(err);
      setError("Invalid credentials");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F7F7F8]">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-xl bg-white p-6 shadow-sm"
      >
        <h2 className="mb-4 text-xl font-bold text-gray-800">
          Sign in to Trendly
        </h2>
        {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-xl border border-[#E5E7EB] bg-white px-4 py-2 focus:border-[#2563EB] focus:outline-none"
          />
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-xl border border-[#E5E7EB] bg-white px-4 py-2 focus:border-[#2563EB] focus:outline-none"
          />
        </div>
        <button
          type="submit"
          className="w-full rounded-xl bg-[#2563EB] py-2 font-semibold text-white hover:bg-blue-700"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
