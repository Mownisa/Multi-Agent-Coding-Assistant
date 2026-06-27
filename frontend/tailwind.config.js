/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Fredoka One'", "cursive"],
        body: ["'Nunito'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        purple: {
          anime: "#a855f7",
          dark: "#6d28d9",
          glow: "#c084fc",
        },
        pink: {
          anime: "#ec4899",
          light: "#f9a8d4",
        },
      },
      animation: {
        "chibi-bob": "chibi-bob 2.5s ease-in-out infinite",
        "sparkle": "sparkle 1.5s ease-in-out infinite",
        "float-up": "float-up linear infinite",
        "twinkle": "twinkle 3s ease-in-out infinite",
        "rainbow": "rainbow-text 6s ease infinite",
      },
    },
  },
  plugins: [],
};
