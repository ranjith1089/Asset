# How to Get Supabase Keys

## Step 1: Access Supabase Dashboard

1. Go to https://supabase.com
2. Log in to your account
3. Select your project (or create one if you don't have one)

## Step 2: Navigate to API Settings

1. In your Supabase project dashboard, look at the left sidebar
2. Click on **Settings** (gear icon ⚙️)
3. Click on **API** (under Project Settings)

## Step 3: Find Your Keys

You'll see a page with three important sections:

### 📍 Project URL
- **Use this for**: `SUPABASE_URL`
- **Location**: Top of the page, labeled "Project URL"
- **Example**: `https://abcdefghijklmnop.supabase.co`
- **Copy the entire URL**

### 🔓 anon public key
- **Use this for**: `SUPABASE_KEY`
- **Location**: In the "Project API keys" section
- **Label**: "anon public" (safe to use in client-side code)
- **Copy the entire key** (it's a long JWT token)

### 🔒 service_role secret key
- **Use this for**: `SUPABASE_SERVICE_KEY`
- **Location**: In the "Project API keys" section
- **Label**: "service_role" with a "secret" tag
- **⚠️ IMPORTANT**: This key has admin privileges - keep it secret!
- **Copy the entire key** (it's a long JWT token)

## Visual Guide

```
Supabase Dashboard → Settings → API

┌─────────────────────────────────────────┐
│ Project URL                             │
│ https://xxxxx.supabase.co  [Copy]       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Project API keys                        │
│                                         │
│ anon public                             │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...  │
│ [Copy]                                  │
│                                         │
│ service_role [secret]                   │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...  │
│ [Copy]                                  │
└─────────────────────────────────────────┘
```

## Step 4: Copy to Railway

1. Go to Railway → Your Service → Variables tab
2. Add each variable:

   | Variable Name | Value | Where to Get It |
   |--------------|-------|-----------------|
   | `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase → Settings → API → Project URL |
   | `SUPABASE_KEY` | `eyJhbGci...` (anon public key) | Supabase → Settings → API → anon public |
   | `SUPABASE_SERVICE_KEY` | `eyJhbGci...` (service_role key) | Supabase → Settings → API → service_role secret |

3. Make sure to:
   - ✅ Copy the **entire** key (they're long)
   - ✅ No extra spaces before/after
   - ✅ Exact variable names (case-sensitive)

## 🔒 Security Note

- **`SUPABASE_KEY`** (anon): Safe to use in frontend code
- **`SUPABASE_SERVICE_KEY`**: ⚠️ **NEVER** expose this in frontend! Only use in backend/server code.

---

# How to Set CORS_ORIGINS

## What is CORS_ORIGINS?

CORS (Cross-Origin Resource Sharing) origins are the URLs where your frontend application is hosted. Your backend needs to know which frontend URLs are allowed to make API requests.

## Format

`CORS_ORIGINS` should be a **comma-separated list** of URLs (no spaces around commas).

## Examples

### For Local Development Only
```
http://localhost:3000,http://localhost:5173
```

### For Production (Railway frontend)
```
https://your-frontend-app.railway.app
```

### For Both Local and Production
```
http://localhost:3000,http://localhost:5173,https://your-frontend-app.railway.app
```

### Multiple Production Environments
```
https://your-frontend-app.railway.app,https://your-custom-domain.com
```

## How to Find Your Frontend URL

### If using Railway for frontend:
1. Go to Railway dashboard
2. Select your **frontend** service (not backend)
3. Click on **Settings** → **Networking**
4. Look for your domain, e.g., `https://frontend-production.up.railway.app`
5. Or go to **Settings** → **Domain** to see your custom domain

### If using Vercel/Netlify:
- Check your deployment URL from their dashboard
- Format: `https://your-app.vercel.app` or `https://your-app.netlify.app`

### If using localhost:
- Use: `http://localhost:3000` (or whatever port your frontend uses)

## Setting in Railway

1. Go to Railway → Your **Backend** Service → Variables tab
2. Add variable:
   - **Name**: `CORS_ORIGINS`
   - **Value**: Your comma-separated URLs

## Example Configuration

If your frontend is deployed at `https://asset-management.up.railway.app` and you also want localhost access:

```
CORS_ORIGINS = http://localhost:3000,http://localhost:5173,https://asset-management.up.railway.app
```

## Important Notes

- ✅ **No spaces** around commas: `url1,url2,url3` ✅
- ❌ **With spaces**: `url1, url2, url3` ❌ (may cause issues)
- ✅ Include `http://` or `https://` protocol
- ✅ Include the full URL including domain and port (if using non-standard port)

## Quick Checklist

For Railway deployment, you need these 4 variables:

- [ ] `SUPABASE_URL` - From Supabase → Settings → API → Project URL
- [ ] `SUPABASE_KEY` - From Supabase → Settings → API → anon public
- [ ] `SUPABASE_SERVICE_KEY` - From Supabase → Settings → API → service_role secret
- [ ] `CORS_ORIGINS` - Your frontend URLs (comma-separated, no spaces)


