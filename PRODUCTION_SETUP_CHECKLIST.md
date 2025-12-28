# 🚨 CRITICAL: Production Environment Setup Checklist

## ✅ COMPLETED
- [x] JWT_SECRET - Generated secure 64-character key
- [x] POSTGRES_PASSWORD - Generated secure database password
- [x] FIREBASE_PRIVATE_KEY - Extracted from mydoc-e3824 service account
- [x] FIREBASE_PROJECT_ID - Set to mydoc-e3824
- [x] Removed unnecessary API keys (Perplexity, Hugging Face) - using only Jan AI
- [x] Sentry DSN - Made optional (can add later)

## 🔴 REQUIRES IMMEDIATE ACTION

### 1. Firebase Service Account Setup
**Current:** `FIREBASE_PRIVATE_KEY=production_firebase_key_change_me`

**Steps to Fix:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `mydoc-e3824` (or create new production project)
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
6. Copy the `private_key` value from the JSON
7. Replace `production_firebase_key_change_me` in `.env.production`

**Format:** The private key should look like:
```
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
```

### 2. Jan AI Configuration
**Current:** `JAN_AI_URL=http://localhost:1337`

**Steps to Verify:**
1. Ensure Jan AI is running on production server
2. Update URL if Jan AI will run on different host/port in production
3. Test connection to Jan AI endpoint

**Note:** Removed Perplexity and Hugging Face API keys - using only Jan AI for AI services

### 3. Monitoring Setup
**Current:** `SENTRY_DSN=https://production_sentry_dsn_change_me`

**Steps to Fix:**
1. Go to [Sentry.io](https://sentry.io/)
2. Create new project for "My Dr AI"
3. Copy the DSN URL
4. Replace placeholder in `.env.production`

**Format:** Should look like:
```
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/123456
```

## 🟡 NEXT STEPS AFTER FIXING ABOVE

### 4. Domain and SSL Setup
- Purchase production domain (currently using mydoc.app)
- Configure DNS records
- Setup SSL certificates (Let's Encrypt recommended)

### 5. Database Setup
- Setup PostgreSQL production database
- Run migrations
- Test connection

## 🔧 Quick Test Commands

After updating the environment variables, test the configuration:

```bash
# Test backend startup
cd backend
python -c "from config import Config; print('Config loaded successfully')"

# Test database connection (after DB setup)
python -c "from database import get_db; print('Database connection OK')"

# Test Firebase connection
python -c "import firebase_admin; print('Firebase config OK')"
```

## ⚠️ SECURITY REMINDERS

1. **Never commit real API keys to git**
2. **Use different keys for staging vs production**
3. **Rotate keys regularly (every 90 days)**
4. **Monitor API key usage for anomalies**
5. **Keep backup of configuration in secure location**

---

**Status:** 🔴 CRITICAL - Cannot deploy to production until all placeholders are replaced
**Next Review:** After completing all manual steps above