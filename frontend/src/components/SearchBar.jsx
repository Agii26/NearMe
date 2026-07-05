import { IconSearch, IconCurrentLocation } from "@tabler/icons-react";

export default function SearchBar({ value, onChange, onUseMyLocation, isUsingDeviceLocation }) {
  return (
    <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          gap: "8px",
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "10px",
          padding: "10px 12px",
        }}
      >
        <IconSearch size={18} color="var(--color-text-secondary)" aria-hidden="true" />
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Search for a business or category"
          aria-label="Search for a business or category"
          style={{
            border: "none",
            outline: "none",
            background: "transparent",
            color: "var(--color-text-primary)",
            fontSize: "15px",
            width: "100%",
          }}
        />
      </div>
      <button
        type="button"
        onClick={onUseMyLocation}
        aria-pressed={isUsingDeviceLocation}
        title="Use my location"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: "44px",
          height: "44px",
          minWidth: "44px",
          borderRadius: "10px",
          border: "1px solid var(--color-border)",
          background: isUsingDeviceLocation ? "var(--color-accent)" : "var(--color-surface)",
          cursor: "pointer",
        }}
      >
        <IconCurrentLocation
          size={18}
          color={isUsingDeviceLocation ? "#ffffff" : "var(--color-text-secondary)"}
          aria-hidden="true"
        />
      </button>
    </div>
  );
}
