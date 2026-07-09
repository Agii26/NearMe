import { useState } from "react";
import { IconStar, IconStarFilled } from "@tabler/icons-react";

export default function StarRatingInput({ value, onChange }) {
  const [hoverValue, setHoverValue] = useState(null);
  const displayValue = hoverValue ?? value;

  return (
    <div role="radiogroup" aria-label="Rating" style={{ display: "inline-flex", gap: "4px" }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          role="radio"
          aria-checked={value === star}
          aria-label={`${star} star${star > 1 ? "s" : ""}`}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHoverValue(star)}
          onMouseLeave={() => setHoverValue(null)}
          style={{ background: "none", border: "none", padding: "2px", cursor: "pointer" }}
        >
          {star <= displayValue ? (
            <IconStarFilled size={24} color="var(--color-accent)" aria-hidden="true" />
          ) : (
            <IconStar size={24} color="var(--color-border)" aria-hidden="true" />
          )}
        </button>
      ))}
    </div>
  );
}
