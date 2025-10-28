# 🔥 Full Scraping Guide - Get Download Links!

## New Features Added

I've added **full scraping** commands that visit each game/software page individually to extract:
- ✅ Download links (MediaFire, Mega, Google Drive, etc.)
- ✅ Complete descriptions
- ✅ File sizes
- ✅ Versions
- ❌ NO screenshots (to keep database small)

---

## 📊 Two Scraping Modes

### ⚡ Quick Scraping (FAST - Titles Only)
**Commands:** `/quickscrapesoft`, `/quickscrapegame`

**Speed:** 0.5s per page  
**Gets:** Game/software titles and URLs  
**Use when:** You want to quickly populate your database with names

```bash
/quickscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
```

**Result:** 205 games scraped in ~2 seconds ⚡

---

### 🔍 Full Scraping (COMPLETE - With Download Links)
**Commands:** `/fullscrapesoft`, `/fullscrapegame`

**Speed:** 2-3s per item  
**Gets:** 
- Game/software titles
- **Download links** (MediaFire, Mega, etc.)
- Complete descriptions
- File sizes
- Versions

**Use when:** You want complete information including download links

```bash
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
```

**Result:** First page games scraped with download links in ~60 seconds

---

## 🚀 Full Scraping Commands

### For Games

#### Basic Usage
```bash
/fullscrapegame <url> page <number>
```

#### Examples
```bash
# Scrape first page (usually ~15-20 games)
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1

# Scrape first 5 pages
/fullscrapegame https://www.apunkagames.com/action-games-for-pc page 5

# Scrape ALL pages (unlimited)
/fullscrapegame https://www.apunkagames.com/racing-games page 0

# With custom category
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 3 category Fighting
```

---

### For Software

#### Basic Usage
```bash
/fullscrapesoft <url> page <number>
```

#### Examples
```bash
# Scrape first page
/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 1

# Scrape first 5 pages
/fullscrapesoft https://bestcracksoftwares.com/category/audio-plugin-tool/ page 5

# Scrape ALL pages (unlimited)
/fullscrapesoft https://bestcracksoftwares.com/category/video-editor/ page 0

# With custom category
/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 3 category 3D Design
```

---

## ⚡ Quick vs Full Comparison

| Feature | Quick Scraping | Full Scraping |
|---------|---------------|---------------|
| **Speed** | ⚡ 0.5s/page | 🐢 2-3s/item |
| **Titles** | ✅ Yes | ✅ Yes |
| **URLs** | ✅ Yes | ✅ Yes |
| **Download Links** | ❌ No | ✅ **Yes** |
| **Descriptions** | ⚠️ Basic | ✅ Complete |
| **File Sizes** | ❌ Unknown | ✅ Extracted |
| **Versions** | ❌ Latest | ✅ Detected |
| **Best For** | Quick populate | Complete data |

---

## 💡 Smart Workflow

### Option 1: Quick First, Full Later
```bash
# Step 1: Quick scrape to get all titles (fast)
/quickscrapegame https://www.apunkagames.com/fighting-games-for-pc page 0

# Step 2: Later, full scrape specific categories for download links
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
```

### Option 2: Full Scraping from Start
```bash
# Get everything at once (slower but complete)
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 5
```

---

## 📋 Real-World Examples

### Example 1: Scrape Fighting Games with Download Links
```bash
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
```

**What happens:**
1. Phase 1: Gets list of 205 fighting games (~2s)
2. Phase 2: Visits first page games (15-20 items)
3. Extracts download links from each game page
4. **Time:** ~60 seconds for first page
5. **Result:** 15-20 games with download links!

---

### Example 2: Scrape All 3D Tools
```bash
/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 0
```

**What happens:**
1. Scrapes ALL pages automatically
2. Visits each software page
3. Extracts download links, descriptions, sizes
4. **Time:** ~2-3s per software
5. **Result:** Complete 3D tools database with download links!

---

### Example 3: Batch Scraping Multiple Categories
```bash
# Fighting games
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1

# Wait for completion, then racing games
/fullscrapegame https://www.apunkagames.com/racing-games page 1

# Then action games
/fullscrapegame https://www.apunkagames.com/action-games-for-pc page 1
```

---

## 🎯 When to Use Which Command

### Use Quick Scraping When:
- ✅ You want to quickly see what's available
- ✅ Building initial database of titles
- ✅ Testing category URLs
- ✅ You'll add download links manually later

### Use Full Scraping When:
- ✅ You need download links immediately
- ✅ Building a complete, ready-to-use database
- ✅ You have time to wait (2-3s per item)
- ✅ You want complete information

---

## ⏱️ Time Estimates

### Quick Scraping
- **1 page (20 items):** ~1 second
- **10 pages (200 items):** ~5 seconds
- **Unlimited (500 items):** ~15 seconds

### Full Scraping
- **1 page (20 items):** ~60 seconds
- **5 pages (100 items):** ~5 minutes
- **10 pages (200 items):** ~10 minutes

---

## 🔗 Download Link Extraction

Full scraping automatically finds links from these services:
- MediaFire
- Mega
- Google Drive
- Dropbox
- GoFile
- PixelDrain
- Krakenfiles
- 1Fichier
- Uploadhaven
- And more...

---

## 📦 What Gets Stored

### Quick Scraping Stores:
```json
{
  "name": "Sodaman",
  "category": "Fighting",
  "version": "Latest",
  "file_size": "Unknown",
  "description": "Sodaman - Free Download",
  "download_links": [],
  "source_url": "https://..."
}
```

### Full Scraping Stores:
```json
{
  "name": "Sodaman",
  "category": "Fighting",
  "version": "1.0",
  "file_size": "2.5 GB",
  "description": "Sodaman is a unique fighting game featuring...",
  "download_links": [
    {"url": "https://mediafire.com/...", "type": "direct"},
    {"url": "https://mega.nz/...", "type": "direct"}
  ],
  "source_url": "https://..."
}
```

---

## ⚠️ Important Notes

1. **No Screenshots:** Full scraping does NOT download images to keep database small
2. **Respect Sites:** 1-second delay between page visits
3. **Duplicates:** Automatically skips games/software already in database
4. **Unlimited Mode:** Use `page 0` to scrape until no items found
5. **Categories:** Auto-detected from URLs

---

## 🎊 Start Using Full Scraping

### For Games:
```bash
# Get first page with download links
/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 1
```

### For Software:
```bash
# Get first page with download links
/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 1
```

---

## 💾 Check Your Database

After scraping, check what was added:
```bash
/dbinfo
```

This shows:
- Total items in database
- Items by category
- Download statistics

---

## 🚀 Pro Tips

1. **Start Small:** Test with `page 1` first
2. **Go Big:** Once confirmed working, use `page 0` for unlimited
3. **Batch Categories:** Scrape one category at a time
4. **Mix Modes:** Use quick for exploration, full for important categories
5. **Monitor Progress:** Bot shows live progress for each item

---

Enjoy complete scraping with download links! 🎉
