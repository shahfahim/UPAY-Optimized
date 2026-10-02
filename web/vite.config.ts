import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],

  server: {
    proxy: { '/api': 'http://localhost:8000' },

    // ── Stable file watcher (Windows fix) ──────────────────────────────────
    watch: {
      // Ignore backend Python files + patch scripts → no more surprise restarts
      ignored: [
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
        path.resolve(__dirname, '../backend/**'),
        path.resolve(__dirname, '../**/*.py'),
      ],
      // Use native FS events on Windows — NOT polling (polling causes CPU spike
      // and false-positive restarts on network/temp file changes)
      usePolling: false,
    },

    hmr: {
      // Give HMR extra time on slow Windows FS events
      timeout: 5000,
    },
  },

  // Restrict dep optimizer scan to src only
  optimizeDeps: {
    entries: ['src/**/*.{ts,tsx}'],
  },

  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})

