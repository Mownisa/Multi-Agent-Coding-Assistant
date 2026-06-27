import { ChibiClassifyHead, ChibiCoderHead, ChibiReviewerHead, ChibiResearcherHead, ChibiFinalizeHead, ChibiRetryHead } from "./ChibiDolls.jsx";

const AGENT_META = {
  classify: {
    label: "Classify",
    tagline: "Hmm, let me think~ 🔍",
    color: "#a855f7",
    glow: "rgba(168,85,247,0.5)",
    border: "rgba(168,85,247,0.35)",
    bg: "rgba(168,85,247,0.08)",
    Chibi: ChibiClassifyHead,
  },
  coder: {
    label: "Coder",
    tagline: "I'll write the best code! 💻",
    color: "#60a5fa",
    glow: "rgba(96,165,250,0.5)",
    border: "rgba(96,165,250,0.35)",
    bg: "rgba(96,165,250,0.08)",
    Chibi: ChibiCoderHead,
  },
  reviewer: {
    label: "Reviewer",
    tagline: "Checking carefully... 📋",
    color: "#fb923c",
    glow: "rgba(251,146,60,0.5)",
    border: "rgba(251,146,60,0.35)",
    bg: "rgba(251,146,60,0.08)",
    Chibi: ChibiReviewerHead,
  },
  researcher: {
    label: "Researcher",
    tagline: "Searching the web! 📚",
    color: "#f472b6",
    glow: "rgba(244,114,182,0.5)",
    border: "rgba(244,114,182,0.35)",
    bg: "rgba(244,114,182,0.08)",
    Chibi: ChibiResearcherHead,
  },
  increment_retry: {
    label: "Retry",
    tagline: "Oops, trying again... 😅",
    color: "#9ca3af",
    glow: "rgba(156,163,175,0.4)",
    border: "rgba(156,163,175,0.3)",
    bg: "rgba(156,163,175,0.06)",
    Chibi: ChibiRetryHead,
  },
  finalize: {
    label: "Finalize",
    tagline: "Ta-da! All done! ✨",
    color: "#fbbf24",
    glow: "rgba(251,191,36,0.5)",
    border: "rgba(251,191,36,0.35)",
    bg: "rgba(251,191,36,0.08)",
    Chibi: ChibiFinalizeHead,
  },
};

function StatusBadge({ status }) {
  const map = {
    running: { text: "Running...", bg: "rgba(234,179,8,0.15)", color: "#fde047", border: "rgba(234,179,8,0.4)" },
    done:    { text: "Done ✓",    bg: "rgba(34,197,94,0.15)",  color: "#86efac", border: "rgba(34,197,94,0.4)" },
    failed:  { text: "Failed ✗",  bg: "rgba(239,68,68,0.15)",  color: "#fca5a5", border: "rgba(239,68,68,0.4)" },
  };
  const s = map[status] || map.done;
  return (
    <span style={{
      padding: "3px 10px",
      borderRadius: "999px",
      fontSize: "11px",
      fontWeight: 700,
      background: s.bg,
      color: s.color,
      border: `1px solid ${s.border}`,
      letterSpacing: "0.03em",
    }}>
      {s.text}
    </span>
  );
}

function DecisionPill({ decision }) {
  if (!decision) return null;
  const isPass = decision === "PASS";
  return (
    <span style={{
      padding: "3px 10px",
      borderRadius: "999px",
      fontSize: "11px",
      fontWeight: 800,
      background: isPass ? "rgba(34,197,94,0.15)" : "rgba(239,68,68,0.15)",
      color: isPass ? "#86efac" : "#fca5a5",
      border: `1px solid ${isPass ? "rgba(34,197,94,0.4)" : "rgba(239,68,68,0.4)"}`,
    }}>
      {isPass ? "✓ PASS" : "✗ FAIL"}
    </span>
  );
}

function TypingDots() {
  return (
    <div style={{ display: "flex", gap: 5, alignItems: "center", padding: "8px 4px" }}>
      {[0,1,2].map(i => (
        <div key={i} className="dot-bounce" style={{
          width: 8, height: 8, borderRadius: "50%",
          background: "rgba(255,255,255,0.5)",
          animationDelay: `${i * 0.2}s`,
        }}/>
      ))}
      <span style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginLeft: 4 }}>thinking...</span>
    </div>
  );
}

function extractPreview(node, output) {
  if (!output) return null;
  if (node === "classify" && output.classification) return { label: "Intent detected", content: output.classification };
  if (node === "coder" && output.code) return { label: "Generated code", content: output.code };
  if (node === "reviewer" && output.review_feedback) return { label: "Review feedback", content: output.review_feedback };
  if (node === "researcher" && output.research_notes) return { label: "Research notes", content: output.research_notes };
  return null;
}

export default function StageCard({ node, output, status, index }) {
  const meta = AGENT_META[node] || {
    label: node,
    tagline: "Working...",
    color: "#a855f7",
    glow: "rgba(168,85,247,0.4)",
    border: "rgba(168,85,247,0.3)",
    bg: "rgba(168,85,247,0.07)",
    Chibi: ChibiClassifyHead,
  };
  const { Chibi } = meta;
  const preview = extractPreview(node, output);
  const decision = output?.review_decision;
  const isRunning = status === "running";

  return (
    <div className="card-enter" style={{ display: "flex", gap: 12, marginBottom: 16, position: "relative" }}>
      {/* Connector rail */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 8, width: 20 }}>
        <div className={isRunning ? "rail-pulse" : ""} style={{
          width: 3,
          borderRadius: 999,
          height: "100%",
          minHeight: 60,
          background: meta.color,
          boxShadow: isRunning ? `0 0 8px ${meta.glow}` : "none",
        }}/>
      </div>

      {/* Card */}
      <div style={{
        flex: 1,
        borderRadius: 16,
        border: `1px solid ${meta.border}`,
        background: meta.bg,
        backdropFilter: "blur(12px)",
        overflow: "hidden",
        boxShadow: isRunning ? `0 0 20px ${meta.glow}, 0 4px 24px rgba(0,0,0,0.3)` : "0 4px 24px rgba(0,0,0,0.2)",
        transition: "box-shadow 0.3s ease",
      }}>
        {/* Header */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 16px",
          borderBottom: `1px solid ${meta.border}`,
          background: `${meta.bg}`,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Chibi size={52} bobbing={isRunning} />
            <div>
              <div style={{
                fontFamily: "'Fredoka One', cursive",
                fontSize: 16,
                color: meta.color,
                lineHeight: 1.2,
                textShadow: `0 0 12px ${meta.glow}`,
              }}>
                {meta.label}
              </div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 1 }}>
                {meta.tagline}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <DecisionPill decision={decision} />
            <StatusBadge status={status} />
            <span style={{
              fontFamily: "monospace",
              fontSize: 11,
              color: "rgba(255,255,255,0.25)",
              fontWeight: 700,
            }}>
              #{String(index + 1).padStart(2, "0")}
            </span>
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: "12px 16px" }}>
          {isRunning && !preview && <TypingDots />}

          {preview && (
            <div>
              <div style={{
                fontSize: 10,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                color: meta.color,
                marginBottom: 8,
                opacity: 0.8,
              }}>
                {preview.label}
              </div>
              <pre style={{
                fontSize: 12,
                fontFamily: "monospace",
                color: "rgba(240,230,255,0.9)",
                whiteSpace: "pre-wrap",
                lineHeight: 1.6,
                maxHeight: 240,
                overflowY: "auto",
                margin: 0,
                padding: "10px 12px",
                background: "rgba(0,0,0,0.25)",
                borderRadius: 10,
                border: "1px solid rgba(255,255,255,0.07)",
              }}>
                {preview.content}
              </pre>
            </div>
          )}

          {node === "increment_retry" && (
            <p style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", fontStyle: "italic" }}>
              Oops! Sending back to the Coder agent for another try~ 🔄
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
