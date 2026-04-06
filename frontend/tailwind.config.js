/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        amazon: {
          dark: "#131921",
          light: "#232f3e",
          accent: "#febd69",
        },
      },
    },
  },
  plugins: [],
};
