import { IconStar, IconStarFilled } from "@tabler/icons-react";

/**
 * Read-only star display for an existing rating (search cards, review list,
 * profile summary). For picking a rating, see StarRatingInput.
 */
export default function StarRating({ value, size = 14, showNumber = true, count }) {
  if (value == null) {
    return <span style={{ fontSize: "12px", color: "var(--color-text-secondary)" }}>No reviews yet</span>;
  }

  const rounded = Math.round(value);
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "3px" }}>
      <span style={{ display: "inline-flex", gap: "1px" }}>
        {[1, 2, 3, 4, 5].map((star) =>
          star <= rounded ? (
            <IconStarFilled key={star} size={size} color="var(--color-accent)" aria-hidden="true" />
          ) : (
            <IconStar key={star} size={size} color="var(--color-border)" aria-hidden="true" />
          )
        )}
      </span>
      {showNumber && (
        <span style={{ fontSize: "12px", color: "var(--color-text-secondary)" }}>
          {value.toFixed(1)}
          {count != null && ` (${count})`}
        </span>
      )}
    </span>
  );
}
