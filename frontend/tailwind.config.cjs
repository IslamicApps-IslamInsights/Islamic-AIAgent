/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'islamic-bg': '#011412',
        'islamic-deep': '#000B0A',
        'gold-primary': '#E5C06F',
        'teal-deep': '#021a1a',
        'teal-primary': '#042b2b',
        gold: {
          light: '#F7E7C0',
          DEFAULT: '#E5C06F',
          dark: '#AD8B3A',
        },
        moss: {
          light: '#2d5a2d',
          DEFAULT: '#1b3d1a',
          dark: '#0e2410',
        },
        antique: '#021a1a',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        outfit: ['Outfit', 'sans-serif'],
        amiri: ['Amiri', 'serif'],
        playfair: ['Playfair Display', 'serif'],
      },
      animation: {
        'slide-up': 'slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-slow': 'pulse-soft 8s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 10s linear infinite',
      },
      keyframes: {
        slideUp: {
          from: { opacity: '0', transform: 'translateY(40px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.05)' },
        }
      }
    },
  },
  plugins: [],
}
