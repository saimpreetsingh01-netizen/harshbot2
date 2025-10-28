# 🚀 Vercel Deployment Guide

This guide will help you deploy your Telegram bot to Vercel's free tier!

## ✨ Features on Vercel Free Tier

- ✅ **Serverless Functions** - No server management needed
- ✅ **Automatic Scaling** - Handles traffic spikes automatically
- ✅ **100GB Bandwidth** - More than enough for most bots
- ✅ **Fast Global CDN** - Low latency worldwide
- ✅ **HTTPS by Default** - Secure connections
- ✅ **Zero Configuration** - Just deploy and go!

---

## 📋 Prerequisites

Before deploying, make sure you have:

1. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/BotFather)
2. **MongoDB Atlas Account** - [Create free account](https://www.mongodb.com/cloud/atlas/register)
3. **Vercel Account** - [Sign up free](https://vercel.com/signup)
4. **GitHub Account** - To connect your repository

---

## 🔧 Step 1: Setup MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a **FREE** cluster (M0 Sandbox)
3. Create a database user with username and password
4. Whitelist all IP addresses (0.0.0.0/0) for Vercel
5. Get your connection string (looks like: `mongodb+srv://...`)

---

## 🤖 Step 2: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. **Save the bot token** - You'll need it later!
5. Send `/setcommands` to BotFather and paste these commands:

```
start - Start the bot and select language
help - Show all available commands
search - Search for software/games
aisearch - AI-powered search
browsegame - Browse games by category
browsesoft - Browse software by category
popular - Show popular downloads
new - Show latest releases
claimnft - Claim free NFTs
gamescripts - Browse game scripts
movies - Browse movies by category
searchmovie - Search all movies
favorites - View your favorites
mydownloads - View download history
profile - View your profile
language - Change language
webapp - Open web interface
```

---

## 📦 Step 3: Push Code to GitHub

1. **Fork or clone this repository** to your GitHub account
2. Make sure all files are committed and pushed

---

## 🚀 Step 4: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Add **Environment Variables**:
   
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   BOT_TOKEN=your_bot_token_here
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database
   ADMIN_IDS=your_telegram_user_id
   URL2CASH_API=your_url2cash_api_key
   ADRINOLINKS_API=your_adrinolinks_api_key
   ```

6. Click **"Deploy"**
7. Wait for deployment to complete
8. Copy your deployment URL (e.g., `https://your-app.vercel.app`)

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts and add environment variables when asked
```

---

## 🔗 Step 5: Setup Webhook

After deployment, you need to configure the Telegram webhook:

1. Add the `WEBHOOK_URL` environment variable in Vercel:
   ```
   WEBHOOK_URL=https://your-app.vercel.app
   ```

2. Run the webhook setup script:
   ```bash
   # Install dependencies first
   pip install requests python-dotenv

   # Set your environment variables
   export TELEGRAM_BOT_TOKEN=your_bot_token
   export WEBHOOK_URL=https://your-app.vercel.app

   # Run setup script
   python setup_webhook.py
   ```

3. You should see:
   ```
   ✅ Webhook set successfully!
   📍 URL: https://your-app.vercel.app/api/webhook
   ```

**Alternative: Set webhook manually via browser**
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app.vercel.app/api/webhook
```

---

## ✅ Step 6: Test Your Bot

1. Open Telegram and search for your bot
2. Send `/start` command
3. You should see a beautiful welcome message with categories!
4. Try other commands like `/help`, `/browsegame`, `/movies`, etc.

---

## 🎨 Step 7: Customize (Optional)

### Add OpenRouter AI Key (Free!)

1. Get a FREE API key from [OpenRouter](https://openrouter.ai/keys)
2. Send to your bot: `/addapikey sk-or-v1-your-key-here`
3. Now `/aisearch` will use AI to find content!

### Customize Categories

Edit the categories in these files:
- `handlers/user_commands.py` - For browse menus
- `services/movie_scraper.py` - For movie categories
- `utils/translations.py` - For UI text

---

## 📊 Monitor Your Bot

### Check Webhook Status
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

### Vercel Logs
1. Go to your project in Vercel Dashboard
2. Click on "Deployments"
3. Click on latest deployment
4. View "Functions" tab to see logs

---

## 🐛 Troubleshooting

### Bot Not Responding?

1. **Check webhook status:**
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
   ```
   Should show your Vercel URL and no errors.

2. **Check Vercel function logs:**
   - Go to Vercel Dashboard → Your Project → Deployments → Latest → Functions
   - Look for errors in `/api/webhook` function

3. **Verify environment variables:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Make sure `TELEGRAM_BOT_TOKEN`, `MONGO_URI` are set correctly

4. **Check MongoDB connection:**
   - Make sure IP whitelist includes `0.0.0.0/0`
   - Verify connection string is correct

### "Function Timeout" Error?

- Free tier has 10-second timeout for functions
- If scraping takes too long, consider:
  - Using quick scrape instead of full scrape
  - Caching results in MongoDB
  - Breaking large operations into smaller chunks

### Webhook SSL Error?

- Vercel provides HTTPS by default
- Make sure your webhook URL starts with `https://` not `http://`

---

## 💰 Cost Breakdown

### Vercel Free Tier Includes:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ 100GB-hours serverless function execution
- ✅ SSL certificates (HTTPS)
- ✅ Custom domains (if you have one)

### MongoDB Atlas Free Tier Includes:
- ✅ 512MB storage
- ✅ Shared RAM
- ✅ No credit card required

### **Total Cost: $0/month** 🎉

---

## 🔄 Updating Your Bot

1. Make changes to your code
2. Push to GitHub
3. Vercel auto-deploys! 🚀

Or manually redeploy:
```bash
vercel --prod
```

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [Python Telegram Bot Docs](https://docs.python-telegram-bot.org/)

---

## 🎉 Success!

Your bot is now running on Vercel's free tier! Enjoy unlimited scalability and zero server management!

**Need help?** Open an issue on GitHub or check the documentation above.

---

### 🌟 Features Available:

- ✅ **Software Distribution** - Share apps & tools
- ✅ **Game Library** - Latest games catalog
- ✅ **Movie Database** - HD movies & shows
- ✅ **NFT Claiming** - Free digital collectibles
- ✅ **Game Scripts** - Pro mods & scripts
- ✅ **AI Search** - Smart content discovery
- ✅ **Multi-language** - 6 languages supported
- ✅ **Web App** - Beautiful Telegram Mini App

**Happy distributing!** 🚀
