import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { IconArrowLeft, IconMapPin, IconPhone } from "@tabler/icons-react";
import { getBusinessDetail } from "../api/client";
import PhotoPlaceholder from "../components/PhotoPlaceholder";
import MapPreview from "../components/MapPreview";
import ThemeToggle from "../components/ThemeToggle";
import { useTheme } from "../context/ThemeContext";

export default function BusinessProfilePage() {
  const { id } = useParams();
  const { theme, toggleTheme } = useTheme();
  const [business, setBusiness] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    setStatus("loading");
    getBusinessDetail(id)
      .then((data) => {
        setBusiness(data);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [id]);

  if (status === "loading") {
    return <p style={{ padding: "20px", color: "var(--color-text-secondary)" }}>Loading…</p>;
  }

  if (status === "error" || !business) {
    return (
      <div style={{ padding: "20px" }}>
        <p style={{ color: "var(--color-danger)" }}>Couldn't find that business.</p>
        <Link to="/" style={{ color: "var(--color-accent)" }}>
          Back to search
        </Link>
      </div>
    );
  }

  const statusColor = business.is_open_now ? "var(--color-success)" : "var(--color-danger)";
  let statusText = "Hours unknown";
  if (business.is_open_now === true) {
    statusText = business.closes_at ? `Open now · closes ${business.closes_at}` : "Open now";
  } else if (business.is_open_now === false) {
    statusText = "Closed now";
  }

  return (
    <div style={{ maxWidth: "480px", margin: "0 auto" }}>
      <div style={{ padding: "16px 16px 0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Link
          to="/"
          aria-label="Back to search results"
          style={{ color: "var(--color-text-primary)", display: "inline-flex" }}
        >
          <IconArrowLeft size={22} aria-hidden="true" />
        </Link>
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </div>

      <div style={{ padding: "12px 16px 24px" }}>
        <div style={{ display: "flex", gap: "6px", marginBottom: "14px" }}>
          <PhotoPlaceholder style={{ width: "31%" }} iconSize={16} />
          <PhotoPlaceholder style={{ width: "31%" }} iconSize={16} />
          <PhotoPlaceholder style={{ width: "31%", opacity: 0.6 }} iconSize={16} />
        </div>

        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontWeight: 600,
            fontSize: "22px",
            color: "var(--color-text-primary)",
            margin: "0 0 8px",
          }}
        >
          {business.name}
        </h1>

        {business.category && (
          <span
            style={{
              display: "inline-block",
              background: "var(--color-accent)",
              color: "#ffffff",
              fontSize: "12px",
              fontWeight: 500,
              padding: "4px 12px",
              borderRadius: "var(--radius-chip)",
              marginBottom: "10px",
            }}
          >
            {business.category.name}
          </span>
        )}

        <p style={{ fontSize: "13px", fontWeight: 500, color: statusColor, margin: "6px 0 18px" }}>
          {statusText}
        </p>

        {business.address && (
          <div style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "12px" }}>
            <IconMapPin size={17} color="var(--color-text-secondary)" style={{ marginTop: "2px", flexShrink: 0 }} aria-hidden="true" />
            <p style={{ fontSize: "14px", color: "var(--color-text-primary)", margin: 0 }}>{business.address}</p>
          </div>
        )}

        {business.contact_phone && (
          <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "16px" }}>
            <IconPhone size={17} color="var(--color-text-secondary)" aria-hidden="true" />
            <a
              href={`tel:${business.contact_phone}`}
              style={{ fontSize: "14px", color: "var(--color-text-primary)", textDecoration: "none" }}
            >
              {business.contact_phone}
            </a>
          </div>
        )}

        <MapPreview latitude={business.latitude} longitude={business.longitude} businessName={business.name} />

        {!business.claimed && (
          <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", marginTop: "16px" }}>
            This listing is sourced from OpenStreetMap and hasn't been claimed by its owner yet.
          </p>
        )}
      </div>
    </div>
  );
}
