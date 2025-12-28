import { motion } from 'framer-motion';
import { forwardRef } from 'react';
import { Icon } from './Icon';
import LoadingSpinner from '../LoadingSpinner';

const Button = forwardRef(({ 
  variant = 'primary',
  size = 'md',
  children,
  loading = false,
  disabled = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  medical = false,
  className = '',
  onClick,
  ...props 
}, ref) => {
  const variants = {
    primary: 'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-medical',
    secondary: 'glass dark:glass-dark text-textMain-700 dark:text-textSubtle-300 hover:bg-white/20 dark:hover:bg-black/20',
    medical: 'bg-gradient-to-r from-medical-500 to-medical-600 text-white hover:from-medical-600 hover:to-medical-700 shadow-medical',
    success: 'bg-gradient-to-r from-success-500 to-success-600 text-white hover:from-success-600 hover:to-success-700 shadow-success',
    warning: 'bg-gradient-to-r from-warning-500 to-warning-600 text-white hover:from-warning-600 hover:to-warning-700 shadow-warning',
    error: 'bg-gradient-to-r from-error-500 to-error-600 text-white hover:from-error-600 hover:to-error-700 shadow-error',
    ghost: 'text-textMain-700 dark:text-textSubtle-300 hover:bg-background-100 dark:hover:bg-textMain-800',
    outline: 'border-2 border-primary-500 text-primary-600 hover:bg-primary-500 hover:text-white dark:border-primary-400 dark:text-primary-400',
  };
  
  const sizes = {
    xs: 'px-2 py-1 text-xs min-h-[32px]',
    sm: 'px-3 py-2 text-sm min-h-[36px]',
    md: 'px-4 py-3 text-base min-h-[44px]',
    lg: 'px-6 py-4 text-lg min-h-[52px]',
    xl: 'px-8 py-5 text-xl min-h-[60px]',
  };
  
  const isDisabled = disabled || loading;
  
  return (
    <motion.button
      ref={ref}
      className={`
        ${variants[medical ? 'medical' : variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        rounded-2xl font-medium transition-all duration-300
        flex items-center justify-center gap-2
        mobile-tap-target relative overflow-hidden
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2
        ${className}
      `}
      whileHover={!isDisabled ? { scale: 1.02 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      disabled={isDisabled}
      onClick={onClick}
      {...props}
    >
      {/* Loading overlay */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-black/10 flex items-center justify-center"
        >
          <LoadingSpinner size="sm" />
        </motion.div>
      )}
      
      {/* Content */}
      <div className={`flex items-center gap-2 ${loading ? 'opacity-0' : 'opacity-100'}`}>
        {icon && iconPosition === 'left' && (
          <Icon name={icon} size={size === 'xs' ? 14 : size === 'sm' ? 16 : 18} />
        )}
        {children}
        {icon && iconPosition === 'right' && (
          <Icon name={icon} size={size === 'xs' ? 14 : size === 'sm' ? 16 : 18} />
        )}
      </div>
      
      {/* Ripple effect */}
      <motion.div
        className="absolute inset-0 bg-white/20 rounded-2xl"
        initial={{ scale: 0, opacity: 1 }}
        animate={{ scale: 2, opacity: 0 }}
        transition={{ duration: 0.6 }}
        style={{ pointerEvents: 'none' }}
      />
    </motion.button>
  );
});

Button.displayName = 'Button';

export default Button;