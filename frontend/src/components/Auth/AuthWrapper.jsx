import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Login from '../Login';
import Signup from '../Signup';
import LoadingSpinner from '../LoadingSpinner';
import EmailVerification from './EmailVerification';

const AuthWrapper = ({ children }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [demoMode, setDemoMode] = useState(false);
  const { currentUser, loading } = useAuth();
  
  const isAuthenticated = !!currentUser;
  const isVerified = currentUser?.emailVerified || false;

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Loading your medical assistant...
          </p>
        </div>
      </div>
    );
  }

  // Show email verification if user is authenticated but not verified
  if (isAuthenticated && !isVerified) {
    return <EmailVerification user={currentUser} />;
  }

  // Show main app if user is authenticated and verified, or in demo mode
  if ((isAuthenticated && isVerified) || demoMode) {
    return children;
  }

  // Show authentication forms if not authenticated
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-gray-50 to-slate-50 dark:from-blue-900/20 dark:via-gray-900/10 dark:to-slate-900/20">
      <div className="w-full max-w-md mx-auto p-6">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          {isLoginMode ? (
            <Login onSwitchToSignup={() => setIsLoginMode(false)} />
          ) : (
            <Signup onSwitchToLogin={() => setIsLoginMode(true)} />
          )}
        </div>
        
        {/* Demo mode notice */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            For demo purposes, you can also continue without authentication
          </p>
          <button
            onClick={() => setDemoMode(true)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline"
          >
            Continue in Demo Mode
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthWrapper;