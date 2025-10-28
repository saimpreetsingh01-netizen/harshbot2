# Vercel Deployment Guide - Single Project Setup

## Overview
This guide will help you deploy your Telegram Mini App bot to Vercel using **ONE project** (not two separate projects).

## Step 1: Delete Your Current Projects (Optional)
If you already have two separate Vercel projects, you can delete them and start fresh, or just use one of them.

## Step 2: Prepare Your Repository
Make sure your code is pushed to GitHub, GitLab, or Bitbucket.

## Step 3: Create ONE Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your repository
4. **DO NOT select any preset/framework** - leave it as "Other"
5. Keep the default settings (Vercel will use the `vercel.json` configuration)

## Step 4: Set Environment Variables

In your Vercel project settings, add these environment variables:

### Required Variables:
```
MONGO_URI=your_mongodb_connection_string
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
BOT_TOKEN=your_telegram_bot_token
WEBHOOK_URL=https://your-project.vercel.app
```

### Optional Variables (if you use these features):
```
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
ADMIN_USER_IDS=123456789,987654321
SHORTIO_DOMAIN=your_shortio_domain
SHORTIO_API_KEY=your_shortio_key
GPLINKS_API_KEY=your_gplinks_key
```

**Important Notes:**
- Replace `your-project.vercel.app` with your actual Vercel deployment URL
- You'll get the actual URL after the first deployment, then update the `WEBHOOK_URL` variable
- DO NOT set `VITE_API_URL` - it will automatically use the same domain

## Step 5: Deploy

1. Click **"Deploy"**
2. Wait for the deployment to complete
3. Copy your deployment URL (e.g., `https://your-project-abc123.vercel.app`)

## Step 6: Update Environment Variables

1. Go to your project **Settings** → **Environment Variables**
2. Update `WEBHOOK_URL` to your actual deployment URL: `https://your-project-abc123.vercel.app`
3. **Redeploy** the project for changes to take effect

## Step 7: Set Telegram Webhook

After deployment, you need to register your webhook with Telegram:

### Method 1: Using Browser
Visit this URL in your browser (replace with your values):
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-project.vercel.app/api/webhook
```

### Method 2: Using curl
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.vercel.app/api/webhook"}'
```

### Verify Webhook
Check if webhook is set correctly:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

## Step 8: Test Your Bot

1. Open Telegram and find your bot
2. Send `/start` command - you should get a welcome message
3. Try the `/webapp` command to open the mini app
4. The mini app should now show movies, software, games, etc.

## Troubleshooting

### Bot doesn't respond to /start
- Check that `WEBHOOK_URL` is set correctly in environment variables
- Verify webhook is registered: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Check Vercel function logs for errors

### Mini app shows no data
- Verify `MONGO_URI` is set correctly
- Check that you have data in your MongoDB collections
- Open browser console (F12) and check for API errors
- Verify the API endpoints work: `https://your-project.vercel.app/api/movies`

### Environment variables not working
- Make sure you redeployed after adding/changing variables
- Variables should be set for "Production" environment
- Check spelling and case sensitivity

## Project Structure on Vercel

After deployment, your project will serve:
- `/` - React frontend (mini app)
- `/api/webhook` - Telegram bot webhook
- `/api/*` - Backend API endpoints (movies, games, software, etc.)

## Updating Your App

Whenever you push changes to your repository:
1. Vercel will automatically deploy
2. The webapp will be rebuilt
3. The API will be updated

## Important Notes

1. **Use ONE project** - Don't split into separate projects
2. **No preset needed** - The `vercel.json` handles everything
3. **Same domain** - Frontend and API use the same URL
4. **Build time** - First deployment may take a few minutes to build the React app
5. **Environment variables** - Always redeploy after changing them

## Common Mistakes to Avoid

❌ Creating two separate Vercel projects  
✅ Use one project with `vercel.json` configuration

❌ Setting a webapp/Vite preset  
✅ Leave as "Other" - let `vercel.json` handle it

❌ Different domains for frontend and API  
✅ Same domain - API at `/api/*`, frontend at `/`

❌ Setting `VITE_API_URL` to a different URL  
✅ Don't set it - will auto-detect the same domain

## Need Help?

If you encounter issues:
1. Check Vercel function logs
2. Check browser console (F12) for frontend errors
3. Verify all environment variables are set
4. Test API endpoints directly in browser
