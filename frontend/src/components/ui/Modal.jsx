import { motion, AnimatePresence } from 'framer-motion';
import { useEffect } from 'react';
import { Icon } from './Icon';
import Button from './Button';
import { getGlassStyle } from '../../theme/glass';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md',
  medical = false,
  showCloseButton = true,
  closeOnOverlayClick = true,
  className = '',
  headerActions,
  footer
}) => {
  const sizes = {
    xs: 'max-w-sm',
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
    full: 'max-w-[95vw]',
  };
  
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);
  
  const glassVariant = medical ? 'medical' : 'auto';
  
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={closeOnOverlayClick ? onClose : undefined}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className={`
              ${sizes[size]} w-full max-h-[90vh] overflow-hidden
              rounded-3xl shadow-2xl border
              ${medical ? 'glass-medical' : 'glass dark:glass-dark'}
              ${className}
            `}
            style={getGlassStyle(glassVariant)}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? "modal-title" : undefined}
          >
            {/* Header */}
            {(title || showCloseButton || headerActions) && (
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <div className="flex items-center gap-3">
                  {medical && (
                    <div className="w-10 h-10 bg-gradient-to-r from-medical-500 to-medical-600 rounded-xl flex items-center justify-center">
                      <Icon name="stethoscope" size={20} className="text-white" />
                    </div>
                  )}
                  {title && (
                    <h2 
                      id="modal-title"
                      className="text-xl font-semibold text-textMain-900 dark:text-white"
                    >
                      {title}
                    </h2>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  {headerActions}
                  {showCloseButton && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={onClose}
                      icon="close"
                      className="w-8 h-8 p-0 rounded-lg"
                      aria-label="Close modal"
                    />
                  )}
                </div>
              </div>
            )}
            
            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {children}
            </div>
            
            {/* Footer */}
            {footer && (
              <div className="p-6 border-t border-white/10 bg-background-50/50 dark:bg-textMain-800/50">
                {footer}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal;