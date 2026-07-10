import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { IconArrowLeft, IconMapPin, IconPhone } from "@tabler/icons-react";
import { getBusinessDetail, getReviews } from "../api/client";
import PhotoPlaceholder from "../components/PhotoPlaceholder";
import MapPreview from "../components/MapPreview";
import Attribution from "../components/Attribution";
import ThemeToggle from "../components/ThemeToggle";
import ClaimButton from "../components/ClaimButton";
import StarRating from "../components/StarRating";
import ReviewForm from "../components/ReviewForm";
import ReviewList from "../components/ReviewList";
import { useTheme } from "../context/ThemeContext";
import { useAuthStore } from "../store/authStore";

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").replace(/\/api\/?$/, "");

export default function BusinessProfilePage() {
  const { id } = useParams();
  const { theme, toggleTheme } = useTheme();
  const accessToken = useAuthStore((state) => state.accessToken);
  const currentUsername = useAuthStore((state) => state.user?.username);

  const [business, setBusiness] = useState(null);
  const [status, setStatus] = useState("loading");
  const [reviews, setReviews] = useState([]);
  const [reviewNotice, setReviewNotice] = useState(null);

  const loadBusiness = useCallback(() => {
    setStatus("loading");
    getBusinessDetail(id, accessToken)
      .then((data) => {
        setBusiness(data);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [id, accessToken]);

  useEffect(() => {
    loadBusiness();
  }, [loadBusiness]);

  useEffect(() => {
    getReviews(id)
      .then((data) => setReviews(data.results || data))
      .catch(() => {
        /* reviews section just shows empty if this fails — not fatal to the page */
      });
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

  const photoSlots = [0, 1, 2];
  const hasAlreadyReviewed = reviews.some((review) => review.username === currentUsername);
  const canReview = accessToken && !business.is_owner && !hasAlreadyReviewed;

  // Derived from the live reviews list rather than the business snapshot's
  // average_rating/review_count — those only reflect what was true at the
  // moment the page first loaded, so they'd otherwise go stale the instant
  // a review is added or removed in this same session.
  const liveReviewCount = reviews.length;
  const liveAverageRating =
    liveReviewCount > 0
      ? reviews.reduce((sum, review) => sum + review.rating, 0) / liveReviewCount
      : null;

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
          {photoSlots.map((index) => {
            const photo = business.photos?.[index];
            if (photo) {
              return (
                <img
                  key={photo.id}
                  src={`${API_ORIGIN}${photo.image}`}
                  alt={`${business.name} photo ${index + 1}`}
                  style={{ width: "31%", aspectRatio: "1", objectFit: "cover", borderRadius: "8px" }}
                />
              );
            }
            return <PhotoPlaceholder key={index} style={{ width: "31%" }} iconSize={16} />;
          })}
        </div>

        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontWeight: 600,
            fontSize: "22px",
            color: "var(--color-text-primary)",
            margin: "0 0 6px",
          }}
        >
          {business.name}
        </h1>

        {liveReviewCount > 0 && (
          <div style={{ marginBottom: "10px" }}>
            <StarRating value={liveAverageRating} count={liveReviewCount} size={15} />
          </div>
        )}

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

        <p style={{ fontSize: "13px", fontWeight: 500, color: statusColor, margin: "6px 0 18px" }}>{statusText}</p>

        {business.address && (
          <div style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "12px" }}>
            <IconMapPin
              size={17}
              color="var(--color-text-secondary)"
              style={{ marginTop: "2px", flexShrink: 0 }}
              aria-hidden="true"
            />
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
          <>
            <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", marginTop: "16px" }}>
              This listing is sourced from OpenStreetMap and hasn't been claimed by its owner yet.
            </p>
            <ClaimButton businessId={business.id} />
          </>
        )}

        <h2
          style={{
            fontFamily: "var(--font-heading)",
            fontWeight: 600,
            fontSize: "16px",
            color: "var(--color-text-primary)",
            margin: "24px 0 0",
          }}
        >
          Reviews
        </h2>

        {canReview && (
          <ReviewForm businessId={business.id} onSubmitted={(review) => setReviews([review, ...reviews])} />
        )}

        {reviewNotice && (
          <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", margin: "10px 0 0" }}>
            {reviewNotice}
          </p>
        )}

        <ReviewList
          reviews={reviews}
          onRemoved={(reviewId, meta) => {
            setReviews(reviews.filter((r) => r.id !== reviewId));
            setReviewNotice(
              meta?.reason === "flagged" ? "Review reported — now hidden pending moderation." : null
            );
          }}
        />

        <Attribution />
      </div>
    </div>
  );
}
