import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Sidebar({
  isOpen,
  onClose,
  onProfileClick,
  onSymptomCheckerClick,
  onMedicalHistoryClick,
  onDrugInteractionsClick,
  onHealthTipsClick,
  onAnalyticsClick,
}) {
  // Demo user for display
  const currentUser = { displayName: 'Demo User', email: 'demo@example.com' };
  const [dragOffset, setDragOffset] = useState(0);
  
  useEffect(() => {
    const mainContent = document.getElementById("main-content");
    if (!mainContent) return;

    if (isOpen) {
      mainContent.classList.add("blur-sm", "pointer-events-none", "transition-blur", "duration-300");
    } else {
      mainContent.classList.remove("blur-sm", "pointer-events-none", "transition-blur", "duration-300");
    }

    // Cleanup on unmount
    return () => {
      mainContent.classList.remove("blur-sm", "pointer-events-none", "transition-blur", "duration-300");
    };
  }, [isOpen]);

  // Handler to wrap click and close sidebar if onClose exists
  const handleClick = (handler) => () => {
    if (typeof handler === "function") handler();
    if (typeof onClose === "function") onClose();
  };

  // Handle swipe to close on mobile
  const handleDragEnd = (_, info) => {
    const threshold = 100;
    if (info.offset.x > threshold) {
      onClose();
    }
    setDragOffset(0);
  };

  const handleDrag = (_, info) => {
    if (info.offset.x > 0) {
      setDragOffset(info.offset.x);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Mobile overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-30 lg:hidden"
          />
          
          {/* Sidebar */}
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: dragOffset }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            drag="x"
            dragConstraints={{ left: 0, right: 300 }}
            dragElastic={0.2}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
            className="font-poppins fixed top-0 right-0 z-40 h-full 
              w-full sm:w-80 md:w-96 lg:w-80
              bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 
              shadow-2xl border-l border-gray-200 dark:border-gray-700
              flex flex-col swipeable pt-safe-top pb-safe-bottom"
            aria-label="Navigation menu"
            role="complementary"
          >
            <div className="p-4 sm:p-6 flex flex-col h-full">
              {/* Swipe indicator */}
              <div className="flex justify-center mb-4 lg:hidden">
                <div className="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full" />
              </div>

              {/* Header with close button */}
              <div className="flex items-center justify-between mb-6 sm:mb-8">
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
                  Menu
                </h2>
                <motion.button
                  onClick={onClose}
                  aria-label="Close menu"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 sm:p-3 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 
                    transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 mobile-tap-target"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </div>

              {/* User Profile Section */}
              <motion.div 
                className="mb-4 sm:mb-6 p-3 sm:p-4 bg-gray-50 dark:bg-gray-700 rounded-xl"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-600 to-gray-800 rounded-full flex items-center justify-center">
                    <span className="text-base sm:text-lg font-bold text-white">
                      {currentUser?.displayName ? currentUser.displayName.charAt(0).toUpperCase() : 
                       currentUser?.email ? currentUser.email.charAt(0).toUpperCase() : 'U'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 dark:text-white truncate text-sm sm:text-base">
                      {currentUser?.displayName || 'User'}
                    </div>
                    <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">
                      {currentUser?.email}
                    </div>
                  </div>
                </div>
                <motion.button
                  onClick={handleClick(onProfileClick)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full mt-3 px-3 py-2 sm:py-3 text-sm bg-gradient-to-r from-blue-600 to-gray-800 
                    hover:from-blue-700 hover:to-gray-900 text-white rounded-lg transition-colors duration-200
                    mobile-tap-target"
                >
                  View Profile
                </motion.button>
              </motion.div>

              {/* Navigation */}
              <nav aria-label="Main navigation" className="flex-grow">
                <ul className="space-y-1 sm:space-y-2">
                  {[
                    { 
                      icon: '🩺', 
                      title: 'Symptom Checker', 
                      subtitle: 'Check symptoms', 
                      onClick: onSymptomCheckerClick 
                    },
                    { 
                      icon: '📋', 
                      title: 'Medical History', 
                      subtitle: 'View history', 
                      onClick: onMedicalHistoryClick 
                    },
                    { 
                      icon: '💊', 
                      title: 'Drug Interactions', 
                      subtitle: 'Check interactions', 
                      onClick: onDrugInteractionsClick 
                    },
                    { 
                      icon: '💡', 
                      title: 'Health Tips', 
                      subtitle: 'Get health tips', 
                      onClick: onHealthTipsClick 
                    },
                    { 
                      icon: '📊', 
                      title: 'Health Analytics', 
                      subtitle: 'Track your health', 
                      onClick: onAnalyticsClick 
                    }
                  ].map((item, index) => (
                    <motion.li
                      key={item.title}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 + index * 0.05 }}
                    >
                      <motion.button
                        onClick={handleClick(item.onClick)}
                        whileHover={{ scale: 1.02, x: 4 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-xl text-left 
                          hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200 
                          focus:outline-none focus:ring-2 focus:ring-gray-500 group mobile-tap-target"
                      >
                        <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gray-100 dark:bg-gray-800 rounded-lg 
                          flex items-center justify-center group-hover:bg-gray-200 dark:group-hover:bg-gray-700 
                          transition-colors duration-200 text-lg sm:text-xl">
                          {item.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 dark:text-white text-sm sm:text-base truncate">
                            {item.title}
                          </div>
                          <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">
                            {item.subtitle}
                          </div>
                        </div>
                        <div className="text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </motion.button>
                    </motion.li>
                  ))}
                </ul>
              </nav>


              {/* Footer */}
              <motion.div 
                className="pt-4 sm:pt-6 border-t border-gray-200 dark:border-gray-700"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center">
                  MyDoc AI - Your medical assistant
                </div>
              </motion.div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}