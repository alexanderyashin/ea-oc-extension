import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Reproducible default: stable dev port (fail fast on conflicts)
    port: 5173,
    strictPort: true,
  },
})
