# Telegram Software Distribution Bot

## Overview
This project is a production-ready Telegram bot designed for automated software and game distribution. Its primary purpose is to provide users with an AI-powered platform to discover and download software, while simultaneously offering monetization opportunities for the bot owner through automated URL shortening. The bot supports multiple languages, leverages a cloud-based database for scalability, and includes a comprehensive admin panel for content management and analytics. Key capabilities include AI-powered search, web scraping for download links, automated link monetization, and a system for distributing free NFTs to users. The project now includes a beautiful **Telegram Mini App** with a modern visual interface alongside the traditional bot commands.

## Recent Changes (October 28, 2025)

### ☁️ Vercel Deployment Support
- **Webhook Mode**: Converted bot from polling to webhook mode for Vercel compatibility
- **Serverless Functions**: Created `api/webhook.py` for serverless deployment on Vercel
- **Configuration**: Added `vercel.json` for automatic Vercel deployment setup
- **Setup Script**: Created `setup_webhook.py` to easily configure webhooks
- **Free Hosting**: Bot can now run 100% FREE on Vercel's free tier with automatic scaling
- **Comprehensive Guide**: Created detailed VERCEL_DEPLOYMENT.md with step-by-step instructions

### 🎨 Visual Design Improvements
- **Creative Colors**: Enhanced bot interface with box-drawing characters and attractive formatting
- **Beautiful Welcome**: Redesigned `/start` command with stunning visual layout showcasing all 5 categories
- **Organized Help Menu**: Completely restructured `/help` command with sectioned categories:
  - Games & Software section
  - Movies & Shows section (with streaming platforms, industries, and languages)
  - Special Features section (NFTs, Game Scripts, Web App)
  - Your Account section
- **Category Showcase**: All 5 content types (Games, Software, Movies, NFTs, Game Scripts) prominently displayed
- **Enhanced Documentation**: Updated README with emoji headers and better organization

### 📄 Documentation Updates
- **VERCEL_DEPLOYMENT.md**: Complete guide for deploying to Vercel free tier
- **README.md**: Enhanced with all 5 categories clearly highlighted, deployment options, and comprehensive command list
- **.env.example**: Updated with WEBHOOK_URL and clear comments for Vercel deployment

## Recent Changes (October 28, 2025 - Earlier)

### 🚀 Telegram Mini App Integration
- **Hybrid Architecture**: Implemented a complete Telegram Mini App alongside the existing bot commands
- **React Frontend**: Built a modern, responsive web interface using React + Vite with Telegram WebApp SDK
- **FastAPI Backend**: Created RESTful API endpoints for games, movies, NFTs, game scripts, and user data
- **Visual Browsing**: Users can now browse content with beautiful card-based UI instead of text-only bot messages
- **Dual Access**: Users can choose between bot commands (`/search`, `/movies`) or the visual mini app interface
- **WebApp Command**: Added `/webapp` command to launch the mini app with a single click
- **Authentication**: Integrated Telegram WebApp authentication for seamless user experience
- **Profile Page**: Users can view their download history and favorites in a visual dashboard
- **Search & Filters**: Implemented real-time search and category filtering in the mini app
- **Responsive Design**: Mobile-optimized UI that works perfectly in Telegram's WebView

### Technical Stack - Mini App
```
webapp/                    # React frontend
├── src/
│   ├── pages/            # Home, Games, Movies, NFTs, Scripts, Profile
│   ├── components/       # Reusable UI components (Navbar, ItemCard)
│   └── utils/            # API client and utilities
api/                      # FastAPI backend
└── main.py              # RESTful API with authentication
start-miniapp.sh         # Combined startup script for API + Frontend
```

## Recent Changes (October 25, 2025)

### Link Shortener Optimization
- **AdRINo Priority**: Changed URL shortener to prioritize AdrinoLinks.in over URL2cash.in as the primary shortening service
- **Updated API Key**: Updated AdrinoLinks API key to: `730eb23c10b70ba35d1a7d1d210c5cada3b2dab3`
- **On-Demand Shortening**: Movie links are now stored as ORIGINAL URLs in the database during scraping
- **User-Request Shortening**: Links are shortened on-demand only when users request movies via `/searchmovie` or `/movies` commands
- **Database Safety**: Added guards to handle cases where URL cache collection might not be initialized
- **Improved Efficiency**: Eliminates unnecessary API calls during scraping, saves API quota for actual user requests

### Category-Specific Movie Search Commands
- **13 New Commands**: Added category-specific movie search commands for each movie category
  - `/movienetflix` - Search Netflix movies only
  - `/movieprime` - Search Prime movies only
  - `/moviehotstar` - Search Hotstar movies only
  - `/moviehindi`, `/movieenglish`, `/movietamil`, `/movietelugu`, `/moviemalayalam`, `/moviekannada` - Language-specific searches
  - `/moviebollywood`, `/moviehollywood`, `/moviesouth` - Region-specific searches
  - `/moviewebseries` - Web-Series only search
- **Updated /searchmovie**: Now clearly indicates it searches ALL categories
- **Removed /netflix alias**: Replaced with category-specific commands for better organization
- **Enhanced Help**: Updated help command to show all category-specific search options

### Movie Scraping Enhancements
- **Increased Page Limit**: Raised scraping limit from 10 to 100 pages per command
- **Duplicate Prevention**: Automatic duplicate detection ensures safe re-scraping
- **Progress Tracking**: Better feedback during long scraping operations

### Documentation
- **ADMIN_COMMANDS_LIST.md**: Created comprehensive admin commands reference file with all 30+ admin commands documented including usage, examples, and best practices

## User Preferences
- No specific preferences set yet

## System Architecture

### Directory Structure
```
├── main.py                    # Bot entry point with polling (local dev)
├── api/
│   ├── webhook.py             # Webhook handler for Vercel deployment
│   └── main.py                # FastAPI backend for mini app
├── vercel.json                # Vercel deployment configuration
├── setup_webhook.py           # Webhook setup utility
├── VERCEL_DEPLOYMENT.md       # Complete Vercel deployment guide
├── handlers/
│   ├── user_commands.py       # User commands (includes /webapp command)
│   ├── admin_commands.py      # Admin commands (add software, stats, earnings, scraping)
│   └── download_handler.py    # Download & callback handlers
├── services/
│   ├── url_shortener.py       # Dual URL shortener with smart rotation
│   ├── ai_service.py          # OpenRouter AI for intelligent search (FREE DeepSeek R1)
│   ├── scraper.py             # Web scraping for download links
│   ├── advanced_scraper.py    # AI-powered multi-page scraping
│   └── movie_scraper.py       # Async movie scraping from thenextplanet.beer
├── utils/
│   ├── translations.py        # Multi-language support
│   └── database.py            # MongoDB connection and utilities
├── api/
│   └── main.py                # FastAPI backend for mini app
├── webapp/                    # React mini app frontend
│   ├── src/
│   │   ├── pages/            # Home, Games, Movies, NFTs, Scripts, Profile
│   │   ├── components/       # Navbar, ItemCard
│   │   ├── utils/            # API client
│   │   ├── App.jsx           # Main app with routing
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── start-miniapp.sh          # Startup script for API + Frontend
├── .env.example              # Configuration template
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation
```

### Key Features
- **Vercel Deployment**: Full support for FREE hosting on Vercel's serverless platform with webhook mode, automatic scaling, and zero server management. Includes comprehensive deployment guide.
- **Beautiful UI**: Creative box-drawing characters, emoji icons, and structured formatting make the bot visually attractive and easy to navigate. All 5 content categories prominently showcased.
- **Telegram Mini App**: Modern web interface with visual browsing for games, movies, NFTs, and scripts. Accessible via `/webapp` command with seamless Telegram authentication.
- **Monetization**: On-demand URL shortening with dual service integration (AdrinoLinks.in as primary, URL2cash.in as fallback). Links are shortened only when users request them, optimizing API usage and costs.
- **Movie Browsing**: Fully async category-based movie browsing system that scrapes thenextplanet.beer website in real-time. Users can browse movies by category (Netflix, Bollywood, Hollywood, etc.) with automatic download link extraction. Links are stored in their original form during scraping and shortened on-demand when users request them. Supports pagination and doesn't block the bot during scraping operations.
- **AI Search**: Utilizes OpenRouter AI with a multi-model fallback system (Qwen → Llama → Gemini → Mistral) for robust and free AI-powered natural language search, including web search fallback for external links.
- **NFT Claiming**: Admin-managed feature allowing users to claim free NFTs, with tracking of claims and NFT management commands.
- **Game Scripts**: Admin-managed feature for sharing game scripts with users. Admins can add/list/remove scripts, and users can browse available scripts with view count tracking.
- **Multi-language Support**: Comprehensive translation system supporting 6 languages (EN, ES, FR, DE, AR, HI).
- **Smart Caching**: Implements URL caching to minimize API calls and track link usage.
- **Analytics**: Provides download tracking and estimated earnings dashboards for admins.
- **Universal Scraping**: AI-powered multi-page scraping capabilities that can work with any website structure to extract software/game details and download links. This includes intelligent article/listing detection, smart pagination handling, and extraction of content from various HTML structures.
- **Admin Tools**: Full suite of commands for managing the software catalog, including scraping, adding/removing items, and managing API keys.
- **Dual Interface**: Users can access content via traditional bot commands or the visual mini app interface, providing flexibility and better user experience.

### Database Schema (MongoDB Atlas)
- `users`: Stores user profiles, preferences, download history, and favorites.
- `software`: Contains the software/game catalog with details like name, category, OS, links, and ratings.
- `downloads`: Tracks download analytics, including timestamps and service usage.
- `reviews`: Stores user ratings and reviews for software/games.
- `url_cache`: Caches shortened URLs to optimize API usage.
- `api_keys`: Stores OpenRouter API keys for load balancing and management.
- `nfts`: Stores NFT details (ID, name, link, description) and tracks claim data.
- `game_scripts`: Stores game script details (ID, name, link, description) with view count tracking and active/inactive status.

## External Dependencies
- **Telegram Bot API**: For bot interaction and messaging.
- **OpenRouter API**: Provides access to various AI models (e.g., DeepSeek R1) for AI search capabilities.
- **MongoDB Atlas**: Cloud-based NoSQL database for data storage and management.
- **URL2cash.in**: Third-party URL shortening service for monetization.
- **AdrinoLinks.in**: Another third-party URL shortening service for monetization.
- **DuckDuckGo**: Used as a search engine for the web search fallback feature in `/aisearch`.