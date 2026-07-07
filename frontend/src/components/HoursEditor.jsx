const DAYS = [
  ["mon", "Monday"], ["tue", "Tuesday"], ["wed", "Wednesday"], ["thu", "Thursday"],
  ["fri", "Friday"], ["sat", "Saturday"], ["sun", "Sunday"],
];

/**
 * Edits the {"mon": [["09:00","18:00"]], ...} hours JSON one day at a time.
 * Deliberately supports a single open/close span per day, not split shifts —
 * covers the large majority of real listings; multi-span editing is a
 * reasonable follow-up if a real business actually needs it.
 */
export default function HoursEditor({ hours, onChange }) {
  const value = hours || {};

  function updateDay(dayKey, field, newValue) {
    const current = value[dayKey]?.[0] || ["09:00", "18:00"];
    const updated = field === "start" ? [newValue, current[1]] : [current[0], newValue];
    onChange({ ...value, [dayKey]: [updated] });
  }

  function toggleClosed(dayKey, isClosed) {
    if (isClosed) {
      onChange({ ...value, [dayKey]: [] });
    } else {
      onChange({ ...value, [dayKey]: [["09:00", "18:00"]] });
    }
  }

  return (
    <div>
      {DAYS.map(([dayKey, label]) => {
        const spans = value[dayKey];
        const isClosed = Array.isArray(spans) && spans.length === 0;
        const [start, end] = spans?.[0] || ["09:00", "18:00"];
        return (
          <div key={dayKey} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
            <span style={{ width: "84px", fontSize: "13px", color: "var(--color-text-primary)" }}>{label}</span>
            <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "12px", color: "var(--color-text-secondary)" }}>
              <input type="checkbox" checked={isClosed} onChange={(e) => toggleClosed(dayKey, e.target.checked)} />
              Closed
            </label>
            {!isClosed && (
              <>
                <input
                  type="time"
                  value={start}
                  onChange={(e) => updateDay(dayKey, "start", e.target.value)}
                  style={{ fontSize: "12px", padding: "4px", borderRadius: "6px", border: "1px solid var(--color-border)" }}
                />
                <span style={{ fontSize: "12px", color: "var(--color-text-secondary)" }}>to</span>
                <input
                  type="time"
                  value={end === "24:00" ? "23:59" : end}
                  onChange={(e) => updateDay(dayKey, "end", e.target.value)}
                  style={{ fontSize: "12px", padding: "4px", borderRadius: "6px", border: "1px solid var(--color-border)" }}
                />
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}
