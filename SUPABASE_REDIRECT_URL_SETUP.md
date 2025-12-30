# Supabase Redirect URL Configuration

## Issue
Password reset links are pointing to `localhost:3000` instead of your Railway frontend URL.

## Solution: Update Supabase Redirect URLs

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **URL Configuration**
4. Update the following settings:

### Site URL
Set to your Railway frontend URL:
```
https://asset-production-364d.up.railway.app
```

### Redirect URLs
Add these URLs (one per line):
```
https://asset-production-364d.up.railway.app
https://asset-production-364d.up.railway.app/*
https://asset-production-364d.up.railway.app/reset-password
http://localhost:5173
http://localhost:5173/*
http://localhost:5173/reset-password
```

5. Click **Save**

## After Updating

1. Request a new password reset email (the old link won't work anymore)
2. The new reset link will use the correct Railway URL
3. Click the link in the email to reset your password

## Manual Reset Link (Quick Fix)

If you have the reset link, you can manually change the domain:

**Original:**
```
http://localhost:3000/#access_token=...
```

**Updated (replace with your Railway URL):**
```
https://asset-production-364d.up.railway.app/#access_token=...
```

Then copy the entire URL and paste it in your browser to reset your password.

