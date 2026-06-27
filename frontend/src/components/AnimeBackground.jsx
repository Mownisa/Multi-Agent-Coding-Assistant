import { useMemo } from "react";

function randomBetween(a, b) {
  return a + Math.random() * (b - a);
}

export default function AnimeBackground() {
  const stars = useMemo(() =>
    Array.from({ length: 80 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: randomBetween(1, 3),
      dur: randomBetween(2, 5),
      delay: randomBetween(0, 4),
    })), []
  );

  const particles = useMemo(() =>
    Array.from({ length: 18 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      size: randomBetween(4, 12),
      dur: randomBetween(8, 18),
      delay: randomBetween(0, 12),
      color: [
        "rgba(168,85,247,0.5)",
        "rgba(255,110,180,0.5)",
        "rgba(255,179,71,0.5)",
        "rgba(126,232,250,0.5)",
        "rgba(165,243,252,0.4)",
      ][i % 5],
    })), []
  );

  return (
    <>
      {/* Stars */}
      <div className="stars-bg">
        {stars.map(s => (
          <div
            key={s.id}
            className="star"
            style={{
              left: `${s.x}%`,
              top: `${s.y}%`,
              width: s.size,
              height: s.size,
              "--dur": `${s.dur}s`,
              "--delay": `${s.delay}s`,
            }}
          />
        ))}
      </div>

      {/* Floating particles */}
      {particles.map(p => (
        <div
          key={p.id}
          className="particle"
          style={{
            left: `${p.x}%`,
            width: p.size,
            height: p.size,
            background: p.color,
            animationDuration: `${p.dur}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </>
  );
}
