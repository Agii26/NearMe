import { IconSun, IconMoon } from "@tabler/icons-react";

export default function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === "dark";
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
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
      {isDark ? (
        <IconSun size={17} color="var(--color-text-secondary)" aria-hidden="true" />
      ) : (
        <IconMoon size={17} color="var(--color-text-secondary)" aria-hidden="true" />
      )}
    </button>
  );
}
