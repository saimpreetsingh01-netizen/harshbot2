# DeepSeek AI Migration Guide 🚀

## Overview
Successfully migrated from Groq AI to DeepSeek AI with **multiple API key support** and automatic rate limit handling!

## What Changed

### ✅ **From Groq to DeepSeek**
- **Old**: Groq API with llama-3.3-70b-versatile model
- **New**: DeepSeek API with deepseek-chat model
- **SDK**: Using OpenAI-compatible Python SDK
- **Benefits**:
  - Better rate limits
  - More stable API
  - Multiple API key support
  - Automatic failover

### 🔑 **Multiple API Key System** (NEW!)
Your bot now supports **unlimited API keys** with:
- ✅ Round-robin load balancing
- ✅ Automatic rate limit detection
- ✅ Instant failover to next key
- ✅ Per-key usage tracking
- ✅ Easy admin management

---

## How It Works

### **API Key Loading**

The bot loads API keys from two sources:

1. **Environment Variable** (Primary)
   - Variable: `DEEPSEEK_API`
   - Priority: Always loaded first
   - Source: Replit Secrets

2. **Database** (Additional Keys)
   - Collection: `api_keys`
   - Added by admins via commands
   - Can add unlimited keys

### **Load Balancing**

```
Request 1 → API Key #1
Request 2 → API Key #2
Request 3 → API Key #3
Request 4 → API Key #1 (cycles back)
```

### **Rate Limit Handling**

```
1. Try API Key #1
   ↓ (Rate limited!)
2. Try API Key #2
   ↓ (Success!)
3. Return result
```

Maximum 3 attempts per search, cycling through available keys.

---

## Admin Commands

### 📝 **Add New API Key**
```
/addapikey <your_deepseek_api_key>
```

**Example:**
```
/addapikey sk-abc123xyz456def789...
```

**Response:**
```
✅ API Key Added Successfully!

🔑 Key: sk-abc123...789
👤 Added by: Admin Name
📅 Date: 2025-10-24 15:30
🔢 ID: 6718a1b2c3d4e5f6g7h8i9j0

🔄 Total active keys: 2

💡 The bot will now use this key in rotation!
```

### 📋 **List All API Keys**
```
/listapikeys
```

**Response:**
```
🔑 DeepSeek API Keys

📌 Environment Key:
└ sk-env123...456
  Status: 🟢 Active (Primary)

💾 Database Keys (2):

1. sk-abc123...789
   Status: 🟢 Active
   Added by: 123456789
   Usage: 45 times
   ID: 6718a1b2c3d4e5f6g7h8i9j0

2. sk-def456...012
   Status: 🔴 Inactive
   Added by: 987654321
   Usage: 12 times
   ID: 6718a2b3c4d5e6f7g8h9i0j1

📊 Current Status:
└ Active clients: 2
└ Load balancing: ✅ Enabled
```

### ❌ **Remove API Key**
```
/removeapikey <key_id>
```

**Example:**
```
/removeapikey 6718a1b2c3d4e5f6g7h8i9j0
```

### 🔄 **Toggle API Key (Enable/Disable)**
```
/toggleapikey <key_id>
```

**Example:**
```
/toggleapikey 6718a1b2c3d4e5f6g7h8i9j0
```

This temporarily disables a key without deleting it.

### 📊 **View API Key Statistics**
```
/apikeystats
```

**Response:**
```
📊 API Key Statistics

Overview:
└ Total keys: 3
└ Active keys: 2
└ Total API calls: 157

Per Key Usage:

1. 🟢 sk-abc123...
   Calls: 82
   Last used: 2025-10-24 15:45:23

2. 🟢 sk-def456...
   Calls: 75
   Last used: 2025-10-24 15:44:18

3. 🔴 sk-ghi789...
   Calls: 0
   Last used: Never

🔄 Currently Loaded:
└ Active clients: 2
└ Rotation: Round-robin
```

---

## Setup Instructions

### **Step 1: Get DeepSeek API Key**

1. Visit https://platform.deepseek.com
2. Create account or log in
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `sk-`)

### **Step 2: Add Primary Key (Environment)**

Your first key is already added as `DEEPSEEK_API` in Replit Secrets! ✅

### **Step 3: Add Additional Keys (Optional)**

For better rate limit handling, add more keys:

```
/addapikey sk-your-second-key-here
/addapikey sk-your-third-key-here
```

**Recommended**: 2-3 API keys for production use.

---

## Technical Details

### **Database Schema**

New collection: `api_keys`

```json
{
  "_id": ObjectId("..."),
  "service": "deepseek",
  "api_key": "sk-abc123...",
  "added_by": 123456789,
  "added_at": "2025-10-24T15:30:00",
  "active": true,
  "usage_count": 45,
  "last_used": "2025-10-24T15:45:23"
}
```

### **API Configuration**

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-key-here",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.3,
    max_tokens=500
)
```

### **Models Used**

- **deepseek-chat**: Standard chat model (used for AI search)
- **Temperature**: 0.3 (focused, deterministic responses)
- **Max tokens**: 500 (sufficient for search results)

---

## Migration Changes

### **Files Modified**

1. **services/ai_service.py**
   - Replaced Groq with OpenAI SDK
   - Added `init_deepseek()` function
   - Added `get_next_deepseek_client()` for rotation
   - Enhanced `ai_search_software()` with rate limit handling

2. **utils/database.py**
   - Added `api_keys_collection`
   - Created index for service + api_key

3. **handlers/api_key_commands.py** (NEW!)
   - Created 5 admin commands for key management
   - Full CRUD operations on API keys

4. **main.py**
   - Updated imports (Groq → DeepSeek)
   - Added API key command handlers
   - Initialize DeepSeek with database collection

5. **requirements.txt**
   - Removed: `groq==0.33.0`
   - Added: `openai==1.59.5`

---

## Benefits of Migration

### **1. Better Rate Limits**
- DeepSeek: More generous limits
- Multiple keys: Effectively unlimited requests
- Automatic failover: No downtime

### **2. Cost Efficiency**
- DeepSeek: Competitive pricing
- Load balancing: Distribute usage evenly
- Tracking: Monitor per-key usage

### **3. Reliability**
- Multiple keys: Redundancy built-in
- Auto-retry: Transparent to users
- Database backup: Keys survive restarts

### **4. Scalability**
- Add keys on-demand
- No code changes needed
- Instant activation

---

## Usage Examples

### **For Users (No Changes!)**

Users won't notice any difference:

```
/aisearch GTA San Andreas
```

Works exactly the same, but now:
- ✅ Uses DeepSeek AI
- ✅ Auto-rotates between keys
- ✅ Never hits rate limits (with multiple keys)

### **For Admins**

**Start of day:**
```
/listapikeys           # Check current keys
/apikeystats          # Check usage
```

**If rate limits occur:**
```
/addapikey sk-new-key-here    # Add another key
```

**End of day:**
```
/apikeystats          # Review usage statistics
```

---

## Troubleshooting

### **Problem: "No DeepSeek API clients available"**

**Solution:**
1. Check environment variable: `DEEPSEEK_API` is set
2. Add database keys: `/addapikey <key>`
3. Check active keys: `/listapikeys`

### **Problem: "Rate limit hit on all keys"**

**Solution:**
1. Add more API keys: `/addapikey <new_key>`
2. Wait a few minutes for limits to reset
3. Check usage: `/apikeystats`

### **Problem: "API key invalid"**

**Solution:**
1. Verify key starts with `sk-`
2. Check key is active on DeepSeek platform
3. Remove and re-add: `/removeapikey <id>` then `/addapikey <key>`

---

## Best Practices

### **For Optimal Performance:**

1. **Use 2-3 API keys minimum**
   - Distributes load
   - Provides redundancy
   - Handles rate limits

2. **Monitor usage regularly**
   - Check `/apikeystats` daily
   - Watch for uneven distribution
   - Add keys if usage is high

3. **Keep environment key as primary**
   - Most reliable
   - Always available
   - Database keys are bonus

4. **Disable unused keys**
   - Use `/toggleapikey` instead of removing
   - Can re-enable later
   - Preserves usage history

---

## Summary

✅ **Migrated from Groq to DeepSeek**
✅ **Added multiple API key support**
✅ **Implemented automatic load balancing**
✅ **Created 5 admin management commands**
✅ **Added rate limit auto-retry**
✅ **Usage tracking per key**
✅ **Zero downtime migration**

**Your bot is now more reliable, scalable, and cost-effective!** 🎉

---

## Quick Reference

```bash
# API Key Management Commands
/addapikey <key>      # Add new API key
/listapikeys          # List all keys
/removeapikey <id>    # Remove a key
/toggleapikey <id>    # Enable/disable key
/apikeystats          # View usage stats
```

**Get DeepSeek API Keys:** https://platform.deepseek.com/api_keys
