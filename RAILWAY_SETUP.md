# Railway Deployment Setup

This guide explains how to deploy the Asset Management System backend to Railway.

## Important: Set Root Directory in Railway

Since this is a monorepo, you need to configure Railway to use the `backend/` directory as the root:

1. Go to your Railway project dashboard
2. Select your service
3. Go to **Settings** → **Source**
4. Set **Root Directory** to: `backend`
5. Save the changes

## Environment Variables

Make sure to set these environment variables in Railway:

1. Go to your service in Railway dashboard
2. Click on **Variables** tab
3. Add the following variables:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
CORS_ORIGINS=https://your-frontend-url.railway.app,https://your-frontend-domain.com
PORT=8000
```

**Important Notes:**
- Railway automatically sets the `PORT` environment variable
- Update `CORS_ORIGINS` with your actual frontend URL after deploying
- Never commit `.env` files with real credentials

## Deployment Steps

1. **Connect GitHub Repository**
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository

2. **Configure Service**
   - After the service is created, go to Settings → Source
   - Set Root Directory to `backend`
   - Railway will auto-detect Python and use the configuration files

3. **Set Environment Variables**
   - Go to Variables tab
   - Add all required environment variables (listed above)

4. **Deploy**
   - Railway will automatically deploy when you push to main branch
   - Or click "Deploy" button in the dashboard

## Accessing Your API

After deployment:
- Railway will provide a URL like: `https://your-service.railway.app`
- Your API will be available at: `https://your-service.railway.app/api/assets`
- API docs will be at: `https://your-service.railway.app/docs`

## Troubleshooting

If you see "Error creating build plan with Railpack":
- Make sure Root Directory is set to `backend/`
- Check that `requirements.txt` exists in the backend directory
- Verify all environment variables are set correctly

## Separate Frontend Deployment

For the frontend, you can:
- Deploy it as a separate Railway service
- Or use Vercel, Netlify, or another static hosting service
- Update the `VITE_API_URL` in frontend `.env` to point to your Railway backend URL

