import { Link } from "react-router-dom";
import PhotoPlaceholder from "./PhotoPlaceholder";

export default function BusinessCard({ business }) {
  const statusColor = business.is_open_now ? "var(--color-success)" : "var(--color-danger)";
  const statusLabel = business.is_open_now === null ? null : business.is_open_now ? "open" : "closed";

  return (
    <Link
      to={`/business/${business.id}`}
      style={{ textDecoration: "none", color: "inherit", display: "block" }}
    >
      <PhotoPlaceholder style={{ marginBottom: "6px" }} />
      <p
        style={{
          fontFamily: "var(--font-heading)",
          fontWeight: 600,
          fontSize: "13px",
          color: "var(--color-text-primary)",
          margin: "0 0 2px",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {business.name}
      </p>
      <p style={{ fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-secondary)", margin: 0 }}>
        {business.category?.name}
        {business.distance_km != null && ` · ${business.distance_km}km`}
        {statusLabel && (
          <>
            {" · "}
            <span style={{ color: statusColor, fontWeight: 500 }}>{statusLabel}</span>
          </>
        )}
      </p>
    </Link>
  );
}
