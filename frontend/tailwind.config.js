/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['"Instrument Sans"', 'sans-serif'],
      },
      colors: {
        ink: { DEFAULT: '#101828', soft: '#1f2937' },
        sand: { DEFAULT: '#f7f4ed', light: '#fbf9f4', dark: '#ede7db' },
        teal: { DEFAULT: '#0f766e', soft: '#5eead4', dark: '#115e59' },
        sun: { DEFAULT: '#f59e0b', soft: '#fde68a' },
        clay: { DEFAULT: '#c2410c', soft: '#fed7aa' }
      },
      boxShadow: {
        glow: '0 18px 40px rgba(15, 118, 110, 0.18)'
      }
    },
  },
  plugins: [],
}
