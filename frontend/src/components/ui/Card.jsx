import { motion } from 'framer-motion';
import { getGlassStyle } from '../../theme/glass';

const Card = ({ 
  children, 
  className = '', 
  medical = false,
  hoverable = true,
  clickable = false,
  onClick,
  variant = 'default',
  ...props 
}) => {
  const variants = {
    default: 'glass dark:glass-dark',
    medical: 'glass-medical',
    success: 'glass-success',
    warning: 'glass-warning',
    error: 'glass-error',
  };
  
  const Component = clickable ? motion.button : motion.div;
  
  return (
    <Component
      className={`
        ${variants[medical ? 'medical' : variant]}
        rounded-2xl p-6 border border-white/20
        ${hoverable ? 'hover:scale-[1.02] hover:shadow-lg' : ''}
        ${clickable ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary-500/50' : ''}
        transition-all duration-300
        ${className}
      `}
      whileHover={hoverable ? { y: -2 } : {}}
      whileTap={clickable ? { scale: 0.98 } : {}}
      onClick={onClick}
      {...props}
    >
      {children}
    </Component>
  );
};

export default Card;