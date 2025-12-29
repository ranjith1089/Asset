# Fix: "secret Supabase: not found" Error

## The Problem

Railway is trying to use a "secret" called "Supabase" during the build process, but secrets are not available during build - they're only available at runtime. The environment variables should be set as **regular variables**, not secrets.

## Solution

### Step 1: Add Environment Variables as REGULAR Variables (Not Secrets)

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Click **+ New Variable**
3. Add these as **regular variables** (NOT secrets):
   - `SUPABASE_URL` = Your Supabase project URL
   - `SUPABASE_KEY` = Your Supabase anon key
   - `SUPABASE_SERVICE_KEY` = Your Supabase service_role key
   - `CORS_ORIGINS` = Your allowed origins (comma-separated)

**Important**: When adding variables, make sure you're adding them as regular variables, not secrets. Secrets have a lock icon and are only available at runtime.

### Step 2: Verify Build Configuration

I've simplified the `nixpacks.toml` and `railway.json` files to avoid any secret references. The configuration now:
- Lets Railway auto-detect Python version
- Uses Procfile for the start command
- Doesn't reference any secrets during build

### Step 3: Redeploy

After adding the environment variables:
1. Commit and push the updated configuration files:
   ```bash
   git add backend/nixpacks.toml backend/railway.json
   git commit -m "Fix Railway build - remove secret references"
   git push
   ```
2. Railway will automatically redeploy
3. The build should now succeed

## Why This Error Happens

Railway has two types of environment variables:
- **Variables**: Available at both build and runtime
- **Secrets**: Only available at runtime (for security)

The error occurs when Railway tries to access a secret during the build phase. By using regular variables instead, they'll be available during both build and runtime.

## Verification

After fixing:
1. Check Railway → Deployments tab
2. The build should complete successfully
3. The application should start
4. Check logs to confirm no more "secret not found" errors

## If Issues Persist

If you still see errors:
1. **Delete and recreate the service** (sometimes Railway caches old configs):
   - Settings → Danger Zone → Delete Service
   - Create a new service
   - Connect to the same GitHub repo
   - Set Root Directory to `backend`
   - Add environment variables before first deploy

2. **Check variable names**: Make sure they're exactly:
   - `SUPABASE_URL` (not `supabase_url` or `SUPABASE_URL`)
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `CORS_ORIGINS`


