# 🔑 Configuration Guide - Where to Get Each Value

---

## 1️⃣ **SECRET_KEY** - Generate New Secure Key

### What is it?
- Flask session encryption key
- Protects user login cookies
- Must be random and strong (32+ characters)

### How to Generate:

**Option A: Python (Recommended)**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Output example:
```
7a9f3c2b1e8d4a6f9c3e1b7d4a2f8c5e9b6d3a1f7c4e2b8d5a9f3c1e7b4a6d
```

**Option B: OpenSSL**
```bash
openssl rand -hex 32
```

**Option C: Online Generator** (NOT RECOMMENDED - less secure)
- Use only if absolutely necessary
- https://randomkeygen.com/ → copy "SHA1" value

### Set in Your Platform:
```
Environment Variable: SECRET_KEY
Value: <paste-your-generated-key>
```

---

## 2️⃣ **INGEST_API_KEY** - For Raspberry Pi Authentication

### What is it?
- Token that Raspberry Pi uses to send data
- Protects your API endpoints from unauthorized access
- Only Raspberry Pi with correct token can upload data

### How to Generate:

**Option A: Python (Recommended)**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Output example:
```
kJ7mNp_9qR2wL8xZ3vB6cD1eF4gH5iK0lM9nO2pQ7rS8tU1vW3xY4zA5bC6dE7fG
```

**Option B: OpenSSL**
```bash
openssl rand -base64 32
```

### Set in Your Platform:
```
Environment Variable: INGEST_API_KEY
Value: <paste-your-generated-key>
```

### Use with Raspberry Pi:
The Pi will send this header in every API request:
```bash
curl -X POST https://your-domain.com/api/ingest/water \
  -H "X-INGEST-TOKEN: kJ7mNp_9qR2wL8xZ3vB6cD1eF4gH5iK0lM9nO2pQ7rS8tU1vW3xY4zA5bC6dE7fG" \
  -H "Content-Type: application/json" \
  -d '{"tds": 150, "turbidity": 5.2, "temperature": 28.5}'
```

---

## 3️⃣ **FIREBASE_DATABASE_URL** - From Firebase Console

### What is it?
- URL for your real-time database
- Optional - app works without it
- Only needed if you want persistent data

### How to Get:

**Step 1: Go to Firebase Console**
```
https://console.firebase.google.com/
```

**Step 2: Select Your Project**
- If no project exists, create one:
  - Project Name: `autonomous-boat` (or your name)
  - Region: `asia-southeast1` (or your region)

**Step 3: Navigate to Realtime Database**
- Left menu → Build → Realtime Database
- Click "Create Database"
- Start in **test mode** (for development)
- Choose region (e.g., `asia-southeast1`)

**Step 4: Copy Database URL**
- Database URL shown at top
- Example: `https://autonomous-boat-906cf-default-rtdb.asia-southeast1.firebasedatabase.app/`

### Set in Your Platform:
```
Environment Variable: FIREBASE_DATABASE_URL
Value: https://your-project-default-rtdb.region.firebasedatabase.app/
```

### If You Don't Have Firebase Yet:
- Leave it empty: `""` (app still works)
- Can add later anytime

---

## 4️⃣ **FIREBASE_CREDENTIALS_PATH** - Service Account Key

### What is it?
- JSON file with Firebase authentication credentials
- Allows app to write to your Firebase database
- Must be kept secret (never commit to git)

### How to Get:

**Step 1: Go to Firebase Console**
```
https://console.firebase.google.com/
```

**Step 2: Project Settings**
- Top left: Click ⚙️ Settings → Project Settings

**Step 3: Service Accounts Tab**
- Click "Service Accounts" tab
- Click "Generate New Private Key"
- File downloads: `autonomous-boat-906cf-firebase-adminsdk-*.json`

**Step 4: Secure the File**
```bash
# Never commit this file
# Add to .gitignore (already done)
cat .gitignore | grep credentials
```

**Step 5: Upload to Server**

**For Railway/Heroku:**
- Store the entire JSON as Base64 in environment variable
```bash
cat your-service-account.json | base64 > credentials.b64
# Copy the output → paste as environment variable FIREBASE_CREDENTIALS_BASE64
```

**For DigitalOcean Droplet:**
```bash
# Upload file to /home/flooting_boat/credentials.json
scp your-service-account.json root@your-droplet-ip:/home/flooting_boat/
chmod 600 /home/flooting_boat/credentials.json
```

### Set in Your Platform:

**Option A: Direct Path (DigitalOcean)**
```
Environment Variable: FIREBASE_CREDENTIALS_PATH
Value: /home/flooting_boat/credentials.json
```

**Option B: Base64 Encoded (Railway/Heroku)**
```bash
# Create base64 version
python -c "
import base64
import json
with open('your-service-account.json') as f:
    data = f.read()
print(base64.b64encode(data.encode()).decode())
"
```
```
Environment Variable: FIREBASE_CREDENTIALS_B64
Value: <base64-encoded-json>
```

### If You Don't Have Firebase:
- Leave empty: `""` (app still works)
- Database writes will be skipped

---

## 5️⃣ **FIREBASE_STORAGE_BUCKET** - For Image Storage (Optional)

### What is it?
- Google Cloud Storage bucket
- Stores camera frame images
- Optional - app works without it

### How to Get:

**Step 1: In Firebase Console**
- Left menu → Build → Storage
- Click "Get Started"
- Choose region (same as database)

**Step 2: Copy Bucket Name**
- Format: `your-project.appspot.com`
- Example: `autonomous-boat-906cf.appspot.com`

### Set in Your Platform:
```
Environment Variable: FIREBASE_STORAGE_BUCKET
Value: your-project.appspot.com
```

---

## 📋 **Complete Configuration Template**

Copy this and fill in your values:

```bash
# ✅ REQUIRED
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=7a9f3c2b1e8d4a6f9c3e1b7d4a2f8c5e9b6d3a1f7c4e2b8d5a9f3c1e7b4a6d
INGEST_API_KEY=kJ7mNp_9qR2wL8xZ3vB6cD1eF4gH5iK0lM9nO2pQ7rS8tU1vW3xY4zA5bC6dE7fG
APP_NAME=Smart AI Lake Monitoring

# ⚠️ OPTIONAL (Firebase)
FIREBASE_DATABASE_URL=https://autonomous-boat-906cf-default-rtdb.asia-southeast1.firebasedatabase.app/
FIREBASE_STORAGE_BUCKET=autonomous-boat-906cf.appspot.com
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
# OR use: GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# 🔧 PLATFORM-SPECIFIC
PORT=5000
```

---

## 🔒 **Security Best Practices**

### DO ✅
- Generate new keys for production
- Use different keys for dev/prod
- Store credentials in environment variables only
- Rotate keys quarterly
- Use `.gitignore` to prevent commits

### DON'T ❌
- Commit credentials to git
- Reuse test credentials in production
- Share credentials in emails/chat
- Use weak/predictable keys
- Store credentials in code

---

## 🚀 **Example: Setting Up Railway**

1. **Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output
```

2. **Generate INGEST_API_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output
```

3. **In Railway Dashboard:**
   - Variables → Add New Variable
   - Name: `SECRET_KEY` → Paste generated key
   - Name: `INGEST_API_KEY` → Paste generated key
   - Name: `FLASK_ENV` → Value: `production`
   - Name: `FLASK_DEBUG` → Value: `false`

4. **Deploy:**
   - Push to GitHub: `git push origin main`
   - Railway auto-deploys
   - Done! ✅

---

## 🆘 **Troubleshooting**

### Error: "CRITICAL: SECRET_KEY environment variable must be set"
**Fix:** Set `SECRET_KEY` in your hosting platform's environment variables

### Error: "CRITICAL: INGEST_API_KEY environment variable must be set"
**Fix:** Set `INGEST_API_KEY` in your hosting platform's environment variables

### Error: "Firebase credentials not found"
**Solution:** 
- If Firebase not needed → leave `FIREBASE_CREDENTIALS_PATH` empty
- If Firebase needed → upload credentials file and set path correctly

### Raspberry Pi can't upload data
**Check:**
1. Is `INGEST_API_KEY` the same on Pi and server?
2. Is Pi sending header: `X-INGEST-TOKEN: your-key`?
3. Is your domain HTTPS?

---

## 📞 **Quick Reference**

| Variable | Required | Where to Get | Example |
|----------|----------|--------------|---------|
| `SECRET_KEY` | ✅ YES | Generate: `secrets.token_hex(32)` | `7a9f3c...` |
| `INGEST_API_KEY` | ✅ YES | Generate: `secrets.token_urlsafe(32)` | `kJ7mNp...` |
| `FIREBASE_DATABASE_URL` | ⚠️ Optional | Firebase Console | `https://your-db.firebasedatabase.app/` |
| `FIREBASE_CREDENTIALS_PATH` | ⚠️ Optional | Firebase Service Account | `/path/to/creds.json` |
| `FIREBASE_STORAGE_BUCKET` | ⚠️ Optional | Firebase Storage | `project.appspot.com` |
| `FLASK_ENV` | ✅ YES | Set to `production` | `production` |
| `FLASK_DEBUG` | ✅ YES | Set to `false` | `false` |
| `APP_NAME` | ⚠️ Optional | Your choice | `Smart AI Lake Monitoring` |
| `PORT` | ⚠️ Optional | Usually auto | `5000` |

---

## 🎯 **Next Steps**

1. **Generate SECRET_KEY and INGEST_API_KEY** (use Python commands above)
2. **Choose your hosting platform** (Railway, Heroku, DigitalOcean, etc.)
3. **Set environment variables** on platform dashboard
4. **Deploy your code**
5. **Test the endpoints**

See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific instructions.
