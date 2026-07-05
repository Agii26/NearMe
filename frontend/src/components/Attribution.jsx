/**
 * OpenStreetMap's ODbL license requires attribution wherever their data is
 * displayed — this isn't optional polish. Google's own required attribution
 * renders automatically on the map tiles themselves once a real API key is
 * configured, so it doesn't need a separate credit here.
 */
export default function Attribution() {
  return (
    <p style={{ fontSize: "11px", color: "var(--color-text-secondary)", textAlign: "center", margin: "20px 0 4px" }}>
      Business data &copy;{" "}
      <a
        href="https://www.openstreetmap.org/copyright"
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: "inherit" }}
      >
        OpenStreetMap
      </a>{" "}
      contributors
    </p>
  );
}
