import type { Config } from "tailwindcss";

// Atelier Digital — warm, gallery-grade editorial design system.
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: { base: "#FBFBF9", subtle: "#F5F5F0" },
        surface: { card: "#FFFFFF", DEFAULT: "#FBFBF9" },
        hairline: "#EAE8E2",
        "hairline-strong": "#E2E0D8",
        ink: {
          DEFAULT: "#121212",
          secondary: "#262626",
          muted: "#71716D",
        },
        accent: {
          DEFAULT: "#D96B27",
          subtle: "#FDF1E9",
          border: "#F3D6C2",
        },
        cobalt: "#2C3E50",
        danger: "#BA1A1A",
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        float:
          "0 12px 36px -4px rgba(18,18,18,0.06), 0 4px 12px -2px rgba(18,18,18,0.03)",
        hair: "0 1px 8px rgba(18,18,18,0.03)",
      },
    },
  },
  plugins: [],
} satisfies Config;
