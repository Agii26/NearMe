import { useState } from "react";
import { IconFlag, IconTrash } from "@tabler/icons-react";
import { flagReview, deleteReview } from "../api/client";
import { useAuthStore } from "../store/authStore";
import StarRating from "./StarRating";

function ReviewItem({ review, onRemoved }) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const currentUsername = useAuthStore((state) => state.user?.username);
  const [flagState, setFlagState] = useState("idle"); // idle | flagging | flagged
  const isOwnReview = currentUsername === review.username;

  async function handleFlag() {
    setFlagState("flagging");
    try {
      await flagReview(review.id, "", accessToken);
      setFlagState("flagged");
    } catch {
      setFlagState("idle");
    }
  }

  async function handleDelete() {
    try {
      await deleteReview(review.id, accessToken);
      onRemoved?.(review.id);
    } catch {
      /* leave the review in place if deletion fails */
    }
  }

  return (
    <div style={{ padding: "12px 0", borderBottom: "1px solid var(--color-border)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <p style={{ fontSize: "13px", fontWeight: 500, color: "var(--color-text-primary)", margin: "0 0 3px" }}>
            {review.username}
          </p>
          <StarRating value={review.rating} showNumber={false} size={13} />
        </div>
        {isOwnReview ? (
          <button
            type="button"
            onClick={handleDelete}
            aria-label="Delete your review"
            style={{ background: "none", border: "none", color: "var(--color-text-secondary)", cursor: "pointer" }}
          >
            <IconTrash size={15} aria-hidden="true" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleFlag}
            disabled={flagState !== "idle"}
            aria-label="Report this review"
            style={{ background: "none", border: "none", color: "var(--color-text-secondary)", cursor: "pointer" }}
          >
            <IconFlag size={15} aria-hidden="true" fill={flagState === "flagged" ? "currentColor" : "none"} />
          </button>
        )}
      </div>
      {review.text && (
        <p style={{ fontSize: "13px", color: "var(--color-text-primary)", margin: "8px 0 0", lineHeight: 1.5 }}>
          {review.text}
        </p>
      )}
    </div>
  );
}

export default function ReviewList({ reviews, onRemoved }) {
  if (reviews.length === 0) {
    return (
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", margin: "12px 0" }}>
        No reviews yet — be the first.
      </p>
    );
  }

  return (
    <div>
      {reviews.map((review) => (
        <ReviewItem key={review.id} review={review} onRemoved={onRemoved} />
      ))}
    </div>
  );
}
