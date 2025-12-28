import { createContext, useContext, useEffect, useState } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  updateProfile,
  sendEmailVerification,
  getIdToken
} from 'firebase/auth';
import { doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';
import { auth, googleProvider, db } from '../firebase';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Create user profile in Firestore
  const createUserProfile = async (user, additionalData = {}) => {
    if (!user) return;

    const userRef = doc(db, 'users', user.uid);
    const userSnap = await getDoc(userRef);

    if (!userSnap.exists()) {
      const { displayName, email, photoURL } = user;
      const createdAt = new Date();

      try {
        await setDoc(userRef, {
          displayName: displayName || additionalData.displayName || '',
          email,
          photoURL: photoURL || '',
          createdAt,
          lastLogin: createdAt,
          isActive: true,
          preferences: {
            theme: 'light',
            notifications: true,
            language: 'en',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
          },
          privacySettings: {
            shareDataForResearch: false,
            allowAnalytics: true,
            dataRetentionPeriod: '2years'
          },
          ...additionalData
        });
      } catch (error) {
        console.error('Error creating user profile:', error);
        throw error;
      }
    } else {
      // Update last login
      try {
        await updateDoc(userRef, {
          lastLogin: new Date()
        });
      } catch (error) {
        console.error('Error updating last login:', error);
      }
    }

    return userRef;
  };

  // Sign up with email and password
  const signup = async (email, password, displayName = '') => {
    try {
      setError(null);
      setLoading(true);

      const { user } = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update display name if provided
      if (displayName) {
        await updateProfile(user, { displayName });
      }

      // Send email verification
      await sendEmailVerification(user);

      // Create user profile in Firestore
      await createUserProfile(user, { displayName });

      return user;
    } catch (error) {
      console.error('Signup error:', error);
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Sign in with email and password
  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);

      const { user } = await signInWithEmailAndPassword(auth, email, password);
      
      // Update user profile with last login
      await createUserProfile(user);

      return user;
    } catch (error) {
      console.error('Login error:', error);
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Sign in with Google
  const loginWithGoogle = async () => {
    try {
      setError(null);
      setLoading(true);

      const { user } = await signInWithPopup(auth, googleProvider);
      
      // Create or update user profile
      await createUserProfile(user);

      return user;
    } catch (error) {
      console.error('Google login error:', error);
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const logout = async () => {
    try {
      setError(null);
      await signOut(auth);
      
      // Clear any cached data
      localStorage.removeItem('sukh_auth_state');
      
    } catch (error) {
      console.error('Logout error:', error);
      setError(error);
      throw error;
    }
  };

  // Reset password
  const resetPassword = async (email) => {
    try {
      setError(null);
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      console.error('Password reset error:', error);
      setError(error);
      throw error;
    }
  };

  // Update user profile
  const updateUserProfile = async (updates) => {
    if (!currentUser) throw new Error('No user logged in');

    try {
      setError(null);
      
      // Update Firebase Auth profile
      if (updates.displayName !== undefined || updates.photoURL !== undefined) {
        await updateProfile(currentUser, {
          ...(updates.displayName !== undefined && { displayName: updates.displayName }),
          ...(updates.photoURL !== undefined && { photoURL: updates.photoURL })
        });
      }

      // Update Firestore profile
      const userRef = doc(db, 'users', currentUser.uid);
      await updateDoc(userRef, {
        ...updates,
        updatedAt: new Date()
      });

    } catch (error) {
      console.error('Profile update error:', error);
      setError(error);
      throw error;
    }
  };

  // Get ID token for API authentication
  const getIdTokenForUser = async (forceRefresh = false) => {
    if (!currentUser) return null;
    
    try {
      return await getIdToken(currentUser, forceRefresh);
    } catch (error) {
      console.error('Error getting ID token:', error);
      throw error;
    }
  };

  // Get user profile from Firestore
  const getUserProfile = async () => {
    if (!currentUser) return null;

    try {
      const userRef = doc(db, 'users', currentUser.uid);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        return userSnap.data();
      }
      return null;
    } catch (error) {
      console.error('Error getting user profile:', error);
      throw error;
    }
  };

  // Monitor auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      try {
        setCurrentUser(user);
        
        if (user) {
          // Store basic auth state for persistence
          const authState = {
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
            emailVerified: user.emailVerified,
            timestamp: Date.now()
          };
          localStorage.setItem('sukh_auth_state', JSON.stringify(authState));
          
          // Update API service with new token
          try {
            const token = await getIdToken(user);
            const { default: apiService } = await import('../services/api');
            apiService.setToken(token);
            apiService.setTokenRefreshCallback(async (forceRefresh) => {
              return await getIdToken(user, forceRefresh);
            });
            
            // Dispatch token update event
            window.dispatchEvent(new CustomEvent('auth:token-updated', {
              detail: { token }
            }));
          } catch (tokenError) {
            console.error('Failed to set API token:', tokenError);
          }
        } else {
          localStorage.removeItem('sukh_auth_state');
          
          // Clear API service token
          try {
            const { default: apiService } = await import('../services/api');
            apiService.clearToken();
            
            // Dispatch logout event
            window.dispatchEvent(new CustomEvent('auth:logout'));
          } catch (apiError) {
            console.error('Failed to clear API token:', apiError);
          }
        }
      } catch (error) {
        console.error('Auth state change error:', error);
        setError(error);
      } finally {
        setLoading(false);
      }
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    loading,
    error,
    isOnline,
    signup,
    login,
    loginWithGoogle,
    logout,
    resetPassword,
    updateUserProfile,
    getUserProfile,
    getIdToken: getIdTokenForUser,
    setError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};