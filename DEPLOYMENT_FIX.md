# Railway Deployment Fix Guide

## The Problem
"Error creating build plan with Railpack" occurs because Railway is trying to build from the repository root, but your backend code is in the `backend/` subdirectory.

## The Solution: Set Root Directory in Railway

**CRITICAL STEP - This must be done in Railway Dashboard:**

1. Go to your Railway project: https://railway.app
2. Select your service (the one showing the error)
3. Click on **Settings** tab (gear icon)
4. Scroll down to **Source** section
5. Find **Root Directory** field
6. Change it from `./` to `backend`
7. Click **Save** or **Update**

Railway will automatically trigger a new deployment after you save.

## Alternative: If Root Directory Setting is Not Available

If you don't see a Root Directory option in Settings, you can:

1. Delete the current service in Railway
2. Create a new service
3. Connect to the same GitHub repository
4. When creating, look for **Root Directory** option and set it to `backend`
5. Or use Railway CLI: `railway service --root backend`

## Verification

After setting the root directory, Railway should:
- Detect Python automatically (from requirements.txt)
- Use the Procfile for the start command
- Successfully build and deploy

## Files Already Configured

These files are already in place in the `backend/` directory:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ `nixpacks.toml` - Build configuration (optional, Railway will auto-detect Python)

## Environment Variables

Don't forget to set these in Railway → Variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`
- `CORS_ORIGINS` (e.g., `https://your-frontend.railway.app`)

## Still Having Issues?

If you see "No start command was found":

1. **Verify Root Directory is Set**: Make sure Root Directory is set to `backend` in Railway Settings → Source
2. **Check that Procfile exists**: Should be at `backend/Procfile` with content: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Verify files are committed**: Make sure `backend/Procfile`, `backend/nixpacks.toml`, and `backend/railway.json` are committed to git
4. **Check Railway Variables**: In Railway dashboard, go to Variables tab and make sure `PORT` is not manually set (Railway sets this automatically)
5. **Force Redeploy**: After making changes, push to git or manually trigger a redeploy in Railway

## File Checklist

Make sure these files exist in `backend/` directory:
- ✅ `requirements.txt`
- ✅ `Procfile` (with start command)
- ✅ `nixpacks.toml` (with [start] cmd)
- ✅ `railway.json` (with startCommand)
- ✅ `app/main.py` (FastAPI app)

All of these specify the same start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

