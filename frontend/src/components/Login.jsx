import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useAuthError, useAuthState } from "../hooks";
import { FaGoogle, FaEye, FaEyeSlash } from "react-icons/fa";
import { MdSignalWifiOff } from "react-icons/md";

export default function Login({ onSwitchToSignup }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [resetEmailSent, setResetEmailSent] = useState(false);

  const { login, loginWithGoogle, resetPassword } = useAuth();
  const { errorMessage, clearError, hasError } = useAuthError();
  const { isOnline } = useAuthState();

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    
    if (!email || !password) {
      return;
    }

    if (!isOnline) {
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      // User will be redirected automatically by AuthContext
    } catch (error) {
      console.error("Login error:", error);
      // Error is handled by useAuthError hook
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      await loginWithGoogle();
      // User will be redirected automatically by AuthContext
    } catch (error) {
      console.error("Google login error:", error);
      // Error is handled by AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!email) {
      return;
    }

    if (!isOnline) {
      return;
    }

    try {
      await resetPassword(email);
      setResetEmailSent(true);
      clearError();
    } catch (error) {
      console.error("Password reset error:", error);
      // Error is handled by useAuthError hook
    }
  };

  return (
    <div className="p-8 flex flex-col items-center justify-center min-h-full bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-gradient-to-br from-blue-600 to-gray-800 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold shadow-lg">
          🩺
        </div>
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome Back
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Sign in to continue your wellness journey</p>
        </div>
        {!isOnline && (
          <div className="flex items-center gap-1 text-orange-500 text-sm animate-pulse">
            <MdSignalWifiOff />
            <span>Offline</span>
          </div>
        )}
      </div>
      
      {hasError && (
        <div className="w-full max-w-sm mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-xl text-sm">
          {errorMessage}
        </div>
      )}

      {!isOnline && (
        <div className="w-full max-w-sm mb-4 p-3 bg-orange-100 dark:bg-orange-900 border border-orange-400 text-orange-700 dark:text-orange-300 rounded-xl text-sm">
          You are currently offline. Please check your internet connection to sign in.
        </div>
      )}

      {resetEmailSent && (
        <div className="w-full max-w-sm mb-4 p-3 bg-green-100 dark:bg-green-900 border border-green-400 text-green-700 dark:text-green-300 rounded-xl text-sm">
          Password reset email sent! Check your inbox.
        </div>
      )}

      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
        <div className="relative group">
          <input
            type="email"
            className="w-full px-4 py-4 rounded-xl border border-gray-300 dark:border-gray-600 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500
              peer"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
          <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
            </svg>
          </div>
        </div>
        
        <div className="relative group">
          <input
            type={showPassword ? "text" : "password"}
            className="w-full px-4 py-4 pr-12 rounded-xl border border-gray-300 dark:border-gray-600 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 
              dark:text-gray-400 dark:hover:text-gray-200 transition-colors duration-200 p-1 rounded-md
              hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => setShowPassword(!showPassword)}
            disabled={isLoading}
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </button>
        </div>

        <button
          type="submit"
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-gray-800 text-white font-semibold 
            hover:from-blue-700 hover:to-gray-900 transition-all duration-200 
            disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]
            shadow-lg hover:shadow-xl disabled:hover:scale-100 disabled:hover:shadow-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={isLoading || !isOnline}
        >
          {isLoading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Signing in...
            </div>
          ) : (
            "Sign In"
          )}
        </button>
      </form>

      <button
        onClick={handleForgotPassword}
        className="mt-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 underline disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={isLoading || !isOnline || !email}
      >
        Forgot Password?
      </button>

      <div className="w-full max-w-sm my-4 flex items-center">
        <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
        <span className="px-3 text-sm text-gray-500 dark:text-gray-400">or</span>
        <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
      </div>

      <button
        onClick={handleGoogleLogin}
        className="w-full max-w-sm py-4 px-4 rounded-xl border-2 border-gray-300 dark:border-gray-600 
          text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 
          transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed 
          flex items-center justify-center gap-3 transform hover:scale-[1.02] active:scale-[0.98]
          hover:border-gray-400 dark:hover:border-gray-500 hover:shadow-md
          disabled:hover:scale-100 disabled:hover:shadow-none
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        disabled={isLoading || !isOnline}
      >
        <FaGoogle className="text-red-500 text-lg" />
        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            Signing in...
          </div>
        ) : (
          "Continue with Google"
        )}
      </button>

      <p className="mt-4 text-sm">
        New here?{" "}
        <button 
          onClick={onSwitchToSignup} 
          className="text-gray-600 dark:text-gray-400 underline hover:text-gray-800 dark:hover:text-gray-200"
          disabled={isLoading}
        >
          Create an account
        </button>
      </p>
    </div>
  );
}
