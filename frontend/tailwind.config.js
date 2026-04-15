/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#e8edfc',
          100: '#c5d0f7',
          200: '#9bb0f0',
          300: '#7090e8',
          400: '#4f77e3',
          500: '#2e5edd',
          600: '#002FA7', // PENS Blue — main
          700: '#002890',
          800: '#002079',
          900: '#001862',
          950: '#000f3d',
        },
        accent: {
          orange: '#FF6B35',
          teal: '#00C9A7',
          gold: '#FFB800',
        },
      },
      animation: {
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16,1,0.3,1)',
        'fade-in': 'fadeIn 0.5s ease-in',
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out 2s infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'typing-dot': 'typingDot 1.4s ease-in-out infinite',
        'slide-in-right': 'slideInRight 0.5s cubic-bezier(0.16,1,0.3,1)',
        'bounce-in': 'bounceIn 0.6s cubic-bezier(0.68,-0.55,0.265,1.55)',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(24px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0, 47, 167, 0.4)' },
          '50%': { boxShadow: '0 0 0 12px rgba(0, 47, 167, 0)' },
        },
        typingDot: {
          '0%, 60%, 100%': { transform: 'translateY(0)', opacity: '0.4' },
          '30%': { transform: 'translateY(-6px)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
