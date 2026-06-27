import { useState } from "react";
import { usePipelineStream } from "./usePipelineStream.js";
import StageCard from "./components/StageCard.jsx";
import FinalCard from "./components/FinalCard.jsx";
import MessageInput from "./components/MessageInput.jsx";
import AnimeBackground from "./components/AnimeBackground.jsx";
import { ChibiClassify, ChibiCoder, ChibiReviewer, ChibiResearcher } from "./components/ChibiDolls.jsx";

function newThreadId() {
  return `thread_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function WelcomeScreen() {
  return (
    <div style={{
      textAlign: "center",
      paddingTop: 40,
      paddingBottom: 40,
    }}>
      {/* Chibi team display */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        gap: 8,
        marginBottom: 24,
        flexWrap: "wrap",
      }}>
        <div className="chibi-doll" style={{ animationDelay: "0s" }}>
          <ChibiClassify size={110} />
        </div>
        <div className="chibi-doll" style={{ animationDelay: "0.5s" }}>
          <ChibiCoder size={110} />
        </div>
        <div className="chibi-doll" style={{ animationDelay: "1s" }}>
          <ChibiReviewer size={110} />
        </div>
        <div className="chibi-doll" style={{ animationDelay: "1.5s" }}>
          <ChibiResearcher size={110} />
        </div>
      </div>

      <h2 style={{
        fontFamily: "'Fredoka One', cursive",
        fontSize: 22,
        color: "rgba(240,230,255,0.8)",
        marginBottom: 10,
        letterSpacing: "0.02em",
      }}>
        Your AI coding team is ready! 🌟
      </h2>
      <p style={{
        fontSize: 14,
        color: "rgba(255,255,255,0.4)",
        maxWidth: 420,
        margin: "0 auto",
        lineHeight: 1.7,
      }}>
        Describe your coding task below and watch the chibi agents work together —
        classifying, coding, reviewing, and researching in real-time!
      </p>

      {/* Pipeline steps */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: 6,
        marginTop: 24,
        flexWrap: "wrap",
      }}>
        {["🔍 Classify", "→", "💻 Code", "→", "📋 Review", "→", "📚 Research", "→", "✨ Done"].map((step, i) => (
          <span key={i} style={{
            fontSize: 12,
            color: step === "→" ? "rgba(255,255,255,0.25)" : "rgba(168,85,247,0.9)",
            fontWeight: step === "→" ? 400 : 700,
            padding: step === "→" ? 0 : "2px 10px",
            background: step === "→" ? "transparent" : "rgba(168,85,247,0.12)",
            borderRadius: 999,
            border: step === "→" ? "none" : "1px solid rgba(168,85,247,0.25)",
          }}>
            {step}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const { stages, finalOutput, isStreaming, error, run } = usePipelineStream();
  const [threadId] = useState(newThreadId);
  const [hasRunOnce, setHasRunOnce] = useState(false);

  const handleSubmit = (message) => {
    setHasRunOnce(true);
    run(message, threadId);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", position: "relative" }}>
      {/* Animated background */}
      <AnimeBackground />

      {/* Header */}
      <header style={{
        position: "relative",
        zIndex: 10,
        borderBottom: "1px solid rgba(168,85,247,0.2)",
        padding: "14px 24px",
        background: "rgba(0,0,0,0.3)",
        backdropFilter: "blur(20px)",
      }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", alignItems: "center", gap: 12 }}>
          {/* Logo sparkle */}
          <div style={{ fontSize: 28 }}>🌸</div>
          <div>
            <h1 className="rainbow-text" style={{
              fontFamily: "'Fredoka One', cursive",
              fontSize: 22,
              margin: 0,
              letterSpacing: "0.04em",
            }}>
              Multi-Agent Coding Assistant
            </h1>
            <p style={{
              fontSize: 11,
              color: "rgba(255,255,255,0.4)",
              margin: "2px 0 0 0",
              letterSpacing: "0.05em",
            }}>
              Powered by Gemini Flash • Chibi Squad ✨
            </p>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
            {isStreaming && (
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "4px 12px",
                borderRadius: 999,
                background: "rgba(168,85,247,0.15)",
                border: "1px solid rgba(168,85,247,0.4)",
                fontSize: 12,
                color: "#c084fc",
                fontWeight: 700,
              }}>
                <div className="dot-bounce" style={{ width: 6, height: 6, borderRadius: "50%", background: "#c084fc" }}/>
                Live
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main style={{
        flex: 1,
        position: "relative",
        zIndex: 10,
        maxWidth: 800,
        width: "100%",
        margin: "0 auto",
        padding: "24px 20px",
      }}>
        {!hasRunOnce && <WelcomeScreen />}

        {/* Stage cards */}
        <div>
          {stages.map((stage, index) => (
            <StageCard
              key={`${stage.node}-${index}`}
              node={stage.node}
              output={stage.output}
              status={stage.status}
              index={index}
            />
          ))}
        </div>

        <FinalCard finalOutput={finalOutput} />

        {error && (
          <div className="card-enter" style={{
            marginTop: 12,
            borderRadius: 14,
            border: "1px solid rgba(239,68,68,0.4)",
            background: "rgba(239,68,68,0.08)",
            padding: "12px 16px",
          }}>
            <p style={{ fontFamily: "monospace", fontSize: 13, color: "#fca5a5", margin: 0 }}>
              ⚠️ Pipeline error: {error}
            </p>
          </div>
        )}
      </main>

      {/* Footer input */}
      <footer style={{
        position: "sticky",
        bottom: 0,
        zIndex: 20,
        borderTop: "1px solid rgba(168,85,247,0.2)",
        background: "rgba(0,0,0,0.4)",
        backdropFilter: "blur(24px)",
        padding: "16px 20px",
      }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <MessageInput onSubmit={handleSubmit} disabled={isStreaming} />
        </div>
      </footer>
    </div>
  );
}
