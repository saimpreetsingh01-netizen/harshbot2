# Admin Commands Reference

This is a complete reference of all admin commands available in the Telegram Bot.

## 📊 Statistics & Monitoring

### `/stats`
View bot statistics including:
- Total users count
- Total software count
- Total downloads count  
- Top downloaded items
- Recent user activity

**Usage:** `/stats`

### `/earnings`
View estimated earnings from URL shortening:
- Total shortened links
- Estimated revenue
- Service usage breakdown (AdRINo vs URL2cash)
- Recent shortening activity

**Usage:** `/earnings`

### `/dbinfo`
Display database information:
- Total documents in each collection
- Database health status
- Collection sizes
- Index information

**Usage:** `/dbinfo`

---

## 💾 Software Management

### `/addsoft`
Add new software/game to the database manually.

**Usage:** 
```
/addsoft <name>|<category>|<OS>|<link>|<description>
```

**Example:**
```
/addsoft Photoshop|Design|Windows|https://link.com|Photo editing software
```

### `/quickadd`
Quick add software with just name and link (auto-fills other fields).

**Usage:** `/quickadd <name> <link>`

**Example:** `/quickadd Photoshop https://download-link.com`

### `/addsite`
Add a download site/link to existing software.

**Usage:** `/addsite <software_id> <site_url>`

**Example:** `/addsite 12345abc https://mega.nz/download-link`

### `/addlink`
Add an additional download link to existing software.

**Usage:** `/addlink <software_id> <link_url>`

**Example:** `/addlink 12345abc https://alternative-download.com`

### `/deletesoft`
Delete software from database by ID or name.

**Usage:** `/deletesoft <software_id or name>`

**Example:** `/deletesoft 12345abc`

### `/editsoft`
Edit existing software details.

**Usage:** 
```
/editsoft <software_id>
```
Then follow the interactive prompts to update fields.

---

## 🕷️ Web Scraping Commands

### `/scrapesoft`
Scrape software from a specific website.

**Usage:** `/scrapesoft <website_url>`

**Example:** `/scrapesoft https://example-software-site.com`

### `/scrapegame`
Scrape games from a specific website.

**Usage:** `/scrapegame <website_url>`

**Example:** `/scrapegame https://example-game-site.com`

### `/quickscrapesoft`
Quick scrape software using simplified scraper (faster but less detailed).

**Usage:** `/quickscrapesoft <website_url>`

### `/quickscrapegame`
Quick scrape games using simplified scraper.

**Usage:** `/quickscrapegame <website_url>`

### `/fullscrapesoft`
Full deep scrape with AI-powered extraction (slower but more accurate).

**Usage:** `/fullscrapesoft <website_url>`

### `/fullscrapegame`
Full deep scrape for games with AI extraction.

**Usage:** `/fullscrapegame <website_url>`

---

## 🎬 Movie Management

### `/moviescrape`
Scrape movies from thenextplanet.beer by category.

**Usage:** `/moviescrape <category> <pages>`

**Available Categories:**
- NETFLIX, PRIME, HOTSTAR
- HINDI, ENGLISH, TAMIL, TELUGU, MALAYALAM, KANNADA
- BOLLYWOOD, HOLLYWOOD, SOUTH
- WEB-SERIES

**Examples:**
```
/moviescrape NETFLIX 5      (scrape 5 pages of Netflix)
/moviescrape BOLLYWOOD 10   (scrape 10 pages of Bollywood)
/moviescrape HOLLYWOOD 50   (scrape 50 pages of Hollywood)
```

**Note:** Max 100 pages per scrape. Each page ~30-60 seconds.

### `/addmovie`
Manually add a movie to database.

**Usage:**
```
/addmovie <movie_id>|<name>|<link>|<description>
```

**Example:**
```
/addmovie movie123|Avengers Endgame|https://download.link|Marvel superhero film
```

### `/listmovies`
List all movies in the database (admin view).

**Usage:** `/listmovies`

### `/removemovie`
Remove a movie from database.

**Usage:** `/removemovie <movie_id>`

**Example:** `/removemovie movie123`

### `/setmovieviews`
Manually set view count for a movie.

**Usage:** `/setmovieviews <movie_id> <views_count>`

**Example:** `/setmovieviews movie123 5000`

---

## 🎨 NFT Management

### `/addnft`
Add a new NFT for users to claim.

**Usage:**
```
/addnft <nft_id>|<name>|<link>|<description>
```

**Example:**
```
/addnft nft001|CryptoArt #1|https://opensea.io/link|Exclusive digital art
```

### `/listnfts`
List all available NFTs.

**Usage:** `/listnfts`

### `/removenft`
Remove an NFT from the system.

**Usage:** `/removenft <nft_id>`

**Example:** `/removenft nft001`

---

## 🎮 Game Scripts Management

### `/addgamescript`
Add a new game script.

**Usage:**
```
/addgamescript <script_id>|<name>|<link>|<description>
```

**Example:**
```
/addgamescript script01|GTA Mod Menu|https://link.com|Advanced mod menu
```

### `/listgamescripts`
List all game scripts.

**Usage:** `/listgamescripts`

### `/removegamescript`
Remove a game script.

**Usage:** `/removegamescript <script_id>`

**Example:** `/removegamescript script01`

### `/setscriptviews`
Set view count for a game script.

**Usage:** `/setscriptviews <script_id> <views_count>`

**Example:** `/setscriptviews script01 1000`

---

## 🔑 API Key Management

### `/addapikey`
Add OpenRouter API key for AI search.

**Usage:** `/addapikey <service> <api_key>`

**Example:** `/addapikey openrouter sk-or-v1-xxxxxxxxxxxxx`

### `/listapikeys`
List all configured API keys (masked for security).

**Usage:** `/listapikeys`

### `/removeapikey`
Remove an API key from the system.

**Usage:** `/removeapikey <service> <api_key>`

**Example:** `/removeapikey openrouter sk-or-v1-xxxxxxxxxxxxx`

### `/toggleapikey`
Enable/disable an API key without deleting it.

**Usage:** `/toggleapikey <service> <api_key>`

**Example:** `/toggleapikey openrouter sk-or-v1-xxxxxxxxxxxxx`

### `/apikeystats`
View API key usage statistics.

**Usage:** `/apikeystats`

---

## 🗑️ Database Maintenance

### `/cleardownloads`
Clear all download history from database (keeps users and software).

**Usage:** `/cleardownloads`

**Warning:** This action cannot be undone!

### `/resetdb`
**DANGER:** Reset entire database (deletes everything).

**Usage:** `/resetdb CONFIRM`

**Warning:** This will delete ALL data including users, software, movies, NFTs, etc!

---

## 💡 Quick Reference

### Most Used Commands:
1. `/stats` - Check bot performance
2. `/moviescrape NETFLIX 10` - Scrape movies
3. `/earnings` - Check monetization
4. `/listmovies` - View movie database
5. `/dbinfo` - Database health

### Scraping Tips:
- Movies: Max 100 pages per command (can run multiple times)
- Duplicates are auto-skipped (safe to re-scrape)
- Links stored as originals (shortened on user request)
- Each page takes ~30-60 seconds

### Best Practices:
- Always check `/stats` before and after scraping
- Use `/dbinfo` to monitor database size
- Regularly check `/earnings` to track revenue
- Back up data before using `/cleardownloads` or `/resetdb`

---

## 📝 Notes

- All commands are **admin-only** - regular users cannot access them
- Commands are case-sensitive
- Use exact syntax as shown in examples
- Bot must have proper permissions and environment variables configured
- AdRINo link shortener is prioritized over URL2cash
- Movie scraping respects website rate limits
- Database operations are logged for audit

---

Last Updated: October 25, 2025
