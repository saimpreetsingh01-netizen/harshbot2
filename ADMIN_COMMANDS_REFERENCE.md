# Admin Commands Reference 📚

## API Key Management Commands

### `/addapikey <key>`
Add a new DeepSeek API key to the system for load balancing.

**Usage:**
```
/addapikey sk-abc123xyz456def789...
```

**Response:**
- Confirms key was added
- Shows masked key preview
- Displays total active keys
- Shows key ID for future reference

**Notes:**
- Keys must start with `sk-`
- Duplicate keys are rejected
- Automatically activates load balancing

---

### `/listapikeys`
List all DeepSeek API keys (environment + database).

**Usage:**
```
/listapikeys
```

**Shows:**
- Environment key (from DEEPSEEK_API secret)
- All database keys with status
- Usage count per key
- Active/inactive status
- Total active clients

**Use for:**
- Checking which keys are active
- Finding key IDs for removal
- Monitoring key distribution

---

### `/removeapikey <key_id>`
Permanently remove an API key from database.

**Usage:**
```
/removeapikey 6718a1b2c3d4e5f6g7h8i9j0
```

**Notes:**
- Get key ID from `/listapikeys`
- Only removes database keys
- Cannot remove environment key
- Immediately updates active clients

**Warning:** This is permanent! Use `/toggleapikey` to temporarily disable instead.

---

### `/toggleapikey <key_id>`
Enable or disable an API key without deleting it.

**Usage:**
```
/toggleapikey 6718a1b2c3d4e5f6g7h8i9j0
```

**Use cases:**
- Temporarily disable misbehaving key
- Preserve usage history
- Test with specific keys only
- Quick enable/disable for maintenance

**Better than removal because:**
- Keeps usage statistics
- Can re-enable later
- Preserves configuration

---

### `/apikeystats`
View detailed usage statistics for all API keys.

**Usage:**
```
/apikeystats
```

**Shows:**
- Total keys (active + inactive)
- Total API calls across all keys
- Per-key usage breakdown
- Last used timestamp
- Currently loaded clients
- Rotation method (round-robin)

**Use for:**
- Monitoring API usage
- Identifying overused keys
- Planning when to add more keys
- Debugging rate limit issues

---

## Content Management Commands

### `/quickscrape <url> <pages>`
Fast scraping without download links (listing only).

**Aliases:**
- `/quickscrapesoft <url> <pages>`
- `/quickscrapegame <url> <pages>`

**Usage:**
```
/quickscrape https://www.apunkagames.com/action-games-for-pc 3
```

**Features:**
- Extracts: name, category, size, version
- No download links (faster)
- Progress updates in real-time
- Duplicate detection

---

### `/fullscrape <url> <pages>`
Full scraping WITH download links (slower but complete).

**Aliases:**
- `/fullscrapesoft <url> <pages>`
- `/fullscrapegame <url> <pages>`

**Usage:**
```
/fullscrape https://www.apunkagames.com/shooting-games-for-pc 5
```

**Features:**
- Extracts: name, category, size, version, AND download links
- Visits each game page individually
- Finds and shortens download URLs
- Complete database entries

**Use:** Set pages to `0` for unlimited scraping!

---

### `/addsoft`
Manually add software/game to database.

**Usage:**
```
/addsoft <name> | <category> | <OS> | <size> | <version> | <description> | <link1> | <link2> | ...
```

**Example:**
```
/addsoft GTA San Andreas | Action | Windows | 4.5GB | 2014 | Classic action game | https://download.com/gta.zip
```

---

### `/stats`
View bot statistics and usage metrics.

**Shows:**
- Total users
- Total software/games
- Total downloads
- Popular items
- Recent activity

---

### `/dbinfo`
View database collection information.

**Shows:**
- Collection sizes
- Document counts
- Index information
- Storage usage

---

## Best Practices

### **API Key Management**

1. **Start with 2-3 keys minimum**
   ```
   /addapikey sk-key1...
   /addapikey sk-key2...
   /addapikey sk-key3...
   ```

2. **Monitor daily**
   ```
   /apikeystats
   /listapikeys
   ```

3. **Add more if needed**
   - Watch for high usage on single key
   - Add keys before hitting limits

4. **Use toggle, not remove**
   ```
   /toggleapikey <id>    # Good - preserves data
   /removeapikey <id>    # Only if key is compromised
   ```

### **Content Scraping**

1. **Quick scrape first** (test if site works)
   ```
   /quickscrape https://example.com 1
   ```

2. **Full scrape after confirmation**
   ```
   /fullscrape https://example.com 5
   ```

3. **Use unlimited for full categories**
   ```
   /fullscrape https://example.com/action-games 0
   ```

### **Monitoring**

**Daily checks:**
```
/apikeystats          # API key usage
/stats               # Bot usage
/listapikeys         # Key health
```

**Weekly:**
```
/dbinfo              # Database size
```

---

## Troubleshooting

### **Problem: All keys rate limited**

**Solution:**
```
/addapikey sk-new-key-here
```

---

### **Problem: Key not working**

**Check:**
1. `/listapikeys` - Is it active?
2. `/apikeystats` - Has it been used?
3. Try toggling:
   ```
   /toggleapikey <id>
   /toggleapikey <id>
   ```

---

### **Problem: Scraping fails**

**Try:**
1. Test with 1 page first
2. Check URL format
3. Use quick scrape to verify
4. Check bot console for errors

---

## Command Summary

```bash
# API Key Management
/addapikey <key>       # Add new API key
/listapikeys           # List all keys  
/removeapikey <id>     # Remove key
/toggleapikey <id>     # Enable/disable
/apikeystats           # Usage stats

# Content Scraping
/quickscrape <url> <pages>    # Fast (no links)
/fullscrape <url> <pages>     # Complete (with links)
/addsoft <fields>             # Manual add

# Monitoring
/stats                 # Bot statistics
/dbinfo               # Database info
```

---

**For detailed migration information, see:** `DEEPSEEK_MIGRATION_GUIDE.md`

**For complete features, see:** `FEATURE_SUMMARY.md`
