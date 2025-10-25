/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        glass: "rgba(255, 255, 255, 0.7)",
        primary: {
          light: "#8ec5fc",
          DEFAULT: "#6fb1fc",
          dark: "#5a93d8"
        },
        accent: "#cfd9df"
      },
      boxShadow: {
        glass: "20px 20px 40px rgba(163, 177, 198, 0.6), -20px -20px 60px rgba(255, 255, 255, 0.8)",
        inset: "inset 10px 10px 20px rgba(163, 177, 198, 0.6), inset -10px -10px 20px rgba(255, 255, 255, 0.9)"
      },
      backdropBlur: {
        xs: "2px"
      }
    }
  },
  plugins: []
};
