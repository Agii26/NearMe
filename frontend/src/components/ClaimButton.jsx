import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { claimBusiness } from "../api/client";
import { useAuthStore } from "../store/authStore";

export default function ClaimButton({ businessId }) {
  const navigate = useNavigate();
  const accessToken = useAuthStore((state) => state.accessToken);
  const user = useAuthStore((state) => state.user);
  const [status, setStatus] = useState("idle"); // idle | submitting | submitted | error
  const [error, setError] = useState(null);

  async function handleClaim() {
    if (!accessToken) {
      navigate("/login", { state: { from: `/business/${businessId}` } });
      return;
    }
    setStatus("submitting");
    setError(null);
    try {
      await claimBusiness(businessId, accessToken);
      setStatus("submitted");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  if (status === "submitted") {
    return (
      <p style={{ fontSize: "13px", color: "var(--color-success)", fontWeight: 500, margin: "12px 0" }}>
        Claim submitted — pending review.
      </p>
    );
  }

  if (user && user.profile?.role !== "business_owner") {
    return null; // consumers aren't offered a claim button at all
  }

  return (
    <div style={{ margin: "16px 0" }}>
      <button
        type="button"
        onClick={handleClaim}
        disabled={status === "submitting"}
        style={{
          padding: "10px 18px",
          borderRadius: "10px",
          border: "1px solid var(--color-accent)",
          background: "transparent",
          color: "var(--color-accent)",
          fontSize: "13px",
          fontWeight: 500,
          cursor: status === "submitting" ? "default" : "pointer",
        }}
      >
        {status === "submitting" ? "Submitting…" : "Claim this business"}
      </button>
      {error && <p style={{ fontSize: "12px", color: "var(--color-danger)", marginTop: "6px" }}>{error}</p>}
    </div>
  );
}
