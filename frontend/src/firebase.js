// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getAnalytics } from "firebase/analytics";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBRQAMbgix9DVCnFJpzUzBIGpoXcOJ_Eao",
  authDomain: "mydoc-e3824.firebaseapp.com",
  projectId: "mydoc-e3824",
  storageBucket: "mydoc-e3824.firebasestorage.app",
  messagingSenderId: "586222023543",
  appId: "1:586222023543:web:0843e114bef17564796772",
  measurementId: "G-KBHWK57R14"
};

// Firebase configuration is now hardcoded for this project
console.log('✅ Firebase configuration loaded successfully');

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

// Export Firestore instance
export const db = getFirestore(app);

// Initialize Analytics (optional)
let analytics = null;
try {
  analytics = getAnalytics(app);
  console.log('✅ Firebase Analytics initialized');
} catch (error) {
  console.log('⚠️ Firebase Analytics not available:', error.message);
}

export { analytics };

// Export the app instance
export default app;
