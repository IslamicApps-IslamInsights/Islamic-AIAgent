import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';
import path from 'path';

export default defineConfig(({ command }) => ({
  plugins: [
    react(),
    command === 'build' ? cssInjectedByJsPlugin() : null,
  ].filter(Boolean),
  server: {
    port: 3001,
    host: 'localhost',
    strictPort: true,
    hmr: {
      host: 'localhost',
      port: 3001,
      protocol: 'ws',
    },
  },
  build: {
    chunkSizeWarningLimit: 2000,
    cssCodeSplit: false,
    lib: {
      entry: path.resolve(__dirname, 'src/widget-entry.tsx'),
      name: 'IslamicAIWidget',
      fileName: (format) => `islamic-ai-widget.${format === 'iife' ? 'js' : format + '.js'}`,
      formats: ['iife'],
    },
    rollupOptions: {
      external: ['react', 'react-dom', 'framer-motion', 'lucide-react'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
          'framer-motion': 'Motion',
          'lucide-react': 'Lucide',
        },
        compact: true,
      },
    },
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
  },
}));
