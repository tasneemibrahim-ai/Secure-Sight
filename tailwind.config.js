/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0A0F1E',
          800: '#0D1526',
          700: '#111C35',
          600: '#162040',
        },
        cyan: {
          DEFAULT: '#00E5FF',
          dim: '#00B8D4',
          glow: 'rgba(0, 229, 255, 0.15)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'ping-slow': 'ping 2.5s cubic-bezier(0, 0, 0.2, 1) infinite',
        'count-up': 'countUp 1s ease-out forwards',
        'gradient': 'gradientShift 8s ease infinite',
        'orbit': 'orbit 12s linear infinite',
        'orbit-reverse': 'orbit 16s linear infinite reverse',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'ray-1': 'ray1 4s ease-in-out infinite',
        'ray-2': 'ray2 4s ease-in-out infinite 0.5s',
        'ray-3': 'ray3 4s ease-in-out infinite 1s',
        'ray-4': 'ray4 4s ease-in-out infinite 1.5s',
        'scan': 'scan 3s linear infinite',
        'particle-1': 'particle1 8s linear infinite',
        'particle-2': 'particle2 10s linear infinite 2s',
        'particle-3': 'particle3 12s linear infinite 4s',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 229, 255, 0.4), 0 0 40px rgba(0, 229, 255, 0.2)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 229, 255, 0.8), 0 0 80px rgba(0, 229, 255, 0.4)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(30px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        orbit: {
          from: { transform: 'rotate(0deg) translateX(130px) rotate(0deg)' },
          to: { transform: 'rotate(360deg) translateX(130px) rotate(-360deg)' },
        },
        ray1: {
          '0%, 100%': { opacity: '0.3', transform: 'scaleX(0.8)' },
          '50%': { opacity: '1', transform: 'scaleX(1.2)' },
        },
        ray2: {
          '0%, 100%': { opacity: '0.2', transform: 'scaleX(0.9)' },
          '50%': { opacity: '0.9', transform: 'scaleX(1.1)' },
        },
        ray3: {
          '0%, 100%': { opacity: '0.4', transform: 'scaleX(1)' },
          '50%': { opacity: '1', transform: 'scaleX(1.3)' },
        },
        ray4: {
          '0%, 100%': { opacity: '0.2', transform: 'scaleX(0.7)' },
          '50%': { opacity: '0.8', transform: 'scaleX(1)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(200%)' },
        },
        particle1: {
          '0%': { transform: 'translate(0, 0) scale(1)', opacity: '0.8' },
          '50%': { transform: 'translate(40px, -60px) scale(1.5)', opacity: '0.4' },
          '100%': { transform: 'translate(80px, -120px) scale(0.5)', opacity: '0' },
        },
        particle2: {
          '0%': { transform: 'translate(0, 0) scale(1)', opacity: '0.6' },
          '50%': { transform: 'translate(-50px, -40px) scale(1.2)', opacity: '0.3' },
          '100%': { transform: 'translate(-100px, -80px) scale(0.3)', opacity: '0' },
        },
        particle3: {
          '0%': { transform: 'translate(0, 0) scale(0.8)', opacity: '0.7' },
          '50%': { transform: 'translate(30px, 50px) scale(1.4)', opacity: '0.35' },
          '100%': { transform: 'translate(60px, 100px) scale(0.2)', opacity: '0' },
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 229, 255, 0.4), 0 0 60px rgba(0, 229, 255, 0.1)',
        'glow-cyan-lg': '0 0 40px rgba(0, 229, 255, 0.6), 0 0 80px rgba(0, 229, 255, 0.2)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4)',
        'card-hover': '0 20px 60px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 229, 255, 0.2)',
      },
    },
  },
  plugins: [],
}
