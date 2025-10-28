# 🎮 Telegram Distribution Bot - Your Ultimate Digital Hub

A production-ready Python Telegram bot for automated distribution of **Software, Games, Movies, NFTs, and Game Scripts** with AI-powered search, MongoDB storage, and URL shortener monetization.

## 🌟 What's Inside?

### 📦 Content Categories
- **🎮 Games** - Latest PC games with auto-categorization (Action, RPG, Strategy, etc.)
- **💻 Software** - Professional tools (3D Tools, Graphics, Security, Office, etc.)
- **🎬 Movies** - HD Movies & Shows (Netflix, Prime, Bollywood, Hollywood, Regional)
- **🎨 NFTs** - Free digital collectibles for users to claim
- **🎯 Game Scripts** - Pro mods, cheats, and game enhancements

### ✨ Core Features

- **🚀 Ultra-Fast Scraping** - NO AI = NO rate limits! Scrape unlimited pages instantly
- **♾️ Unlimited Pages** - Set page to 0 for automatic scraping until completion
- **📂 Auto-Categorization** - Smart category detection from URLs
- **🌍 Multi-language Support** - 6 languages (English, Spanish, French, German, Arabic, Hindi)
- **🤖 AI-Powered Search** - OpenRouter integration for intelligent natural language queries
- **💰 Automated Monetization** - Dual URL shortener rotation (URL2cash.in & AdrinoLinks.in)
- **⚡ Smart Caching** - Reduces API calls and maximizes efficiency
- **☁️ Cloud Database** - MongoDB Atlas for zero-maintenance data persistence
- **👥 User Management** - Complete profile system with download history and favorites
- **🛡️ Admin Panel** - Full CRUD operations for catalog management
- **📊 Analytics Dashboard** - Real-time earnings tracking and download statistics
- **⭐ Rating System** - User reviews and average rating calculations
- **🎨 Beautiful UI** - Creative colors and attractive formatting with emojis

## 🚀 Deployment Options

### Option 1: Deploy to Vercel (Recommended - FREE!) 

**Perfect for production use with zero server costs!**

✅ **100% Free hosting**  
✅ **Automatic scaling**  
✅ **Global CDN**  
✅ **Zero server management**

👉 **[See Complete Vercel Deployment Guide](VERCEL_DEPLOYMENT.md)**

Quick steps:
1. Push code to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy with one click!
5. Setup webhook

### Option 2: Run Locally (Development)

**For testing and local development**

#### 1. Prerequisites

- Python 3.11+
- Telegram Bot Token (get from @BotFather)
- MongoDB Atlas account (free tier available)
- OpenRouter API key (optional, free tier available)

#### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

#### 3. Configuration

Create a `.env` file from `.env.example`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
BOT_TOKEN=your_telegram_bot_token_from_botfather
ADMIN_IDS=your_telegram_user_id

MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/telegram_bot?retryWrites=true&w=majority

# For Vercel deployment only
WEBHOOK_URL=https://your-app.vercel.app

# URL Shortener APIs
URL2CASH_API=your_api_key
ADRINOLINKS_API=your_api_key
```

#### 4. Run the Bot

```bash
# Polling mode (for local development)
python main.py

# Or run the web API separately
python api/main.py
```

## Getting API Keys

### Telegram Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token provided

### MongoDB Atlas (Free)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free M0 cluster
3. Get connection string (replace username/password)

### Groq API (Free)
1. Visit [groq.com](https://groq.com)
2. Sign up and get API key from console
3. Free tier includes generous limits

### Your Telegram User ID
1. Search for @userinfobot on Telegram
2. Send `/start` to get your user ID
3. Add it to ADMIN_IDS in .env

## 📱 Bot Commands

### 👥 User Commands

#### 🔍 Search & Browse
- `/start` - Welcome message with language selection
- `/help` - Full command list with beautiful formatting
- `/search <query>` - Search software/games by keywords
- `/aisearch <query>` - AI-powered natural language search
- `/browsegame` - Browse games by category (Action, RPG, Strategy, etc.)
- `/browsesoft` - Browse software by category (3D Tools, Graphics, etc.)
- `/popular` - View most downloaded items
- `/new` - Latest releases

#### 🎬 Movies & Entertainment
- `/movies <category>` - Browse movies by category
- `/searchmovie <name>` - Search all movie categories
- `/movienetflix <name>` - Search Netflix content
- `/movieprime <name>` - Search Prime Video content
- `/moviehotstar <name>` - Search Hotstar content
- `/moviebollywood <name>` - Search Bollywood movies
- `/moviehollywood <name>` - Search Hollywood movies
- `/moviesouth <name>` - Search South Indian cinema
- `/moviehindi`, `/movieenglish`, `/movietamil`, `/movietelugu`, etc. - Language-specific searches
- `/moviewebseries <name>` - Search web series

#### 🎨 Special Features
- `/claimnft` - Claim FREE NFTs from available collection
- `/gamescripts` - Browse game scripts, mods, and cheats
- `/webapp` - Open beautiful Telegram Mini App interface

#### 👤 Your Account
- `/favorites` - Your favorite items
- `/mydownloads` - Download history
- `/profile` - Your profile statistics
- `/language` - Change bot language

### Admin Commands

#### 🚀 Quick Scraping (RECOMMENDED - No AI, No Limits!)
- `/quickscrapesoft <url> page <number>` - Fast scrape software (use page 0 for unlimited!)
- `/quickscrapegame <url> page <number>` - Fast scrape games (use page 0 for unlimited!)

**Examples:**
```bash
# Scrape UNLIMITED pages from category
/quickscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 0

# Scrape ALL action games
/quickscrapegame https://www.apunkagames.com/action-games-for-pc page 0
```

#### 💻 Software & Games Management
- `/addsoft <details>` - Add new software with full details
- `/quickadd <name>,<category>,<os>,<size>,<version>` - Quick add software
- `/addsite <url>` - Scrape download links from website
- `/addlink <id> <url>` - Add download link to existing software
- `/deletesoft <id>` - Delete software entry
- `/editsoft <id> <field> <value>` - Edit software fields

#### 🎬 Movies Management
- `/addmovie <title>,<category>,<quality>,<size>` - Add new movie
- `/moviescrape <url> page <number>` - Scrape movies from website
- `/listmovies` - List all movies in database
- `/removemovie <id>` - Remove movie from database
- `/setmovieviews <id> <views>` - Set view count for movie

#### 🎨 NFT Management
- `/addnft <name>,<description>,<image_url>` - Add new NFT
- `/listnfts` - List all available NFTs
- `/removenft <id>` - Remove NFT from collection

#### 🎯 Game Scripts Management
- `/addgamescript <name>,<game>,<description>,<download_url>` - Add game script
- `/listgamescripts` - List all game scripts
- `/removegamescript <id>` - Remove game script
- `/setscriptviews <id> <views>` - Set view count for script

#### 🤖 AI & API Key Management
- `/addapikey <key>` - Add OpenRouter API key for AI search
- `/listapikeys` - List all configured API keys
- `/removeapikey <key_id>` - Remove API key
- `/toggleapikey <key_id>` - Enable/disable API key
- `/apikeystats` - View API key usage statistics

#### 📊 Database & Analytics
- `/dbinfo` - View database statistics (all collections)
- `/stats` - Bot usage statistics
- `/earnings` - Earnings dashboard with monetization breakdown
- `/cleardownloads confirm` - Clear download history
- `/resetdb confirm` - Reset entire database (⚠️ Use with caution!)

#### 🔧 Legacy Tools (AI-based, slower, rate limited)
- `/scrapesoft <url> page <number>` - AI-powered software scraping
- `/scrapegame <url> page <number>` - AI-powered game scraping

## Monetization

The bot automatically shortens all download links using:
- **URL2cash.in** - $3-5 CPM
- **AdrinoLinks.in** - $4-6 CPM

Smart rotation ensures optimal distribution between both services. The earnings dashboard shows real-time statistics and estimated revenue.

## Project Structure

```
telegram-bot/
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (create from .env.example)
├── handlers/
│   ├── user_commands.py    # User command handlers
│   ├── admin_commands.py   # Admin command handlers
│   └── download_handler.py # Download & callback handlers
├── services/
│   ├── url_shortener.py    # Dual URL shortener with caching
│   ├── ai_service.py       # Groq AI integration
│   └── scraper.py          # Web scraping service
└── utils/
    ├── translations.py     # Multi-language support
    └── database.py         # MongoDB utilities
```

## 📦 Database Collections

- **users** - User profiles, preferences, favorites, and download history
- **software** - Software & games catalog with metadata, links, and ratings
- **movies** - Movie database with categories, quality, and streaming info
- **nfts** - NFT collection with metadata and claim tracking
- **game_scripts** - Game scripts, mods, and cheats catalog
- **downloads** - Download analytics and tracking for monetization
- **reviews** - User ratings and reviews for software/games
- **url_cache** - Cached shortened URLs to reduce API calls
- **api_keys** - OpenRouter API keys for AI search functionality

## Windows 24/7 Deployment

### Run as Windows Service (Recommended)

Using NSSM (Non-Sucking Service Manager):

```cmd
# Download NSSM from nssm.cc
# Run as Administrator
nssm install TelegramBot "C:\Python311\python.exe" "C:\path\to\main.py"
nssm set TelegramBot AppDirectory "C:\path\to\bot"
nssm start TelegramBot
```

### Task Scheduler (Auto-start on boot)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When computer starts"
4. Action: Start program `python.exe` with argument `main.py`
5. Save

## Support

For issues or questions:
1. Check logs for error messages
2. Verify all API keys are correct in .env
3. Ensure MongoDB connection string is valid
4. Test bot with /start command

## License

MIT License - feel free to modify and use for your projects!

## Credits

Built with:
- python-telegram-bot
- MongoDB Atlas
- Groq AI
- URL2cash.in & AdrinoLinks.in
