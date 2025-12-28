export const glassStyles = {
  base: {
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)', // Safari support
    borderRadius: '1rem',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  
  light: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  },
  
  dark: {
    background: 'rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  
  medical: {
    background: 'rgba(45, 156, 219, 0.1)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    boxShadow: '0 8px 32px 0 rgba(45, 156, 219, 0.2)',
    border: '1px solid rgba(45, 156, 219, 0.2)',
  },
  
  success: {
    background: 'rgba(39, 174, 96, 0.1)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    boxShadow: '0 8px 32px 0 rgba(39, 174, 96, 0.2)',
    border: '1px solid rgba(39, 174, 96, 0.2)',
  },
  
  warning: {
    background: 'rgba(245, 158, 11, 0.1)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    boxShadow: '0 8px 32px 0 rgba(245, 158, 11, 0.2)',
    border: '1px solid rgba(245, 158, 11, 0.2)',
  },
  
  error: {
    background: 'rgba(239, 68, 68, 0.1)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRadius: '1rem',
    boxShadow: '0 8px 32px 0 rgba(239, 68, 68, 0.2)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
  }
};

// CSS-in-JS helper
export const getGlassStyle = (variant = 'light', darkMode = false) => {
  if (variant === 'auto') {
    return darkMode ? glassStyles.dark : glassStyles.light;
  }
  return glassStyles[variant] || glassStyles.light;
};