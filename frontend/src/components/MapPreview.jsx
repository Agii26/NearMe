import { useEffect, useRef, useState } from "react";
import { IconMapPin } from "@tabler/icons-react";

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
 * Renders a single-pin Google Map for a business's location. Google Maps
 * is used for rendering only — see the Foundation doc's note that
 * Google Places API's terms don't allow caching Google-sourced content,
 * so nothing from this map is ever written back to our database.
 *
 * Falls back to a static placeholder when no API key is configured
 * (e.g. local development without a key set in .env), rather than
 * throwing or rendering a broken map.
 */
export default function MapPreview({ latitude, longitude, businessName }) {
  const mapContainerRef = useRef(null);
  const [failedToLoad, setFailedToLoad] = useState(false);

  useEffect(() => {
    if (!GOOGLE_MAPS_API_KEY || !mapContainerRef.current) return;

    let cancelled = false;
    loadGoogleMapsScript()
      .then(() => {
        if (cancelled || !mapContainerRef.current) return;
        const map = new window.google.maps.Map(mapContainerRef.current, {
          center: { lat: latitude, lng: longitude },
          zoom: 16,
          disableDefaultUI: true,
        });
        new window.google.maps.Marker({
          position: { lat: latitude, lng: longitude },
          map,
          title: businessName,
        });
      })
      .catch(() => {
        if (!cancelled) setFailedToLoad(true);
      });

    return () => {
      cancelled = true;
    };
  }, [latitude, longitude, businessName]);

  const showPlaceholder = !GOOGLE_MAPS_API_KEY || failedToLoad;

  if (showPlaceholder) {
    return (
      <div
        style={{
          width: "100%",
          height: "90px",
          borderRadius: "10px",
          background: "var(--color-bg)",
          border: "1px solid var(--color-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        role="img"
        aria-label={`Map preview unavailable for ${businessName}`}
      >
        <IconMapPin size={24} color="var(--color-accent)" aria-hidden="true" />
      </div>
    );
  }

  return (
    <div
      ref={mapContainerRef}
      style={{ width: "100%", height: "90px", borderRadius: "10px", overflow: "hidden" }}
    />
  );
}
