import { useEffect, useRef, useState } from "react";
import { IconMapPin } from "@tabler/icons-react";
import PhotoPlaceholder from "./PhotoPlaceholder";

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

function loadGoogleMapsScript() {
  if (window.google?.maps) return Promise.resolve();
  if (window.__googleMapsLoadingPromise) return window.__googleMapsLoadingPromise;

  window.__googleMapsLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}`;
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
  return window.__googleMapsLoadingPromise;
}

/**
 * Renders one pin per search result on a shared map, fitted to bounds.
 * See MapPreview.jsx for the same fallback rationale — Google Maps is
 * rendering/autocomplete only, per the Foundation doc's data policy, and
 * this never persists anything Google-sourced back to our database.
 */
export default function ResultsMap({ results, onSelectBusiness }) {
  const mapContainerRef = useRef(null);
  const [failedToLoad, setFailedToLoad] = useState(false);

  useEffect(() => {
    if (!GOOGLE_MAPS_API_KEY || !mapContainerRef.current || results.length === 0) return;

    let cancelled = false;
    loadGoogleMapsScript()
      .then(() => {
        if (cancelled || !mapContainerRef.current) return;
        const bounds = new window.google.maps.LatLngBounds();
        const map = new window.google.maps.Map(mapContainerRef.current, {
          disableDefaultUI: true,
          zoomControl: true,
        });
        results.forEach((business) => {
          const position = { lat: business.latitude, lng: business.longitude };
          const marker = new window.google.maps.Marker({ position, map, title: business.name });
          marker.addListener("click", () => onSelectBusiness?.(business.id));
          bounds.extend(position);
        });
        map.fitBounds(bounds);
      })
      .catch(() => {
        if (!cancelled) setFailedToLoad(true);
      });

    return () => {
      cancelled = true;
    };
  }, [results, onSelectBusiness]);

  const showPlaceholder = !GOOGLE_MAPS_API_KEY || failedToLoad;

  if (showPlaceholder) {
    return (
      <div>
        <div
          style={{
            width: "100%",
            height: "180px",
            borderRadius: "10px",
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
            marginBottom: "16px",
          }}
          role="img"
          aria-label="Map view unavailable — showing the list instead"
        >
          <IconMapPin size={26} color="var(--color-accent)" aria-hidden="true" />
          <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", margin: 0, textAlign: "center", padding: "0 20px" }}>
            Map view needs a Google Maps API key — showing the list below instead.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
          {results.map((business) => (
            <div key={business.id} style={{ opacity: 0.5 }}>
              <PhotoPlaceholder />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={mapContainerRef}
      style={{ width: "100%", height: "70vh", borderRadius: "10px", overflow: "hidden" }}
    />
  );
}
