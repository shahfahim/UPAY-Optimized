import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import path from 'path'
import { fileURLToPath } from 'url'

// const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react(), tailwindcss()],

  server: {
    proxy: { '/api': 'http://localhost:8000' },
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
        // path.resolve(__dirname, '../backend/**'), // Removing these complex rules to prevent build failure
        // path.resolve(__dirname, '../**/*.py'),
      ],
      usePolling: false,
    },
    hmr: {
      timeout: 5000,
    },
  },
  optimizeDeps: {
    entries: ['src/**/*.{ts,tsx}'],
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
