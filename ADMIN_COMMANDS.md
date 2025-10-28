# Admin Commands Reference

## Database Management Commands

### 1. `/dbinfo` - Database Information
Shows comprehensive database statistics including:
- Total software entries (games and software separately)
- User count
- Download statistics
- Review count
- URL cache size
- All categories

**Usage:**
```
/dbinfo
```

---

### 2. `/deletesoft` - Delete Software
Delete a specific software entry from the database by its ID.

**Usage:**
```
/deletesoft <software_id>
```

**Example:**
```
/deletesoft 507f1f77bcf86cd799439011
```

**Output:**
- Shows the deleted software name, category, and download count
- Confirms successful deletion

---

### 3. `/editsoft` - Edit Software
Edit specific fields of a software entry.

**Available Fields:**
- name
- category
- version
- file_size
- description

**Usage:**
```
/editsoft <software_id> <field> <new_value>
```

**Examples:**
```
/editsoft 507f1f77bcf86cd799439011 name VLC Media Player
/editsoft 507f1f77bcf86cd799439011 version 3.0.20
/editsoft 507f1f77bcf86cd799439011 category Video Player
```

**Output:**
- Shows old value and new value
- Confirms successful update

---

### 4. `/cleardownloads` - Clear Download History
Clears all download records and resets download counters.

**Important:** This requires confirmation to prevent accidental deletion.

**Usage:**
```
/cleardownloads          # Shows warning and count
/cleardownloads confirm  # Actually clears the data
```

**What it does:**
- Deletes all download records from downloads collection
- Resets user download history
- Resets software download counters to 0

---

### 5. `/resetdb` - Complete Database Reset
**⚠️ DANGER ZONE ⚠️**

Completely wipes the entire database. This will delete:
- All software entries
- All users
- All downloads
- All reviews
- All URL cache

**Important:** This requires confirmation and CANNOT BE UNDONE!

**Usage:**
```
/resetdb          # Shows warning and statistics
/resetdb confirm  # Actually resets the database
```

**Output:**
- Shows count of deleted items from each collection
- Confirms database is empty and ready for fresh data

---

## 🔥 NEW: Full Scraping (With Download Links!)

### `/fullscrapesoft` - Full Scrape Software (With Download Links)
**COMPLETE** scraping that visits each page to get download links!

**Features:**
- 🔗 Extracts download links (MediaFire, Mega, Google Drive, etc.)
- 📄 Complete descriptions (up to 500 chars)
- 💾 File sizes detected
- 🏷️ Version numbers extracted
- ❌ NO screenshots (keeps database small)

**Speed:** ~2-3 seconds per item (slower but complete)

**Usage:**
```
/fullscrapesoft <url> page <number>
/fullscrapesoft <url> page <number> category <name>
/fullscrapesoft <url> page 0  (unlimited)
```

**Examples:**
```
/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 1
/fullscrapesoft https://bestcracksoftwares.com/category/audio-plugin-tool/ page 5
/fullscrapesoft https://bestcracksoftwares.com/category/video-editor/ page 0
```

---

### `/fullscrapegame` - Full Scrape Games (With Download Links)
Same as fullscrapesoft but for game websites.

**Usage:**
```
/fullscrapegame <url> page <number>
/fullscrapegame <url> page <number> category <name>
/fullscrapegame <url> page 0  (unlimited)
```

**Examples:**
```
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
/fullscrapegame https://www.apunkagames.com/action-games-for-pc page 5
/fullscrapegame https://www.apunkagames.com/racing-games page 0
```

**What Full Scraping Does:**
1. **Phase 1:** Gets list of games/software from category pages (fast)
2. **Phase 2:** Visits each individual page to extract:
   - Download links (MediaFire, Mega, Drive, etc.)
   - Complete descriptions
   - File sizes
   - Versions
3. **Result:** Complete database ready for users!

---

## 🚀 Quick Scrape Commands (NO AI - Fast & No Rate Limits!)

### `/quickscrapesoft` - Quick Scrape Software (No AI)
**FAST** scraping without AI - perfect for category pages with many items!

**Features:**
- ⚡ No AI processing = No rate limits
- 📂 Auto-detects category from URL
- 🎯 Works perfectly with category listing pages
- ⏱️ Much faster than AI scraping

**Usage:**
```
/quickscrapesoft <url> page <number>
/quickscrapesoft <url> page <number> category <category_name>
```

**Perfect for sites like:**
- `bestcracksoftwares.com/category/3d-tools/`
- `bestcracksoftwares.com/category/audio-plugin-tool/`
- `bestcracksoftwares.com/category/activator-tools/`

**Examples:**
```
/quickscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 5
/quickscrapesoft https://bestcracksoftwares.com/category/audio-plugin-tool/ page 3
/quickscrapesoft https://example.com/multimedia/ page 2 category Multimedia
```

**How it works:**
1. Extracts items directly from listing pages (doesn't visit each article)
2. Auto-detects category from URL patterns (action, racing, 3d-tools, audio, etc.)
3. Extracts title, version, size, description from the listing page
4. No AI calls = No rate limits = Much faster!

---

### `/quickscrapegame` - Quick Scrape Games (No AI)
Same as quickscrapesoft but optimized for game websites.

**Usage:**
```
/quickscrapegame <url> page <number>
/quickscrapegame <url> page <number> category <category_name>
```

**Perfect for sites like:**
- `www.apunkagames.com/action-games-for-pc`
- `www.apunkagames.com/racing-games`
- `www.apunkagames.com/rpg/`

**Examples:**
```
/quickscrapegame https://www.apunkagames.com/action-games-for-pc page 5
/quickscrapegame https://www.apunkagames.com/racing-games page 3
/quickscrapegame https://example.com/rpg/ page 2 category RPG Games
```

**Auto-detected categories:**
- Games: Action, Adventure, Racing, Sports, Strategy, RPG, Shooter, Simulation, Horror, Puzzle
- Software: 3D Tools, Activator, Audio, Browser, Graphics, Multimedia, Office, Security, Utilities, Video

---

## Existing Admin Commands

### `/addsoft` - Add Software Manually
Add software with full details including multiple download links.

**Usage:**
```
/addsoft <name> | <category> | <OS> | <size> | <version> | <description> | <link1> | <link2> | ...
```

**Example:**
```
/addsoft VLC Player | Video | Windows,Mac,Linux | 50MB | 3.0.18 | Best media player | https://download.com/vlc.exe
```

---

### `/quickadd` - Quick Add Software
Quickly add software with basic info (you can add download links later).

**Usage:**
```
/quickadd <name>,<category>,<OS>,<size>,<version>
```

**Example:**
```
/quickadd Chrome,Browser,Windows,100MB,120.0
```

---

### `/addlink` - Add Download Link
Add a download link to existing software.

**Usage:**
```
/addlink <software_id> <download_url>
```

---

### `/addsite` - Scrape Website
Automatically scrape download links from a website.

**Usage:**
```
/addsite <website_url>
```

---

### `/scrapesoft` - Scrape Software Pages
Scrape multiple pages of software with AI categorization.

**Usage:**
```
/scrapesoft <url> page <number>
/scrapesoft <url> page <number> category <category_name>
```

**Examples:**
```
/scrapesoft https://www.cracksoft.xyz/ page 5
/scrapesoft https://bestcracksoftwares.com/category/multimedia/ page 3 category Multimedia
```

---

### `/scrapegame` - Scrape Game Pages
Same as scrapesoft but optimized for game websites.

**Usage:**
```
/scrapegame <url> page <number>
/scrapegame <url> page <number> category <category_name>
```

**Examples:**
```
/scrapegame https://apunkagames.net.pk/ page 5
/scrapegame https://www.apunkagames.com/action-games-for-pc page 3 category Action Games
```

---

### `/stats` - Bot Statistics
Shows bot statistics including:
- Total software count
- Total downloads
- Today's downloads
- Top 5 most downloaded software

---

### `/earnings` - Earnings Dashboard
Shows detailed earnings report from URL shorteners:
- Total downloads
- Today's downloads
- Breakdown by shortener service (URL2cash, AdrinoLinks)
- Estimated earnings based on CPM rates
- Links to check actual earnings on dashboards

---

## Safety Features

All new database management commands include:
- Admin-only access control
- Confirmation required for destructive operations
- Detailed previews before deletion
- Error handling and validation
- Success/failure notifications

## Access Control

All admin commands check if the user is an admin using the `ADMIN_ID` or `ADMIN_IDS` environment variables. Non-admin users will see:
```
⛔ Admin only command!
```
