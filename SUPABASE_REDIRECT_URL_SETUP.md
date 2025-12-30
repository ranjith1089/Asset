# Supabase Redirect URL Configuration

## Issue
Password reset links are pointing to `localhost:3000` instead of your Railway frontend URL, or links are expiring.

## Solution: Update Supabase Redirect URLs

### Step 1: Configure Supabase URLs

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **URL Configuration**
4. Update the following settings:

#### Site URL
Set to your Railway frontend URL:
```
https://asset-production-364d.up.railway.app
```

#### Redirect URLs
Add these URLs (one per line - make sure each is on a separate line):
```
https://asset-production-364d.up.railway.app
https://asset-production-364d.up.railway.app/*
https://asset-production-364d.up.railway.app/reset-password
http://localhost:5173
http://localhost:5173/*
http://localhost:5173/reset-password
```

5. Click **Save** at the bottom

### Step 2: Request New Password Reset

1. Go to your login page: https://asset-production-364d.up.railway.app/login
2. Click "Forgot your password?"
3. Enter your email: `ranjithkumar@aveoninfotech.com`
4. Click "Send Reset Email"
5. Check your email for the new reset link (should now point to Railway URL)
6. Click the link in the email (it will redirect to `/reset-password`)
7. Enter your new password

## Important Notes

- **Password reset links expire after 1 hour** - if your link expired, you need to request a new one
- **Old links won't work** - after updating Supabase settings, you must request a new reset email
- **Email delivery** - check your spam folder if you don't see the email

## Alternative: Reset Password via Supabase Dashboard

If email links are not working, you can reset the password directly:

1. Go to Supabase Dashboard → **Authentication** → **Users**
2. Find user: `ranjithkumar@aveoninfotech.com`
3. Click on the user
4. Click **"Reset Password"** button or manually set a new password
5. Save the changes
6. You can now login with the new password

