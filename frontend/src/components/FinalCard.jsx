import { ChibiFinalize } from "./ChibiDolls.jsx";

function Sparkle({ style }) {
  return (
    <div className="sparkle" style={{
      position: "absolute",
      fontSize: 16,
      ...style,
    }}>✨</div>
  );
}

export default function FinalCard({ finalOutput }) {
  if (!finalOutput) return null;

  return (
    <div className="card-enter" style={{ position: "relative", marginTop: 8 }}>
      {/* Sparkles */}
      <Sparkle style={{ top: -10, left: 20 }} />
      <Sparkle style={{ top: -8, right: 40, animationDelay: "0.5s" }} />
      <Sparkle style={{ top: 10, right: 10, animationDelay: "1s" }} />

      <div style={{
        borderRadius: 20,
        border: "1px solid rgba(251,191,36,0.5)",
        background: "rgba(251,191,36,0.06)",
        backdropFilter: "blur(16px)",
        overflow: "hidden",
        boxShadow: "0 0 30px rgba(251,191,36,0.25), 0 8px 32px rgba(0,0,0,0.3)",
      }}>
        {/* Header */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "12px 20px",
          borderBottom: "1px solid rgba(251,191,36,0.3)",
          background: "rgba(251,191,36,0.08)",
        }}>
          <div className="chibi-spin">
            <ChibiFinalize size={84} />
          </div>
          <div>
            <div style={{
              fontFamily: "'Fredoka One', cursive",
              fontSize: 22,
              background: "linear-gradient(135deg, #fbbf24, #f97316, #fbbf24)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              textShadow: "none",
              letterSpacing: "0.02em",
            }}>
              Pipeline Complete!
            </div>
            <div style={{ fontSize: 12, color: "rgba(251,191,36,0.7)", marginTop: 2 }}>
              Your magical code is ready~ ⭐
            </div>
          </div>
        </div>

        {/* Output */}
        <div style={{ padding: "16px 20px" }}>
          <pre style={{
            fontSize: 13,
            fontFamily: "monospace",
            color: "rgba(240,230,255,0.92)",
            whiteSpace: "pre-wrap",
            lineHeight: 1.7,
            margin: 0,
            padding: "14px 16px",
            background: "rgba(0,0,0,0.3)",
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.07)",
          }}>
            {finalOutput}
          </pre>
        </div>
      </div>
    </div>
  );
}
