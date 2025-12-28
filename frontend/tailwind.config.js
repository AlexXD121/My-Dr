/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      colors: {
        // Your custom color scheme
        primary: {
          50: '#e6f3ff',
          100: '#cce7ff',
          200: '#99cfff',
          300: '#66b7ff',
          400: '#339fff',
          500: '#2D9CDB', // Calm Blue - Primary
          600: '#2485c2',
          700: '#1b6ea9',
          800: '#125790',
          900: '#094077',
          950: '#062a5e',
        },
        
        secondary: {
          50: '#e8f8ff',
          100: '#d1f1ff',
          200: '#a3e3ff',
          300: '#75d5ff',
          400: '#56CCF2', // Light Sky Blue - Secondary
          500: '#47c7ff',
          600: '#3bb8f0',
          700: '#2fa9e1',
          800: '#239ad2',
          900: '#178bc3',
          950: '#0b7cb4',
        },
        
        accent: {
          50: '#e8f5e8',
          100: '#d1ebd1',
          200: '#a3d7a3',
          300: '#75c375',
          400: '#47af47',
          500: '#27AE60', // Healthy Green - Accent
          600: '#229e56',
          700: '#1d8e4c',
          800: '#187e42',
          900: '#136e38',
          950: '#0e5e2e',
        },
        
        background: {
          50: '#F8F9FA', // Soft White - Background
          100: '#f5f6f7',
          200: '#f2f3f4',
          300: '#eff0f1',
          400: '#ecedef',
          500: '#e9eaec',
          600: '#d0d1d3',
          700: '#b7b8ba',
          800: '#9e9fa1',
          900: '#858688',
          950: '#6c6d6f',
        },
        
        textMain: {
          50: '#f5f5f5',
          100: '#e6e6e6',
          200: '#cccccc',
          300: '#b3b3b3',
          400: '#999999',
          500: '#808080',
          600: '#666666',
          700: '#4d4d4d',
          800: '#333333',
          900: '#1A1A1A', // Deep Charcoal - Main Text
          950: '#0d0d0d',
        },
        
        textSubtle: {
          50: '#f8f9fa',
          100: '#f1f3f4',
          200: '#e3e5e8',
          300: '#d5d7dc',
          400: '#c7c9d0',
          500: '#b9bbc4',
          600: '#9ca0ab',
          700: '#7f8592',
          800: '#6B7280', // Medium Gray - Subtle Text
          900: '#4f5967',
          950: '#32394e',
        },
        
        // Medical brand colors (keeping medical theme)
        medical: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#2D9CDB', // Using your primary color
          600: '#2485c2',
          700: '#1b6ea9',
          800: '#125790',
          900: '#094077',
          950: '#062a5e',
        },
        
        // Enhanced status colors
        success: {
          50: '#e8f5e8',
          100: '#d1ebd1',
          200: '#a3d7a3',
          300: '#75c375',
          400: '#47af47',
          500: '#27AE60', // Your accent color
          600: '#229e56',
          700: '#1d8e4c',
          800: '#187e42',
          900: '#136e38',
          950: '#0e5e2e',
        },
        
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        
        // Semantic colors for medical context
        semantic: {
          critical: '#dc2626',
          urgent: '#f59e0b',
          normal: '#27AE60',
          info: '#2D9CDB',
          neutral: '#6B7280',
        },
        
        glass: {
          light: 'rgba(255, 255, 255, 0.1)',
          dark: 'rgba(0, 0, 0, 0.2)',
          medical: 'rgba(45, 156, 219, 0.1)',
          success: 'rgba(39, 174, 96, 0.1)',
          warning: 'rgba(245, 158, 11, 0.1)',
          error: 'rgba(239, 68, 68, 0.1)',
        }
      },
      backdropBlur: {
        xs: '2px',
        '4xl': '72px',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s infinite',
        'bounce-dots': 'bounce-dots 1.4s infinite ease-in-out',
        'gradient': 'gradient-shift 3s ease infinite',
        'fade-in-up': 'fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-in-left': 'slideInLeft 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-in-right': 'slideInRight 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
        'pulse-medical': 'pulse-medical 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(45, 156, 219, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(45, 156, 219, 0.6)' },
        },
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        'pulse-medical': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'bounce-dots': {
          '0%, 80%, 100%': { transform: 'scale(0.8)', opacity: '0.5' },
          '40%': { transform: 'scale(1.2)', opacity: '1' },
        },
        'gradient-shift': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        fadeInUp: {
          'from': { opacity: '0', transform: 'translateY(30px) scale(0.95)' },
          'to': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        slideInLeft: {
          'from': { opacity: '0', transform: 'translateX(-40px) scale(0.95)' },
          'to': { opacity: '1', transform: 'translateX(0) scale(1)' },
        },
        slideInRight: {
          'from': { opacity: '0', transform: 'translateX(40px) scale(0.95)' },
          'to': { opacity: '1', transform: 'translateX(0) scale(1)' },
        },
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(45, 156, 219, 0.37)',
        'glass-light': '0 8px 32px 0 rgba(255, 255, 255, 0.37)',
        'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glow': '0 0 20px rgba(45, 156, 219, 0.3)',
        'glow-lg': '0 0 30px rgba(45, 156, 219, 0.6)',
        'medical': '0 4px 20px rgba(45, 156, 219, 0.2)',
        'success': '0 4px 20px rgba(39, 174, 96, 0.2)',
        'warning': '0 4px 20px rgba(245, 158, 11, 0.2)',
        'error': '0 4px 20px rgba(239, 68, 68, 0.2)',
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'hard': '0 10px 40px -10px rgba(0, 0, 0, 0.2), 0 20px 25px -5px rgba(0, 0, 0, 0.1)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-medical': 'linear-gradient(135deg, #2D9CDB 0%, #2485c2 100%)',
        'gradient-success': 'linear-gradient(135deg, #27AE60 0%, #229e56 100%)',
        'gradient-warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        'gradient-error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'shimmer': 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)',
      },
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
        // Touch device specific breakpoints
        'touch': { 'raw': '(hover: none) and (pointer: coarse)' },
        'no-touch': { 'raw': '(hover: hover) and (pointer: fine)' },
        // Medical device specific
        'tablet-portrait': { 'raw': '(min-width: 768px) and (max-width: 1024px) and (orientation: portrait)' },
        'tablet-landscape': { 'raw': '(min-width: 768px) and (max-width: 1024px) and (orientation: landscape)' },
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // Enhanced border radius for medical UI
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
        '6xl': '3rem',
      },
      
      // Medical-specific font sizes
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.75rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },
      
      // Z-index scale for layering
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    // Custom plugin for glass effects
    function({ addUtilities, theme }) {
      const glassUtilities = {
        '.glass': {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        '.glass-dark': {
          background: 'rgba(0, 0, 0, 0.2)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-medical': {
          background: 'rgba(45, 156, 219, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(45, 156, 219, 0.2)',
          boxShadow: '0 8px 32px 0 rgba(45, 156, 219, 0.2)',
        },
        '.glass-success': {
          background: 'rgba(39, 174, 96, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(39, 174, 96, 0.2)',
          boxShadow: '0 8px 32px 0 rgba(39, 174, 96, 0.2)',
        },
        '.glass-warning': {
          background: 'rgba(245, 158, 11, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          boxShadow: '0 8px 32px 0 rgba(245, 158, 11, 0.2)',
        },
        '.glass-error': {
          background: 'rgba(239, 68, 68, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          boxShadow: '0 8px 32px 0 rgba(239, 68, 68, 0.2)',
        },
        '.gradient-text': {
          background: 'linear-gradient(135deg, #2D9CDB 0%, #2485c2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        },
        '.gradient-text-success': {
          background: 'linear-gradient(135deg, #27AE60 0%, #229e56 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        },
        '.gradient-text-warning': {
          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        },
        '.gradient-text-error': {
          background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        },
        '.mobile-tap-target': {
          minHeight: '44px',
          minWidth: '44px',
        },
      };
      
      addUtilities(glassUtilities);
    },
  ],
}

