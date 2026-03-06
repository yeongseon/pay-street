/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0a0f',
        surface: '#0f0f17',
        card: '#13131f',
        border: '#1e1e2e',
        accent: '#e4ff3d',
        'accent-dim': '#b8cc2a',
        muted: '#4a4a6a',
        text: '#e8e8f0',
        'text-dim': '#8888aa',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Syne"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

