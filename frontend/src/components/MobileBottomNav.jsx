import { motion } from 'framer-motion';
import { FiActivity, FiHeart, FiBookOpen, FiBarChart, FiUser } from 'react-icons/fi';
import { RiCapsuleLine } from 'react-icons/ri';

export default function MobileBottomNav({
  onChatClick,
  onSymptomCheckerClick,
  onMedicalHistoryClick,
  onDrugInteractionsClick,
  onAnalyticsClick,
  onProfileClick,
  activeTab = 'chat'
}) {
  const navItems = [
    { 
      id: 'chat', 
      icon: FiActivity, 
      label: 'Chat', 
      onClick: onChatClick 
    },
    { 
      id: 'symptoms', 
      icon: FiHeart, 
      label: 'Symptoms', 
      onClick: onSymptomCheckerClick 
    },
    { 
      id: 'history', 
      icon: FiBookOpen, 
      label: 'History', 
      onClick: onMedicalHistoryClick 
    },
    { 
      id: 'drugs', 
      icon: RiCapsuleLine, 
      label: 'Drugs', 
      onClick: onDrugInteractionsClick 
    },
    { 
      id: 'analytics', 
      icon: FiBarChart, 
      label: 'Analytics', 
      onClick: onAnalyticsClick 
    }
  ];

  return (
    <motion.nav
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed bottom-0 left-0 right-0 z-50 lg:hidden bg-white/90 dark:bg-gray-900/90 
        backdrop-blur-xl border-t border-gray-200/50 dark:border-gray-700/50 pb-safe-bottom"
    >
      <div className="flex items-center justify-around px-2 py-2">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={item.onClick}
              className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all duration-200
                mobile-tap-target ${
                isActive 
                  ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30' 
                  : 'text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <motion.div
                animate={isActive ? { scale: 1.1 } : { scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <Icon size={20} />
              </motion.div>
              <span className="text-xs mt-1 font-medium">{item.label}</span>
              
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute -top-0.5 left-1/2 transform -translate-x-1/2 w-8 h-0.5 
                    bg-blue-600 dark:bg-blue-400 rounded-full"
                  initial={false}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.nav>
  );
}