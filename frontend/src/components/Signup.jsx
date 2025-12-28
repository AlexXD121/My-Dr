import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { FaGoogle, FaEye, FaEyeSlash } from "react-icons/fa";

export default function Signup({ onSwitchToLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { signup, loginWithGoogle, error, setError } = useAuth();

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) errors.push("at least 8 characters");
    if (!/[A-Z]/.test(password)) errors.push("one uppercase letter");
    if (!/[a-z]/.test(password)) errors.push("one lowercase letter");
    if (!/\d/.test(password)) errors.push("one number");
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) errors.push("one special character");
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password || !confirmPassword) {
      setError("Please fill in all required fields");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      setError(`Password must contain ${passwordErrors.join(", ")}`);
      return;
    }

    setIsLoading(true);
    try {
      await signup(email, password, displayName);
      // User will be redirected automatically by AuthContext
    } catch (error) {
      console.error("Signup error:", error);
      // Error is handled by AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setIsLoading(true);
    try {
      await loginWithGoogle();
      // User will be redirected automatically by AuthContext
    } catch (error) {
      console.error("Google signup error:", error);
      // Error is handled by AuthContext
    } finally {
      setIsLoading(false);
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
            Join Sukh
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm">Start your mental wellness journey today</p>
        </div>
      </div>
      
      {error && (
        <div className="w-full max-w-sm mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-xl text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <div className="relative group">
          <input
            type="text"
            className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500"
            placeholder="Display Name (optional)"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="relative group">
          <input
            type="email"
            className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        
        <div className="relative group">
          <input
            type={showPassword ? "text" : "password"}
            className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 dark:border-gray-600 
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

        <div className="relative group">
          <input
            type={showConfirmPassword ? "text" : "password"}
            className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 dark:border-gray-600 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            disabled={isLoading}
          />
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 
              dark:text-gray-400 dark:hover:text-gray-200 transition-colors duration-200 p-1 rounded-md
              hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            disabled={isLoading}
          >
            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
          </button>
        </div>

        <div className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">Password Requirements:</span>
          </div>
          <ul className="text-xs space-y-1 ml-6">
            <li className={password.length >= 8 ? 'text-green-600 dark:text-green-400' : ''}>• At least 8 characters</li>
            <li className={/[A-Z]/.test(password) ? 'text-green-600 dark:text-green-400' : ''}>• One uppercase letter</li>
            <li className={/[a-z]/.test(password) ? 'text-green-600 dark:text-green-400' : ''}>• One lowercase letter</li>
            <li className={/\d/.test(password) ? 'text-green-600 dark:text-green-400' : ''}>• One number</li>
            <li className={/[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'text-green-600 dark:text-green-400' : ''}>• One special character</li>
          </ul>
        </div>

        <button
          type="submit"
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-gray-800 text-white font-semibold 
            hover:from-blue-700 hover:to-gray-900 transition-all duration-200 
            disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]
            shadow-lg hover:shadow-xl disabled:hover:scale-100 disabled:hover:shadow-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={isLoading}
        >
          {isLoading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Creating Account...
            </div>
          ) : (
            "Create Account"
          )}
        </button>
      </form>

      <div className="w-full max-w-sm my-4 flex items-center">
        <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
        <span className="px-3 text-sm text-gray-500 dark:text-gray-400">or</span>
        <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
      </div>

      <button
        onClick={handleGoogleSignup}
        className="w-full max-w-sm py-4 px-4 rounded-xl border-2 border-gray-300 dark:border-gray-600 
          text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 
          transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed 
          flex items-center justify-center gap-3 transform hover:scale-[1.02] active:scale-[0.98]
          hover:border-gray-400 dark:hover:border-gray-500 hover:shadow-md
          disabled:hover:scale-100 disabled:hover:shadow-none
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        disabled={isLoading}
      >
        <FaGoogle className="text-red-500 text-lg" />
        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            Creating Account...
          </div>
        ) : (
          "Continue with Google"
        )}
      </button>

      <p className="mt-4 text-sm">
        Already have an account?{" "}
        <button 
          onClick={onSwitchToLogin} 
          className="text-gray-600 dark:text-gray-400 underline hover:text-gray-800 dark:hover:text-gray-200"
          disabled={isLoading}
        >
          Login
        </button>
      </p>
    </div>
  );
}
