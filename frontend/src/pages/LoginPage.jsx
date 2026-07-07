import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import FormField, { inputStyle } from "../components/FormField";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((state) => state.login);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const redirectTo = location.state?.from || "/";

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(username, password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: "360px", margin: "0 auto", padding: "40px 16px" }}>
      <h1 style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: "22px", color: "var(--color-text-primary)", marginBottom: "20px" }}>
        Log in
      </h1>
      <form onSubmit={handleSubmit}>
        <FormField label="Username">
          <input style={inputStyle} value={username} onChange={(e) => setUsername(e.target.value)} required />
        </FormField>
        <FormField label="Password">
          <input
            type="password"
            style={inputStyle}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormField>
        {error && <p style={{ color: "var(--color-danger)", fontSize: "13px", marginBottom: "12px" }}>{error}</p>}
        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "10px",
            border: "none",
            background: "var(--color-accent)",
            color: "#ffffff",
            fontSize: "14px",
            fontWeight: 500,
            cursor: isSubmitting ? "default" : "pointer",
            opacity: isSubmitting ? 0.7 : 1,
          }}
        >
          {isSubmitting ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", marginTop: "16px", textAlign: "center" }}>
        No account? <Link to="/register" style={{ color: "var(--color-accent)" }}>Sign up</Link>
      </p>
    </div>
  );
}
