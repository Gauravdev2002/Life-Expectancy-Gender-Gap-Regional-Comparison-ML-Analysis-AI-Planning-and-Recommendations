/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette – used throughout the dashboard
        primary:   { DEFAULT: '#1D4ED8', light: '#3B82F6', dark: '#1E40AF' },
        secondary: { DEFAULT: '#0F766E', light: '#14B8A6' },
        accent:    { DEFAULT: '#7C3AED' },
        surface:   { DEFAULT: '#F8FAFC', card: '#FFFFFF', border: '#E2E8F0' },
        text:      { primary: '#0F172A', secondary: '#475569', muted: '#94A3B8' },
        success:   { DEFAULT: '#16A34A', light: '#DCFCE7' },
        warning:   { DEFAULT: '#D97706', light: '#FEF3C7' },
        danger:    { DEFAULT: '#DC2626', light: '#FEE2E2' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
