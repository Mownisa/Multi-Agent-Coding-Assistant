import { useState } from "react";

const PLACEHOLDERS = [
  "Write a binary search function in Python~ 💫",
  "Review this React component for bugs... 🔍",
  "Research the best way to handle JWT auth 📚",
  "Create a REST API with FastAPI 🚀",
  "Help me fix this TypeScript error! 😅",
];

export default function MessageInput({ onSubmit, disabled }) {
  const [value, setValue] = useState("");
  const [placeholder] = useState(() =>
    PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]
  );

  const handleSubmit = (e) => {
    e?.preventDefault?.();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  };

  return (
    <div style={{
      background: "rgba(255,255,255,0.05)",
      backdropFilter: "blur(20px)",
      border: "1px solid rgba(168,85,247,0.3)",
      borderRadius: 20,
      padding: 16,
      boxShadow: "0 0 24px rgba(168,85,247,0.15), 0 8px 32px rgba(0,0,0,0.3)",
    }}>
      <div style={{ display: "flex", gap: 12, alignItems: "flex-end" }}>
        <div style={{ flex: 1, position: "relative" }}>
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder={placeholder}
            rows={3}
            disabled={disabled}
            style={{
              width: "100%",
              resize: "none",
              borderRadius: 14,
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(0,0,0,0.25)",
              padding: "12px 16px",
              fontSize: 14,
              fontFamily: "'Nunito', system-ui, sans-serif",
              color: "rgba(240,230,255,0.95)",
              outline: "none",
              boxSizing: "border-box",
              lineHeight: 1.6,
              transition: "border-color 0.2s",
              opacity: disabled ? 0.5 : 1,
            }}
            onFocus={(e) => e.target.style.borderColor = "rgba(168,85,247,0.6)"}
            onBlur={(e) => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
          />
          <div style={{
            position: "absolute",
            bottom: 8,
            right: 10,
            fontSize: 11,
            color: "rgba(255,255,255,0.25)",
          }}>
            Enter to send · Shift+Enter for newline
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          style={{
            padding: "14px 24px",
            borderRadius: 14,
            border: "none",
            background: disabled
              ? "rgba(168,85,247,0.3)"
              : "linear-gradient(135deg, #a855f7, #ec4899)",
            color: "white",
            fontFamily: "'Fredoka One', cursive",
            fontSize: 16,
            cursor: disabled || !value.trim() ? "not-allowed" : "pointer",
            opacity: !value.trim() ? 0.5 : 1,
            transition: "all 0.2s",
            boxShadow: disabled ? "none" : "0 4px 20px rgba(168,85,247,0.4)",
            whiteSpace: "nowrap",
            letterSpacing: "0.03em",
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            if (!disabled && value.trim()) {
              e.target.style.transform = "scale(1.05)";
              e.target.style.boxShadow = "0 6px 28px rgba(168,85,247,0.6)";
            }
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "scale(1)";
            e.target.style.boxShadow = disabled ? "none" : "0 4px 20px rgba(168,85,247,0.4)";
          }}
        >
          {disabled ? "✨ Running..." : "✨ Run!"}
        </button>
      </div>
    </div>
  );
}
