/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        darkBg: '#0f172a',
        darkCard: '#1e293b'
      }
    }
  },
  plugins: [],
}
