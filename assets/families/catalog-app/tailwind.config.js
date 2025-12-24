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
          // Paleta basada en logo BIMAC (gradiente naranja → rojo)
          primary: '#E65100',      // Naranja profundo (header, botones principales)
          secondary: '#FF8A65',    // Naranja claro (badges, highlights)
          accent: '#D32F2F',       // Rojo (CTAs, enlaces activos)
          light: '#FFF3E0',        // Crema claro (fondos suaves)
          dark: '#1A1A1A',         // Negro carbón (footer, textos)
          // Colores adicionales
          orange: {
            50: '#FFF3E0',
            100: '#FFE0B2',
            200: '#FFCC80',
            300: '#FFB74D',
            400: '#FFA726',
            500: '#FF9800',
            600: '#FB8C00',
            700: '#F57C00',
            800: '#EF6C00',
            900: '#E65100'
          }
        }
      }
    },
  },
  plugins: [],
}
