# 🔐 Firebase Credentials Setup Guide

The `firebase-credentials.json` file contains sensitive data and should **NEVER** be committed to GitHub. Here's how to handle it in different environments:

---

## 🏠 Local Development

Simply keep the file in `backend/firebase-credentials.json` (already in .gitignore)

The code will automatically detect it.

---

## 🚀 Deployment Options

### Option A: Render Secret Files (Recommended ⭐)

**Best for**: Render, Railway, or similar platforms with file upload support

1. Go to your Render service dashboard
2. Click **"Environment"** tab
3. Scroll to **"Secret Files"** section
4. Click **"Add Secret File"**
5. Set:
   - **Filename**: `firebase-credentials.json`
   - **Contents**: Paste your entire Firebase JSON (copy from local file)
6. Click **"Save"**

✅ Render will create this file at runtime in the same directory

---

### Option B: Environment Variable (Alternative)

**Best for**: Vercel, Netlify, Heroku, or platforms without file upload

#### Step 1: Convert JSON to Single Line

**On Windows (PowerShell):**
```powershell
cd C:\Users\JAYAN\Downloads\orbit\backend
(Get-Content firebase-credentials.json -Raw) -replace '\r?\n', '' | Set-Clipboard
```

**On Mac/Linux:**
```bash
cat firebase-credentials.json | tr -d '\n' | pbcopy
```

This copies the minified JSON to your clipboard.

#### Step 2: Add as Environment Variable

In your deployment platform (Render/Vercel/etc.), add:

**Variable Name**: `FIREBASE_CREDENTIALS_JSON`

**Value**: Paste the single-line JSON from clipboard

Example:
```
{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

⚠️ **Important**: The value must be valid JSON on a single line!

---

## 🔍 How It Works

The code tries multiple methods in this order:

1. ✅ **Environment Variable**: `FIREBASE_CREDENTIALS_JSON` (best for deployment)
2. ✅ **Custom File Path**: `FIREBASE_CONFIG_PATH` environment variable
3. ✅ **Default File**: `./firebase-credentials.json` (for local dev)

---

## ✅ Verification

After deployment, check your logs for:

```
✓ Initializing Firebase with config file: ./firebase-credentials.json
```

or

```
✓ Initializing Firebase from FIREBASE_CREDENTIALS_JSON environment variable
```

If you see errors, verify:
- The JSON is valid (no missing commas, quotes, etc.)
- Private key includes `\n` characters (newlines)
- No extra spaces or line breaks in environment variable

---

## 🎯 Recommended Approach

| Platform | Best Method |
|----------|-------------|
| **Render** | Secret Files (Option A) |
| **Railway** | Secret Files or Environment Variable |
| **Vercel** | Environment Variable (Option B) |
| **Heroku** | Environment Variable (Option B) |
| **Google Cloud Run** | Service Account attached to instance |
| **AWS/Azure** | Environment Variable or secrets manager |

---

## 🛠️ Troubleshooting

### Error: "Firebase credentials not configured"

**Solution**: Add the credentials using one of the methods above

### Error: "Failed to parse FIREBASE_CREDENTIALS_JSON"

**Solution**: 
1. Verify JSON is valid: https://jsonlint.com/
2. Ensure it's on a single line
3. Check for escaped quotes (should be `\"` in strings)

### Error: "Invalid private key"

**Solution**: 
- Ensure private key includes `\n` for line breaks
- Example: `"private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQI...\n-----END PRIVATE KEY-----\n"`

### Works locally but not in production

**Solution**: 
- Check deployment logs for Firebase initialization message
- Verify environment variable name is exactly `FIREBASE_CREDENTIALS_JSON`
- Ensure value doesn't have extra quotes or formatting

---

## 📋 Quick Reference

### Local Development
```bash
# File location
backend/firebase-credentials.json
```

### Render Deployment
```
Environment → Secret Files → Add Secret File
Filename: firebase-credentials.json
Contents: [paste JSON]
```

### Other Platforms
```
Environment Variables:
FIREBASE_CREDENTIALS_JSON=[single-line JSON]
```

---

## 🔒 Security Best Practices

✅ **DO**:
- Keep `firebase-credentials.json` in .gitignore
- Use environment variables or secret files in production
- Rotate credentials if exposed
- Use different Firebase projects for dev/staging/production

❌ **DON'T**:
- Commit credentials to GitHub
- Share credentials in chat/email
- Use production credentials in development
- Hard-code credentials in your code

---

## 🆘 Need Help?

If you're still having issues:
1. Check your deployment platform logs
2. Verify Firebase project is active
3. Ensure service account has Firestore permissions
4. Try the Secret Files method first (easier to debug)
