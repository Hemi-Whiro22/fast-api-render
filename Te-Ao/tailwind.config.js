/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        koru: {
          night: "#020617",
          fern: "#064e3b",
          tide: "#0f172a",
          mist: "#94a3b8",
        },
      },
      boxShadow: {
        koru: "0 20px 50px -15px rgba(16, 185, 129, 0.35)",
      },
    },
  },
  plugins: [],
};
