import { IconPhoto } from "@tabler/icons-react";

/**
 * Stand-in for a real business photo. Phase 1 has no media upload yet, so
 * every image slot renders this instead of leaving a broken <img> or an
 * empty box — the warm tint keeps the layout feeling intentional rather
 * than "under construction."
 */
export default function PhotoPlaceholder({ aspectRatio = "1", iconSize = 20, style = {} }) {
  return (
    <div
      style={{
        width: "100%",
        aspectRatio,
        borderRadius: "var(--radius-photo)",
        background: "var(--color-warm-tint)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        ...style,
      }}
    >
      <IconPhoto size={iconSize} color="var(--color-text-primary)" stroke={1.75} aria-hidden="true" />
    </div>
  );
}
