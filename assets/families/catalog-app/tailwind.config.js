/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bimac: {
          primary: '#1e3a5f',
          secondary: '#3d5a80',
          accent: '#ee6c4d',
          light: '#e0fbfc',
          dark: '#293241'
        }
      }
    },
  },
  plugins: [],
}
