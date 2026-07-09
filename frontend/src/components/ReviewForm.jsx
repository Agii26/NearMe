import { useState } from "react";
import { createReview } from "../api/client";
import { useAuthStore } from "../store/authStore";
import StarRatingInput from "./StarRatingInput";

export default function ReviewForm({ businessId, onSubmitted }) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const [rating, setRating] = useState(0);
  const [text, setText] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    if (rating === 0) {
      setError("Pick a star rating first.");
      return;
    }
    setStatus("submitting");
    setError(null);
    try {
      const review = await createReview(businessId, { rating, text }, accessToken);
      setStatus("submitted");
      setRating(0);
      setText("");
      onSubmitted?.(review);
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  if (status === "submitted") {
    return (
      <p style={{ fontSize: "13px", color: "var(--color-success)", fontWeight: 500, margin: "12px 0" }}>
        Thanks — your review is live.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ margin: "16px 0" }}>
      <StarRatingInput value={rating} onChange={setRating} />
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Share what stood out (optional)"
        rows={3}
        style={{
          width: "100%",
          marginTop: "10px",
          padding: "10px 12px",
          borderRadius: "10px",
          border: "1px solid var(--color-border)",
          background: "var(--color-surface)",
          color: "var(--color-text-primary)",
          fontSize: "14px",
          fontFamily: "inherit",
          resize: "vertical",
        }}
      />
      {error && <p style={{ color: "var(--color-danger)", fontSize: "12px", margin: "6px 0 0" }}>{error}</p>}
      <button
        type="submit"
        disabled={status === "submitting"}
        style={{
          marginTop: "10px",
          padding: "9px 16px",
          borderRadius: "10px",
          border: "none",
          background: "var(--color-accent)",
          color: "#ffffff",
          fontSize: "13px",
          fontWeight: 500,
          cursor: "pointer",
        }}
      >
        {status === "submitting" ? "Posting…" : "Post review"}
      </button>
    </form>
  );
}
