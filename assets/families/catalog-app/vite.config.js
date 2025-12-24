import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Genera un solo archivo JS para fácil embed en WordPress
    rollupOptions: {
      output: {
        manualChunks: undefined,
        entryFileNames: 'bimac-catalog.js',
        chunkFileNames: 'bimac-catalog.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.endsWith('.css')) {
            return 'bimac-catalog.css'
          }
          return 'assets/[name][extname]'
        }
      }
    }
  }
})
