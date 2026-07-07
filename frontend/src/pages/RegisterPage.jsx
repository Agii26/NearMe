import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import FormField, { inputStyle } from "../components/FormField";

export default function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("consumer");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register(username, email, password, role);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: "360px", margin: "0 auto", padding: "40px 16px" }}>
      <h1 style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: "22px", color: "var(--color-text-primary)", marginBottom: "20px" }}>
        Create an account
      </h1>
      <form onSubmit={handleSubmit}>
        <FormField label="Username">
          <input style={inputStyle} value={username} onChange={(e) => setUsername(e.target.value)} required />
        </FormField>
        <FormField label="Email">
          <input type="email" style={inputStyle} value={email} onChange={(e) => setEmail(e.target.value)} required />
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
        <FormField label="I am a…">
          <select style={inputStyle} value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="consumer">Consumer, looking for businesses</option>
            <option value="business_owner">Business owner</option>
          </select>
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
          {isSubmitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", marginTop: "16px", textAlign: "center" }}>
        Already have an account? <Link to="/login" style={{ color: "var(--color-accent)" }}>Log in</Link>
      </p>
    </div>
  );
}
