# Railway Environment Variables Setup Guide

## Current Error

If you're seeing this error:
```
ValidationError: 3 validation errors for Settings
supabase_url - Field required
supabase_key - Field required  
supabase_service_key - Field required
```

**This means the environment variables are not set in Railway!**

## Step-by-Step: Adding Environment Variables to Railway

1. **Go to Railway Dashboard**
   - Open https://railway.app
   - Select your backend service

2. **Open Variables Tab**
   - Click on the **Variables** tab (or go to Settings → Variables)

3. **Add Each Variable**
   Click **+ New Variable** for each of these:

   | Variable Name | Value | Where to Find |
   |--------------|-------|---------------|
   | `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API → Project URL |
   | `SUPABASE_KEY` | Your Supabase anon key | Supabase Dashboard → Settings → API → anon public |
   | `SUPABASE_SERVICE_KEY` | Your Supabase service_role key | Supabase Dashboard → Settings → API → service_role secret |
   | `CORS_ORIGINS` | Comma-separated origins | e.g., `https://your-frontend.railway.app,http://localhost:3000` |

4. **Save and Deploy**
   - After adding all variables, Railway will automatically redeploy
   - Check the Deployments tab to see the new deployment

## Detailed Instructions for Supabase Keys

### Step 1: Go to Supabase Dashboard
1. Visit https://supabase.com
2. Log in to your account
3. Select your project (or create one if you haven't)

### Step 2: Find Your API Keys
1. In your Supabase project, click on **Settings** (gear icon in the left sidebar)
2. Click on **API** under Project Settings
3. You'll see:
   - **Project URL**: This is your `SUPABASE_URL`
     - Example: `https://abcdefghijklmnop.supabase.co`
   - **anon public**: This is your `SUPABASE_KEY`
     - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role secret**: This is your `SUPABASE_SERVICE_KEY`
     - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
     - ⚠️ **WARNING**: Never expose this key in frontend code! It's only for backend use.

### Step 3: Copy Values to Railway
1. For each key, copy the full value (they're long strings)
2. Paste into Railway's Variables tab
3. Make sure the variable names match exactly (case-sensitive):
   - `SUPABASE_URL` (not `supabase_url` or `SUPABASE_URL`)
   - `SUPABASE_KEY` (not `supabase_key`)
   - `SUPABASE_SERVICE_KEY` (not `supabase_service_key`)

## Example .env File (for local reference)

For your local development, you should have a `.env` file in `backend/` with:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Note**: Do NOT commit `.env` files to git! They should be in `.gitignore`.

## Verification

After adding the variables:
1. Check Railway → Deployments tab
2. Wait for the deployment to complete
3. Check the logs - you should no longer see validation errors
4. The application should start successfully

## Troubleshooting

**Still seeing validation errors?**
- Double-check variable names (case-sensitive!)
- Make sure there are no extra spaces in variable names or values
- Verify the values are copied completely (keys are very long)
- Try redeploying: Settings → Deployments → Redeploy

**Application starts but can't connect to Supabase?**
- Verify the `SUPABASE_URL` is correct
- Check that the keys match your Supabase project
- Make sure you're using the `service_role` key for `SUPABASE_SERVICE_KEY` (not the anon key)


