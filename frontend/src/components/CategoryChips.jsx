export default function CategoryChips({ categories, selectedSlug, onSelect }) {
  const options = [{ slug: "all", name: "All" }, ...categories];

  return (
    <div
      role="tablist"
      aria-label="Filter by category"
      style={{
        display: "flex",
        gap: "8px",
        overflowX: "auto",
        marginBottom: "16px",
        paddingBottom: "2px",
      }}
    >
      {options.map((option) => {
        const isSelected = option.slug === selectedSlug;
        return (
          <button
            key={option.slug}
            type="button"
            role="tab"
            aria-selected={isSelected}
            onClick={() => onSelect(option.slug)}
            style={{
              flexShrink: 0,
              padding: "8px 16px",
              borderRadius: "var(--radius-chip)",
              border: isSelected ? "none" : "1px solid var(--color-border)",
              background: isSelected ? "var(--color-accent)" : "var(--color-surface)",
              color: isSelected ? "#ffffff" : "var(--color-text-secondary)",
              fontSize: "13px",
              fontWeight: 500,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {option.name}
          </button>
        );
      })}
    </div>
  );
}
