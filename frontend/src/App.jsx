import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster } from 'react-hot-toast';

import "./App.css";
import { ThemeProvider } from "./components/ThemeProvider";
import { AuthProvider } from "./contexts/AuthContext";
import AuthWrapper from "./components/Auth/AuthWrapper";
import ParticleBackground from "./components/ParticleBackground";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Mainbox from "./components/MainBox";
import SymptomChecker from "./components/SymptomChecker";
import MedicalHistory from "./components/MedicalHistory";
import DrugInteractions from "./components/DrugInteractions";
import HealthTips from "./components/HealthTips";
import UserProfile from "./components/UserProfile";
import HealthAnalyticsDashboard from "./components/HealthAnalyticsDashboard";
import ConnectionStatus from "./components/ConnectionStatus";
import MobileBottomNav from "./components/MobileBottomNav";
import PWAInstallPrompt from "./components/PWAInstallPrompt";
import TestPage from "./components/TestPage";
import { useAuth } from "./contexts/AuthContext";
import accessibilityService from "./services/accessibilityService";

function AppContent() {
  const { logout } = useAuth();

  // UI states
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") === "dark");
  const [symptomCheckerOpen, setSymptomCheckerOpen] = useState(false);
  const [medicalHistoryOpen, setMedicalHistoryOpen] = useState(false);
  const [drugInteractionsOpen, setDrugInteractionsOpen] = useState(false);
  const [healthTipsOpen, setHealthTipsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [testPageOpen, setTestPageOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');

  // Sync dark mode class on <html> element and initialize accessibility
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    // Initialize accessibility service
    accessibilityService.init();
  }, [darkMode]);

  // Toggle sidebar open/close
  const toggleSidebar = useCallback(() => setSidebarOpen((open) => !open), []);

  // Toggle dark mode and save preference
  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      const newMode = !prev;
      localStorage.setItem("theme", newMode ? "dark" : "light");
      return newMode;
    });
  }, []);

  // Close all page modals
  const closeAll = useCallback(() => {
    setSymptomCheckerOpen(false);
    setMedicalHistoryOpen(false);
    setDrugInteractionsOpen(false);
    setHealthTipsOpen(false);
    setProfileOpen(false);
    setAnalyticsOpen(false);
    setTestPageOpen(false);
  }, []);

  // Open one page modal and close others, also close sidebar
  const openPage = useCallback(
    (pageSetter, tabName) => {
      closeAll();
      pageSetter(true);
      setSidebarOpen(false);
      setActiveTab(tabName);
    },
    [closeAll]
  );

  // Close sidebar on Escape key for accessibility
  useEffect(() => {
    function onKeyDown(e) {
      if (e.key === "Escape" && sidebarOpen) {
        setSidebarOpen(false);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [sidebarOpen]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div
      className="font-inter min-h-screen w-full relative overflow-hidden bg-white dark:bg-gray-900 text-black dark:text-white"
      tabIndex={-1}
      aria-live="polite"
      aria-atomic="true"
    >

      {/* Particle background */}
      <ParticleBackground particleCount={25} />

      <motion.div
        className="relative z-10 min-h-screen w-full flex flex-col"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {/* Sidebar overlay */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              key="overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.4 }}
              exit={{ opacity: 0 }}
              className="fixed top-0 left-0 w-full h-full bg-black z-30 backdrop-blur-sm"
              onClick={toggleSidebar}
              role="button"
              aria-label="Close sidebar overlay"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  toggleSidebar();
                }
              }}
            />
          )}
        </AnimatePresence>

        {/* Header */}
        <Header
          toggleSidebar={toggleSidebar}
          toggleDarkMode={toggleDarkMode}
          darkMode={darkMode}
          onLogout={handleLogout}
          onProfileClick={() => setProfileOpen(true)}
          onSymptomCheckerClick={() => openPage(setSymptomCheckerOpen, 'symptoms')}
          onMedicalHistoryClick={() => openPage(setMedicalHistoryOpen, 'history')}
          onDrugInteractionsClick={() => openPage(setDrugInteractionsOpen, 'drugs')}
          onHealthTipsClick={() => openPage(setHealthTipsOpen, 'tips')}
          onAnalyticsClick={() => openPage(setAnalyticsOpen, 'analytics')}
          onTestPageClick={() => openPage(setTestPageOpen, 'test')}
        />

        {/* Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onProfileClick={() => setProfileOpen(true)}
          onSymptomCheckerClick={() => openPage(setSymptomCheckerOpen, 'symptoms')}
          onMedicalHistoryClick={() => openPage(setMedicalHistoryOpen, 'history')}
          onDrugInteractionsClick={() => openPage(setDrugInteractionsOpen, 'drugs')}
          onHealthTipsClick={() => openPage(setHealthTipsOpen, 'tips')}
          onAnalyticsClick={() => openPage(setAnalyticsOpen, 'analytics')}
        />

        {/* Main content area */}
        <div id="main-content" className="flex-1 flex flex-col">
          <AnimatePresence mode="wait">
            {symptomCheckerOpen && (
              <motion.div
                key="symptom-checker"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <SymptomChecker
                  isOpen={symptomCheckerOpen}
                  onClose={() => setSymptomCheckerOpen(false)}
                  darkMode={darkMode}
                />
              </motion.div>
            )}

            {medicalHistoryOpen && (
              <motion.div
                key="medical-history"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <MedicalHistory
                  isOpen={medicalHistoryOpen}
                  onClose={() => setMedicalHistoryOpen(false)}
                  darkMode={darkMode}
                />
              </motion.div>
            )}

            {drugInteractionsOpen && (
              <motion.div
                key="drug-interactions"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <DrugInteractions
                  isOpen={drugInteractionsOpen}
                  onClose={() => setDrugInteractionsOpen(false)}
                  darkMode={darkMode}
                />
              </motion.div>
            )}

            {healthTipsOpen && (
              <motion.div
                key="health-tips"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <HealthTips
                  isOpen={healthTipsOpen}
                  onClose={() => setHealthTipsOpen(false)}
                  darkMode={darkMode}
                />
              </motion.div>
            )}

            {analyticsOpen && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <HealthAnalyticsDashboard />
              </motion.div>
            )}

            {testPageOpen && (
              <motion.div
                key="test-page"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="flex-1 flex flex-col"
              >
                <TestPage />
              </motion.div>
            )}

            {/* Default Mainbox */}
            {!symptomCheckerOpen && !medicalHistoryOpen && !drugInteractionsOpen && !healthTipsOpen && !analyticsOpen && !testPageOpen && (
              <motion.div
                key="mainbox"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
                className="flex-1 flex flex-col"
              >
                <Mainbox />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Mobile Bottom Navigation */}
        <MobileBottomNav
          activeTab={activeTab}
          onChatClick={() => {
            closeAll();
            setActiveTab('chat');
          }}
          onSymptomCheckerClick={() => openPage(setSymptomCheckerOpen, 'symptoms')}
          onMedicalHistoryClick={() => openPage(setMedicalHistoryOpen, 'history')}
          onDrugInteractionsClick={() => openPage(setDrugInteractionsOpen, 'drugs')}
          onAnalyticsClick={() => openPage(setAnalyticsOpen, 'analytics')}
          onProfileClick={() => setProfileOpen(true)}
        />

        {/* User Profile Modal */}
        <UserProfile
          isOpen={profileOpen}
          onClose={() => setProfileOpen(false)}
          darkMode={darkMode}
          onDarkModeChange={toggleDarkMode}
        />

        {/* Connection Status Indicator */}
        <ConnectionStatus />

        {/* PWA Install Prompt */}
        <PWAInstallPrompt />

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: darkMode ? 'rgba(55, 65, 81, 0.95)' : 'rgba(255, 255, 255, 0.95)',
              color: darkMode ? '#f3f4f6' : '#1f2937',
              border: darkMode ? '1px solid rgba(75, 85, 99, 0.3)' : '1px solid rgba(229, 231, 235, 0.3)',
              borderRadius: '16px',
              fontSize: '14px',
              maxWidth: '400px',
              backdropFilter: 'blur(12px)',
              boxShadow: darkMode 
                ? '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1)' 
                : '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#ffffff'
              }
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#ffffff'
              }
            }
          }}
        />
      </motion.div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AuthWrapper>
          <AppContent />
        </AuthWrapper>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;