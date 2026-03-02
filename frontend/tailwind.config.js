/** @type {import('tailwindcss').Config} */
// Tailwind CSS configuration — scans both React components and Django templates
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",     // React frontend components
    "../templates/**/*.html",          // Project-level Django templates
    "../**/templates/**/*.html",       // App-level Django templates
  ],
  theme: {
    extend: {
      // Custom indigo/violet color palette used throughout the app
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
      },
    },
  },
  plugins: [],
}
