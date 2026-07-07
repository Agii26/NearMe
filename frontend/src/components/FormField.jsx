export default function FormField({ label, error, children }) {
  return (
    <div style={{ marginBottom: "14px" }}>
      <label style={{ display: "block", fontSize: "13px", fontWeight: 500, color: "var(--color-text-primary)" }}>
        <span style={{ display: "block", marginBottom: "6px" }}>{label}</span>
        {children}
      </label>
      {error && <p style={{ fontSize: "12px", color: "var(--color-danger)", margin: "4px 0 0" }}>{error}</p>}
    </div>
  );
}

export const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: "10px",
  border: "1px solid var(--color-border)",
  background: "var(--color-surface)",
  color: "var(--color-text-primary)",
  fontSize: "14px",
  outline: "none",
};
