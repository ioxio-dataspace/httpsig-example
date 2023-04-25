import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      "/api": `http://127.0.0.1:8088`,
      "/.well-known": `http://127.0.0.1:8088`,
    },
  },
  plugins: [react()],
  build: {
    outDir: "dist",
  },
})
