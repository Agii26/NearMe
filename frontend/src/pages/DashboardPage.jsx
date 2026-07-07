import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IconArrowLeft } from "@tabler/icons-react";
import { getMyBusinesses, getMyClaims, getCategories } from "../api/client";
import { useAuthStore } from "../store/authStore";
import BusinessEditCard from "../components/BusinessEditCard";

const CLAIM_STATUS_COLOR = {
  pending: "var(--color-text-secondary)",
  approved: "var(--color-success)",
  rejected: "var(--color-danger)",
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const accessToken = useAuthStore((state) => state.accessToken);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [businesses, setBusinesses] = useState([]);
  const [claims, setClaims] = useState([]);
  const [categories, setCategories] = useState([]);
  const [status, setStatus] = useState("loading"); // only gates the very first load
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false);

  const loadData = useCallback(() => {
    Promise.all([getMyBusinesses(accessToken), getMyClaims(accessToken), getCategories()])
      .then(([businessesData, claimsData, categoriesData]) => {
        setBusinesses(businessesData.results || businessesData);
        setClaims(claimsData.results || claimsData);
        setCategories(categoriesData);
        setStatus("success");
        setHasLoadedOnce(true);
      })
      .catch(() => setStatus("error"));
  }, [accessToken]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <div style={{ maxWidth: "480px", margin: "0 auto", padding: "20px 16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <Link to="/" aria-label="Back to search" style={{ color: "var(--color-text-primary)", display: "inline-flex" }}>
          <IconArrowLeft size={22} aria-hidden="true" />
        </Link>
        <button
          type="button"
          onClick={handleLogout}
          style={{ background: "none", border: "none", color: "var(--color-text-secondary)", fontSize: "13px", cursor: "pointer" }}
        >
          Log out
        </button>
      </div>

      <h1 style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: "20px", color: "var(--color-text-primary)", marginBottom: "4px" }}>
        Dashboard
      </h1>
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", marginBottom: "24px" }}>
        Signed in as {user?.username}
      </p>

      {status === "loading" && !hasLoadedOnce && (
        <p style={{ color: "var(--color-text-secondary)", fontSize: "14px" }}>Loading…</p>
      )}
      {status === "error" && !hasLoadedOnce && (
        <p style={{ color: "var(--color-danger)", fontSize: "14px" }}>Couldn't load your dashboard.</p>
      )}

      {hasLoadedOnce && (
        <>
          <section style={{ marginBottom: "28px" }}>
            <h2 style={{ fontSize: "14px", fontWeight: 500, color: "var(--color-text-primary)", marginBottom: "10px" }}>
              Your businesses
            </h2>
            {businesses.length === 0 && (
              <p style={{ fontSize: "13px", color: "var(--color-text-secondary)" }}>
                No claimed businesses yet — find one on the map and claim it.
              </p>
            )}
            {businesses.map((business) => (
              <BusinessEditCard key={business.id} business={business} categories={categories} onSaved={loadData} />
            ))}
          </section>

          <section>
            <h2 style={{ fontSize: "14px", fontWeight: 500, color: "var(--color-text-primary)", marginBottom: "10px" }}>
              Claim requests
            </h2>
            {claims.length === 0 && (
              <p style={{ fontSize: "13px", color: "var(--color-text-secondary)" }}>No claim requests submitted yet.</p>
            )}
            {claims.map((claim) => (
              <div
                key={claim.id}
                style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid var(--color-border)" }}
              >
                <span style={{ fontSize: "13px", color: "var(--color-text-primary)" }}>{claim.business_name}</span>
                <span style={{ fontSize: "12px", fontWeight: 500, color: CLAIM_STATUS_COLOR[claim.status] }}>
                  {claim.status}
                </span>
              </div>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
