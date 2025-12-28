import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../LoadingSpinner';

const ProtectedRoute = ({ 
  children, 
  requireVerified = false, 
  fallback = null,
  loadingComponent = null 
}) => {
  const { currentUser, loading } = useAuth();

  // Show loading spinner while checking auth state
  if (loading) {
    return loadingComponent || (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Checking authentication...
          </p>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!currentUser) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Authentication Required
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Please sign in to access this feature.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  // Check email verification if required
  if (requireVerified && !currentUser.emailVerified) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Email Verification Required
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Please verify your email address to access this feature.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Check your inbox for a verification email.
          </p>
        </div>
      </div>
    );
  }

  // User is authenticated and verified (if required)
  return children;
};

export default ProtectedRoute;