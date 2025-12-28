import { useState, useEffect } from 'react';
import { sendEmailVerification, reload } from 'firebase/auth';
import { useAuth } from '../../contexts/AuthContext';
import { FaEnvelope, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';

const EmailVerification = ({ user }) => {
  const [isResending, setIsResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [verificationSent, setVerificationSent] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const { logout } = useAuth();

  // Cooldown timer for resend button
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  // Auto-check verification status periodically
  useEffect(() => {
    const checkVerification = async () => {
      if (user && !isChecking) {
        setIsChecking(true);
        try {
          await reload(user);
          // The auth state will update automatically if verification status changes
        } catch (error) {
          console.error('Error checking verification status:', error);
        } finally {
          setIsChecking(false);
        }
      }
    };

    // Check every 5 seconds
    const interval = setInterval(checkVerification, 5000);
    return () => clearInterval(interval);
  }, [user, isChecking]);

  const handleResendVerification = async () => {
    if (!user || resendCooldown > 0) return;

    setIsResending(true);
    try {
      await sendEmailVerification(user);
      setVerificationSent(true);
      setResendCooldown(60); // 60 second cooldown
    } catch (error) {
      console.error('Error resending verification email:', error);
    } finally {
      setIsResending(false);
    }
  };

  const handleCheckNow = async () => {
    if (!user || isChecking) return;

    setIsChecking(true);
    try {
      await reload(user);
      if (user.emailVerified) {
        // Verification status will update automatically
        return;
      }
    } catch (error) {
      console.error('Error checking verification:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-gray-50 to-slate-50 dark:from-blue-900/20 dark:via-gray-900/10 dark:to-slate-900/20 p-6">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
          {/* Header */}
          <div className="mb-6">
            <div className="bg-blue-100 dark:bg-blue-900/30 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <FaEnvelope className="text-blue-600 dark:text-blue-400 text-2xl" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Verify Your Email
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              We've sent a verification link to
            </p>
            <p className="text-gray-900 dark:text-white font-medium mt-1">
              {user?.email}
            </p>
          </div>

          {/* Status Messages */}
          {verificationSent && (
            <div className="mb-6 p-3 bg-green-100 dark:bg-green-900/30 border border-green-400 dark:border-green-600 text-green-700 dark:text-green-300 rounded-xl text-sm flex items-center gap-2">
              <FaCheckCircle />
              <span>Verification email sent! Check your inbox and spam folder.</span>
            </div>
          )}

          {/* Instructions */}
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl text-left">
            <h3 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <FaExclamationTriangle className="text-yellow-500 text-sm" />
              Next Steps:
            </h3>
            <ol className="text-sm text-gray-600 dark:text-gray-400 space-y-1 list-decimal list-inside">
              <li>Check your email inbox for a verification message</li>
              <li>Click the verification link in the email</li>
              <li>Return to this page and click "I've Verified My Email"</li>
            </ol>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleCheckNow}
              disabled={isChecking}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-xl transition-colors duration-200 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isChecking ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Checking...
                </>
              ) : (
                "I've Verified My Email"
              )}
            </button>

            <button
              onClick={handleResendVerification}
              disabled={isResending || resendCooldown > 0}
              className="w-full py-3 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isResending ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                  Sending...
                </div>
              ) : resendCooldown > 0 ? (
                `Resend in ${resendCooldown}s`
              ) : (
                "Resend Verification Email"
              )}
            </button>
          </div>

          {/* Footer */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Wrong email address?
            </p>
            <button
              onClick={handleLogout}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline"
            >
              Sign out and try again
            </button>
          </div>
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Didn't receive the email? Check your spam folder or contact support if the issue persists.
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification;