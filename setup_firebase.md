# Firebase Setup Guide

This guide will help you set up Firebase authentication for the MyDoc AI application.

## Frontend Configuration ✅

The frontend Firebase configuration has been set up with your project credentials:
- Project ID: `mydoc-e3824`
- Auth Domain: `mydoc-e3824.firebaseapp.com`

## Backend Configuration

To enable full authentication features on the backend, you need to set up a Firebase service account:

### Step 1: Generate Service Account Key

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `mydoc-e3824`
3. Go to Project Settings (gear icon) → Service Accounts
4. Click "Generate new private key"
5. Download the JSON file

### Step 2: Configure Backend

Option A - Environment Variable (Recommended):
```bash
# Copy the entire JSON content and set as environment variable
export FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"mydoc-e3824",...}'
```

Option B - Service Account File:
```bash
# Save the downloaded JSON file as firebase-service-account.json in the backend directory
cp ~/Downloads/mydoc-e3824-firebase-adminsdk-xxxxx.json backend/firebase-service-account.json
```

Option C - Project ID Only (Limited Features):
```bash
# For development/testing with limited auth features
export FIREBASE_PROJECT_ID=mydoc-e3824
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp backend/.env.example backend/.env

# Edit the .env file with your configuration
```

## Firebase Console Setup

Make sure your Firebase project has the following enabled:

### Authentication
1. Go to Authentication → Sign-in method
2. Enable Email/Password authentication
3. Enable Google authentication (optional)
4. Configure authorized domains if needed

### Firestore Database
1. Go to Firestore Database
2. Create database in production mode
3. Set up security rules for user data isolation

### Security Rules Example
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Conversations belong to users
    match /conversations/{conversationId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Testing the Setup

1. Start the backend server:
```bash
cd backend
python -m uvicorn main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Try creating an account and logging in

## Troubleshooting

### Common Issues:

1. **"Firebase Admin SDK not initialized"**
   - Make sure you have set up the service account or project ID
   - Check that environment variables are loaded correctly

2. **"Invalid authentication token"**
   - Verify that the frontend and backend are using the same Firebase project
   - Check that the service account has the correct permissions

3. **"Permission denied"**
   - Make sure Firestore security rules allow authenticated users to access their data
   - Verify that the user is properly authenticated

### Demo Mode

If you don't want to set up Firebase authentication right now, the application will run in demo mode with limited authentication features. You can still test all the medical AI functionality.

## Production Deployment

For production deployment:

1. Set up proper environment variables on your hosting platform
2. Configure Firebase security rules for production
3. Set up proper CORS origins
4. Enable Firebase Analytics (optional)
5. Set up proper logging and monitoring

The application is now configured to work with your Firebase project!