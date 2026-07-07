import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { IconList, IconMap2, IconUserCircle } from "@tabler/icons-react";
import { getCategories, searchBusinesses } from "../api/client";
import SearchBar from "../components/SearchBar";
import CategoryChips from "../components/CategoryChips";
import BusinessCard from "../components/BusinessCard";
import ThemeToggle from "../components/ThemeToggle";
import ResultsMap from "../components/ResultsMap";
import Attribution from "../components/Attribution";
import { useGeolocation } from "../hooks/useGeolocation";
import { useTheme } from "../context/ThemeContext";
import { useAuthStore } from "../store/authStore";

export default function SearchResultsPage() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const { location, isUsingDeviceLocation, requestDeviceLocation, error: geoError } = useGeolocation();

  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [errorMessage, setErrorMessage] = useState(null);
  const [view, setView] = useState("list"); // list | map

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => {
        /* filter chips just show "All" if categories fail to load */
      });
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timeout);
  }, [query]);

  useEffect(() => {
    setStatus("loading");
    searchBusinesses({
      lat: location.lat,
      lng: location.lng,
      category: selectedCategory,
      q: debouncedQuery || undefined,
    })
      .then((data) => {
        setResults(data.results);
        setStatus("success");
      })
      .catch((err) => {
        setErrorMessage(err.message);
        setStatus("error");
      });
  }, [location, selectedCategory, debouncedQuery]);

  return (
    <div style={{ maxWidth: "480px", margin: "0 auto", padding: "20px 16px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <h1
          style={{
            fontFamily: "var(--font-heading)",
            fontWeight: 600,
            fontSize: "22px",
            color: "var(--color-text-primary)",
            margin: 0,
          }}
        >
          NearMe
        </h1>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button
            type="button"
            onClick={() => setView(view === "list" ? "map" : "list")}
            aria-label={view === "list" ? "Switch to map view" : "Switch to list view"}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "36px",
              height: "36px",
              borderRadius: "50%",
              border: "1px solid var(--color-border)",
              background: "var(--color-surface)",
              cursor: "pointer",
            }}
          >
            {view === "list" ? (
              <IconMap2 size={17} color="var(--color-text-secondary)" aria-hidden="true" />
            ) : (
              <IconList size={17} color="var(--color-text-secondary)" aria-hidden="true" />
            )}
          </button>
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
          <Link
            to={isAuthenticated ? "/dashboard" : "/login"}
            aria-label={isAuthenticated ? "Go to dashboard" : "Log in"}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "36px",
              height: "36px",
              borderRadius: "50%",
              border: "1px solid var(--color-border)",
              background: "var(--color-surface)",
              color: "var(--color-text-secondary)",
            }}
          >
            <IconUserCircle size={18} aria-hidden="true" />
          </Link>
        </div>
      </div>

      <SearchBar
        value={query}
        onChange={setQuery}
        onUseMyLocation={requestDeviceLocation}
        isUsingDeviceLocation={isUsingDeviceLocation}
      />
      {geoError && (
        <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", marginTop: "-6px" }}>{geoError}</p>
      )}

      <CategoryChips categories={categories} selectedSlug={selectedCategory} onSelect={setSelectedCategory} />

      {status === "loading" && (
        <p style={{ color: "var(--color-text-secondary)", fontSize: "14px" }}>Finding businesses nearby…</p>
      )}

      {status === "error" && (
        <p style={{ color: "var(--color-danger)", fontSize: "14px" }}>
          Couldn't load results: {errorMessage}
        </p>
      )}

      {status === "success" && results.length === 0 && (
        <p style={{ color: "var(--color-text-secondary)", fontSize: "14px" }}>
          No businesses found nearby. Try a wider search or a different category.
        </p>
      )}

      {status === "success" && results.length > 0 && view === "list" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
          {results.map((business) => (
            <BusinessCard key={business.id} business={business} />
          ))}
        </div>
      )}

      {status === "success" && results.length > 0 && view === "map" && (
        <ResultsMap results={results} onSelectBusiness={(id) => navigate(`/business/${id}`)} />
      )}

      <Attribution />
    </div>
  );
}
