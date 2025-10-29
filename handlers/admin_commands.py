from telegram import Update
from telegram.ext import ContextTypes
import os
from datetime import datetime, date
import logging
import utils.database as db
from services.scraper import scrape_software_info
from services.quick_scraper import quick_scrape_multiple_pages
from services.full_scraper import full_scrape_with_details
from services.movie_scraper import scrape_and_save_movies, get_available_categories

def get_admin_ids():
    admin_id = os.getenv('ADMIN_ID', '')
    if admin_id:
        return [int(admin_id)]
    admin_ids = os.getenv('ADMIN_IDS', '')
    if admin_ids:
        return [int(id) for id in admin_ids.split(',') if id.strip()]
    return []

def is_admin(user_id):
    return user_id in get_admin_ids()

async def addsoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Usage:**\n"
            "`/addsoft <name> | <category> | <OS> | <size> | <version> | <description> | <download_link1> | <link2> | ...`\n\n"
            "**Example:**\n"
            "`/addsoft VLC Player | Video | Windows,Mac,Linux | 50MB | 3.0.18 | Best media player | https://download.com/vlc.exe | https://mirror.com/vlc.exe`",
            parse_mode='Markdown'
        )
        return
    
    parts = ' '.join(context.args).split('|')
    
    if len(parts) < 7:
        await update.message.reply_text("❌ Please provide all required fields separated by |")
        return
    
    software = {
        "name": parts[0].strip(),
        "category": parts[1].strip(),
        "os": [os.strip() for os in parts[2].split(',')],
        "file_size": parts[3].strip(),
        "version": parts[4].strip(),
        "description": parts[5].strip(),
        "download_links": [{"url": link.strip(), "type": "primary"} for link in parts[6:]],
        "downloads_count": 0,
        "average_rating": 0,
        "reviews_count": 0,
        "date_added": datetime.now().isoformat(),
        "added_by": update.effective_user.id
    }
    
    result = db.software_collection.insert_one(software)
    
    await update.message.reply_text(
        f"✅ **Software Added Successfully!**\n\n"
        f"**Name:** {software['name']}\n"
        f"**Category:** {software['category']}\n"
        f"**Links:** {len(software['download_links'])}\n"
        f"**ID:** `{str(result.inserted_id)}`",
        parse_mode='Markdown'
    )

async def quickadd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Quick Add Usage:**\n"
            "`/quickadd <name>,<category>,<OS>,<size>,<version>`\n\n"
            "**Example:**\n"
            "`/quickadd Chrome,Browser,Windows,100MB,120.0`",
            parse_mode='Markdown'
        )
        return
    
    parts = ','.join(context.args).split(',')
    
    if len(parts) < 5:
        await update.message.reply_text("❌ Please provide: name,category,OS,size,version")
        return
    
    software = {
        "name": parts[0].strip(),
        "category": parts[1].strip(),
        "os": parts[2].strip().split('/'),
        "file_size": parts[3].strip(),
        "version": parts[4].strip(),
        "description": f"{parts[0].strip()} - {parts[1].strip()} software",
        "download_links": [],
        "downloads_count": 0,
        "average_rating": 0,
        "reviews_count": 0,
        "date_added": datetime.now().isoformat(),
        "added_by": update.effective_user.id
    }
    
    result = db.software_collection.insert_one(software)
    
    await update.message.reply_text(
        f"✅ **Software Added!**\n\n"
        f"Use `/addlink {str(result.inserted_id)} <download_url>` to add download links.",
        parse_mode='Markdown'
    )

async def addsite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Scrape Website Usage:**\n"
            "`/addsite <website_url>`\n\n"
            "This will automatically scrape download links from the page.",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    await update.message.reply_text("🔍 Scraping website... Please wait...")
    
    info = scrape_software_info(url)
    
    if not info or not info['download_links']:
        await update.message.reply_text("❌ No download links found on this page.")
        return
    
    links_msg = f"✅ **Found {len(info['download_links'])} download links:**\n\n"
    for i, link in enumerate(info['download_links'][:5], 1):
        links_msg += f"{i}. {link[:60]}...\n"
    
    links_msg += f"\n💡 Use `/quickadd` with this data and then `/addlink <id> <url>` to add links."
    
    await update.message.reply_text(links_msg, parse_mode='Markdown')

async def addlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 **Add Link Usage:**\n"
            "`/addlink <software_id> <download_url>`",
            parse_mode='Markdown'
        )
        return
    
    from bson import ObjectId
    
    software_id = context.args[0]
    download_url = context.args[1]
    
    try:
        db.software_collection.update_one(
            {"_id": ObjectId(software_id)},
            {"$push": {"download_links": {"url": download_url, "type": "mirror"}}}
        )
        
        await update.message.reply_text("✅ Download link added successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    total_software = db.software_collection.count_documents({})
    total_downloads = db.downloads_collection.count_documents({})
    
    today_str = date.today().isoformat()
    today_downloads = db.downloads_collection.count_documents({
        "timestamp": {"$regex": f"^{today_str}"}
    })
    
    top_software = list(db.software_collection.find().sort("downloads_count", -1).limit(5))
    
    stats_msg = "📊 **Bot Statistics**\n\n"
    stats_msg += f"📦 Total Software: **{total_software:,}**\n"
    stats_msg += f"⬇️ Total Downloads: **{total_downloads:,}**\n"
    stats_msg += f"📅 Today's Downloads: **{today_downloads:,}**\n\n"
    
    stats_msg += "🔥 **Top 5 Software:**\n"
    for i, soft in enumerate(top_software, 1):
        stats_msg += f"{i}. {soft['name']} - {soft['downloads_count']:,} downloads\n"
    
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def earnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    total_downloads = db.downloads_collection.count_documents({})
    
    url2cash_downloads = 0
    adrinolinks_downloads = 0
    cached_downloads = 0
    
    all_downloads = db.downloads_collection.find({})
    
    for download in all_downloads:
        services = download.get('shorteners_used', [])
        for service in services:
            if service == 'url2cash':
                url2cash_downloads += 1
            elif service == 'adrinolinks':
                adrinolinks_downloads += 1
            elif service == 'cached':
                cached_downloads += 1
    
    url2cash_cpm = 4.0
    adrinolinks_cpm = 5.0
    
    url2cash_earnings = (url2cash_downloads / 1000) * url2cash_cpm
    adrinolinks_earnings = (adrinolinks_downloads / 1000) * adrinolinks_cpm
    total_estimated = url2cash_earnings + adrinolinks_earnings
    
    today_str = date.today().isoformat()
    today_downloads = db.downloads_collection.count_documents({
        "timestamp": {"$regex": f"^{today_str}"}
    })
    
    dashboard_msg = "💰 **EARNINGS DASHBOARD**\n\n"
    dashboard_msg += "📊 **Overview:**\n"
    dashboard_msg += f"• Total Downloads: **{total_downloads:,}**\n"
    dashboard_msg += f"• Today's Downloads: **{today_downloads:,}**\n"
    dashboard_msg += f"• Cached (No API call): {cached_downloads:,}\n\n"
    
    dashboard_msg += f"💵 **Estimated Total Earnings: ${total_estimated:.2f}**\n\n"
    
    dashboard_msg += "📈 **Breakdown by Shortener:**\n\n"
    
    dashboard_msg += f"💰 **URL2cash.in**\n"
    dashboard_msg += f"   • Clicks: {url2cash_downloads:,}\n"
    dashboard_msg += f"   • Est. Earnings: ${url2cash_earnings:.2f}\n"
    dashboard_msg += f"   • CPM Rate: ${url2cash_cpm}\n\n"
    
    dashboard_msg += f"💵 **AdrinoLinks.in**\n"
    dashboard_msg += f"   • Clicks: {adrinolinks_downloads:,}\n"
    dashboard_msg += f"   • Est. Earnings: ${adrinolinks_earnings:.2f}\n"
    dashboard_msg += f"   • CPM Rate: ${adrinolinks_cpm}\n\n"
    
    dashboard_msg += "💡 **Check Actual Earnings:**\n"
    dashboard_msg += "• URL2cash Dashboard: url2cash.in/dashboard\n"
    dashboard_msg += "• AdrinoLinks Dashboard: adrinolinks.in/dashboard\n\n"
    
    dashboard_msg += "⚡ **Tip:** Promote your bot to increase downloads and earnings!"
    
    await update.message.reply_text(dashboard_msg, parse_mode='Markdown')

async def scrapesoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Scrape Software Usage:**\n"
            "`/scrapesoft <url> page <number>`\n"
            "`/scrapesoft <url> page <number> category <category_name>`\n\n"
            "**Examples:**\n"
            "`/scrapesoft https://www.cracksoft.xyz/ page 5`\n"
            "`/scrapesoft https://bestcracksoftwares.com/category/multimedia/ page 3 category Multimedia`\n\n"
            "💡 Use the 'category' parameter to manually set category for all scraped items!",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/scrapesoft <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 1 or max_pages > 10:
            await update.message.reply_text("❌ Page number must be between 1 and 10 (to save resources)")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual override)\n" if custom_category else ""
    
    await update.message.reply_text(
        f"🚀 **Starting Smart Scraping**\n\n"
        f"🌐 Target: {url}\n"
        f"📄 Pages: {max_pages}\n"
        f"{category_msg}\n"
        f"📋 Phase 1: Scraping raw data...\n"
        f"🤖 Phase 2: AI will organize & categorize...\n\n"
        f"⏱️ This may take a few minutes...",
        parse_mode='Markdown'
    )
    
    try:
        from services.advanced_scraper import scrape_multiple_pages
        
        items_list, error = scrape_multiple_pages(url, "any", max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found or scraping failed. Check the URL and try again.")
            return
        
        added_games = 0
        added_software = 0
        duplicate_count = 0
        error_count = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                is_game = item_data.get('type', '').lower() == 'game'
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'N/A'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:200],
                    "os": ["Windows"],
                    "download_links": [{"url": link, "type": "scraped"} for link in item_data.get('download_links', [])[:3]],
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": is_game
                }
                
                db.software_collection.insert_one(item_doc)
                
                if is_game:
                    added_games += 1
                else:
                    added_software += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        category_note = f"📂 **All items set to category:** {custom_category}\n" if custom_category else "🤖 AI automatically categorized everything!\n"
        
        result_msg = f"✅ **Scraping Complete!**\n\n"
        result_msg += f"🎮 **Games added:** {added_games}\n"
        result_msg += f"💻 **Software added:** {added_software}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += category_note
        result_msg += f"💾 Database updated successfully!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Scraping error: {str(e)}")

async def scrapegame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Scrape Games Usage:**\n"
            "`/scrapegame <url> page <number>`\n"
            "`/scrapegame <url> page <number> category <category_name>`\n\n"
            "**Examples:**\n"
            "`/scrapegame https://apunkagames.net.pk/ page 5`\n"
            "`/scrapegame https://www.apunkagames.com/action-games-for-pc page 3 category Action Games`\n\n"
            "💡 Use the 'category' parameter to manually set category for all scraped games!",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/scrapegame <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 1 or max_pages > 10:
            await update.message.reply_text("❌ Page number must be between 1 and 10 (to save resources)")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual override)\n" if custom_category else ""
    
    await update.message.reply_text(
        f"🚀 **Starting Smart Scraping**\n\n"
        f"🌐 Target: {url}\n"
        f"📄 Pages: {max_pages}\n"
        f"{category_msg}\n"
        f"📋 Phase 1: Scraping raw data...\n"
        f"🤖 Phase 2: AI will organize & categorize...\n\n"
        f"⏱️ This may take a few minutes...",
        parse_mode='Markdown'
    )
    
    try:
        from services.advanced_scraper import scrape_multiple_pages
        
        items_list, error = scrape_multiple_pages(url, "any", max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found or scraping failed. Check the URL and try again.")
            return
        
        added_games = 0
        added_software = 0
        duplicate_count = 0
        error_count = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                is_game = item_data.get('type', '').lower() == 'game'
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'N/A'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:200],
                    "os": ["Windows"],
                    "download_links": [{"url": link, "type": "scraped"} for link in item_data.get('download_links', [])[:3]],
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": is_game
                }
                
                db.software_collection.insert_one(item_doc)
                
                if is_game:
                    added_games += 1
                else:
                    added_software += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        category_note = f"📂 **All items set to category:** {custom_category}\n" if custom_category else "🤖 AI automatically categorized everything!\n"
        
        result_msg = f"✅ **Scraping Complete!**\n\n"
        result_msg += f"🎮 **Games added:** {added_games}\n"
        result_msg += f"💻 **Software added:** {added_software}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += category_note
        result_msg += f"💾 Database updated successfully!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Game scraping error: {str(e)}")

async def deletesoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a software entry from the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Delete Software Usage:**\n"
            "`/deletesoft <software_id>`\n\n"
            "**Example:**\n"
            "`/deletesoft 507f1f77bcf86cd799439011`",
            parse_mode='Markdown'
        )
        return
    
    from bson import ObjectId
    
    software_id = context.args[0]
    
    try:
        software = db.software_collection.find_one({"_id": ObjectId(software_id)})
        
        if not software:
            await update.message.reply_text("❌ Software not found!")
            return
        
        result = db.software_collection.delete_one({"_id": ObjectId(software_id)})
        
        if result.deleted_count > 0:
            await update.message.reply_text(
                f"✅ **Software Deleted!**\n\n"
                f"**Name:** {software['name']}\n"
                f"**Category:** {software.get('category', 'N/A')}\n"
                f"**Downloads:** {software.get('downloads_count', 0)}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to delete software!")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def editsoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit software details"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Edit Software Usage:**\n"
            "`/editsoft <software_id> <field> <new_value>`\n\n"
            "**Available fields:**\n"
            "• name\n"
            "• category\n"
            "• version\n"
            "• file_size\n"
            "• description\n\n"
            "**Example:**\n"
            "`/editsoft 507f1f77bcf86cd799439011 name VLC Media Player`\n"
            "`/editsoft 507f1f77bcf86cd799439011 version 3.0.20`",
            parse_mode='Markdown'
        )
        return
    
    from bson import ObjectId
    
    software_id = context.args[0]
    field = context.args[1].lower()
    new_value = ' '.join(context.args[2:])
    
    allowed_fields = ['name', 'category', 'version', 'file_size', 'description']
    
    if field not in allowed_fields:
        await update.message.reply_text(f"❌ Invalid field! Allowed fields: {', '.join(allowed_fields)}")
        return
    
    try:
        software = db.software_collection.find_one({"_id": ObjectId(software_id)})
        
        if not software:
            await update.message.reply_text("❌ Software not found!")
            return
        
        old_value = software.get(field, 'N/A')
        
        result = db.software_collection.update_one(
            {"_id": ObjectId(software_id)},
            {"$set": {field: new_value}}
        )
        
        if result.modified_count > 0:
            await update.message.reply_text(
                f"✅ **Software Updated!**\n\n"
                f"**Name:** {software['name']}\n"
                f"**Field:** {field}\n"
                f"**Old Value:** {old_value}\n"
                f"**New Value:** {new_value}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ No changes made!")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def dbinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show database information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    try:
        software_count = db.software_collection.count_documents({})
        users_count = db.users_collection.count_documents({})
        downloads_count = db.downloads_collection.count_documents({})
        reviews_count = db.reviews_collection.count_documents({})
        cache_count = db.url_cache_collection.count_documents({})
        
        games_count = db.software_collection.count_documents({"is_game": True})
        software_only_count = db.software_collection.count_documents({"is_game": {"$ne": True}})
        
        categories = db.software_collection.distinct("category")
        
        db_size_msg = "🗄️ **DATABASE INFORMATION**\n\n"
        db_size_msg += "📊 **Collections:**\n"
        db_size_msg += f"• Software: **{software_count:,}** entries\n"
        db_size_msg += f"  └ Games: **{games_count:,}**\n"
        db_size_msg += f"  └ Software: **{software_only_count:,}**\n"
        db_size_msg += f"• Users: **{users_count:,}**\n"
        db_size_msg += f"• Downloads: **{downloads_count:,}**\n"
        db_size_msg += f"• Reviews: **{reviews_count:,}**\n"
        db_size_msg += f"• URL Cache: **{cache_count:,}**\n\n"
        db_size_msg += f"📂 **Categories:** {len(categories)}\n"
        db_size_msg += f"• {', '.join(categories[:10])}"
        
        if len(categories) > 10:
            db_size_msg += f"\n  ... and {len(categories) - 10} more"
        
        await update.message.reply_text(db_size_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cleardownloads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear download history"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args or context.args[0].lower() != 'confirm':
        downloads_count = db.downloads_collection.count_documents({})
        await update.message.reply_text(
            f"⚠️ **WARNING: Clear Downloads**\n\n"
            f"This will delete **{downloads_count:,}** download records!\n\n"
            f"To confirm, use:\n"
            f"`/cleardownloads confirm`",
            parse_mode='Markdown'
        )
        return
    
    try:
        downloads_count = db.downloads_collection.count_documents({})
        result = db.downloads_collection.delete_many({})
        
        db.users_collection.update_many(
            {},
            {"$set": {"downloads": [], "total_downloads": 0}}
        )
        
        db.software_collection.update_many(
            {},
            {"$set": {"downloads_count": 0}}
        )
        
        await update.message.reply_text(
            f"✅ **Downloads Cleared!**\n\n"
            f"Deleted **{result.deleted_count:,}** download records\n"
            f"Reset all download counters",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def resetdb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Complete database reset"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args or context.args[0].lower() != 'confirm':
        software_count = db.software_collection.count_documents({})
        users_count = db.users_collection.count_documents({})
        downloads_count = db.downloads_collection.count_documents({})
        reviews_count = db.reviews_collection.count_documents({})
        
        await update.message.reply_text(
            f"🚨 **DANGER: COMPLETE DATABASE RESET**\n\n"
            f"This will **PERMANENTLY DELETE**:\n"
            f"• {software_count:,} software entries\n"
            f"• {users_count:,} users\n"
            f"• {downloads_count:,} downloads\n"
            f"• {reviews_count:,} reviews\n"
            f"• All URL cache\n\n"
            f"⚠️ **THIS CANNOT BE UNDONE!**\n\n"
            f"To confirm, use:\n"
            f"`/resetdb confirm`",
            parse_mode='Markdown'
        )
        return
    
    try:
        software_deleted = db.software_collection.delete_many({})
        users_deleted = db.users_collection.delete_many({})
        downloads_deleted = db.downloads_collection.delete_many({})
        reviews_deleted = db.reviews_collection.delete_many({})
        cache_deleted = db.url_cache_collection.delete_many({})
        
        result_msg = "✅ **DATABASE RESET COMPLETE!**\n\n"
        result_msg += f"Deleted:\n"
        result_msg += f"• Software: {software_deleted.deleted_count:,}\n"
        result_msg += f"• Users: {users_deleted.deleted_count:,}\n"
        result_msg += f"• Downloads: {downloads_deleted.deleted_count:,}\n"
        result_msg += f"• Reviews: {reviews_deleted.deleted_count:,}\n"
        result_msg += f"• Cache: {cache_deleted.deleted_count:,}\n\n"
        result_msg += "🔄 Database is now empty and ready for fresh data!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def quickscrapesoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick scrape software WITHOUT using AI - avoids rate limits"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Quick Scrape Software (NO AI)**\n\n"
            "`/quickscrapesoft <url> page <number>`\n"
            "`/quickscrapesoft <url> page <number> category <name>`\n"
            "`/quickscrapesoft <url> page 0` - **UNLIMITED PAGES!**\n\n"
            "**Examples:**\n"
            "`/quickscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 10`\n"
            "`/quickscrapesoft https://bestcracksoftwares.com/category/audio-plugin-tool/ page 0` ← unlimited!\n"
            "`/quickscrapesoft https://example.com/multimedia/ page 5 category Multimedia`\n\n"
            "⚡ **FAST & NO LIMITS** - Set page to 0 for unlimited scraping!\n"
            "📂 Category is auto-detected from URL or specify manually.",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/quickscrapesoft <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 0:
            await update.message.reply_text("❌ Page number must be 0 (unlimited) or positive number")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer (use 0 for unlimited)")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual)\n" if custom_category else "📂 Category will be auto-detected from URL\n"
    pages_msg = "📄 **UNLIMITED PAGES** - will scrape until no items found!" if max_pages == 0 else f"📄 Pages: {max_pages}"
    
    await update.message.reply_text(
        f"🚀 **Quick Scraping (NO AI)**\n\n"
        f"🌐 Target: {url}\n"
        f"{pages_msg}\n"
        f"{category_msg}\n"
        f"⚡ Fast mode - no AI, no rate limits!\n"
        f"⏱️ Starting now...",
        parse_mode='Markdown'
    )
    
    try:
        items_list, error = quick_scrape_multiple_pages(url, max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found. Check the URL and try again.")
            return
        
        added_count = 0
        duplicate_count = 0
        error_count = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'Latest'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:200],
                    "os": ["Windows"],
                    "download_links": [{"url": link, "type": "scraped"} for link in item_data.get('download_links', [])[:3]],
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": False
                }
                
                db.software_collection.insert_one(item_doc)
                added_count += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        result_msg = f"✅ **Quick Scraping Complete!**\n\n"
        result_msg += f"💻 **Software added:** {added_count}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += f"⚡ **No AI used** - no rate limits hit!\n"
        result_msg += f"💾 Database updated successfully!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Quick scraping error: {str(e)}")

async def quickscrapegame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick scrape games WITHOUT using AI - avoids rate limits"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Quick Scrape Games (NO AI)**\n\n"
            "`/quickscrapegame <url> page <number>`\n"
            "`/quickscrapegame <url> page <number> category <name>`\n"
            "`/quickscrapegame <url> page 0` - **UNLIMITED PAGES!**\n\n"
            "**Examples:**\n"
            "`/quickscrapegame https://www.apunkagames.com/action-games-for-pc page 10`\n"
            "`/quickscrapegame https://www.apunkagames.com/racing-games page 0` ← unlimited!\n"
            "`/quickscrapegame https://example.com/rpg/ page 5 category RPG Games`\n\n"
            "⚡ **FAST & NO LIMITS** - Set page to 0 for unlimited scraping!\n"
            "📂 Category is auto-detected from URL or specify manually.",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/quickscrapegame <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 0:
            await update.message.reply_text("❌ Page number must be 0 (unlimited) or positive number")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer (use 0 for unlimited)")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual)\n" if custom_category else "📂 Category will be auto-detected from URL\n"
    pages_msg = "📄 **UNLIMITED PAGES** - will scrape until no items found!" if max_pages == 0 else f"📄 Pages: {max_pages}"
    
    await update.message.reply_text(
        f"🚀 **Quick Scraping Games (NO AI)**\n\n"
        f"🌐 Target: {url}\n"
        f"{pages_msg}\n"
        f"{category_msg}\n"
        f"⚡ Fast mode - no AI, no rate limits!\n"
        f"⏱️ Starting now...",
        parse_mode='Markdown'
    )
    
    try:
        items_list, error = quick_scrape_multiple_pages(url, max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found. Check the URL and try again.")
            return
        
        added_count = 0
        duplicate_count = 0
        error_count = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'Latest'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:200],
                    "os": ["Windows"],
                    "download_links": [{"url": link, "type": "scraped"} for link in item_data.get('download_links', [])[:3]],
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": True
                }
                
                db.software_collection.insert_one(item_doc)
                added_count += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        result_msg = f"✅ **Quick Scraping Complete!**\n\n"
        result_msg += f"🎮 **Games added:** {added_count}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += f"⚡ **No AI used** - no rate limits hit!\n"
        result_msg += f"💾 Database updated successfully!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Quick game scraping error: {str(e)}")

async def fullscrapesoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full scrape software WITH download links - visits each page individually"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Full Scrape Software (With Download Links)**\n\n"
            "`/fullscrapesoft <url> page <number>`\n"
            "`/fullscrapesoft <url> page <number> category <name>`\n"
            "`/fullscrapesoft <url> page 0` - **UNLIMITED!**\n\n"
            "**Examples:**\n"
            "`/fullscrapesoft https://bestcracksoftwares.com/category/3d-tools/ page 5`\n"
            "`/fullscrapesoft https://bestcracksoftwares.com/category/audio-plugin-tool/ page 0`\n\n"
            "⚠️ **This is SLOWER** (2-3s per item) but gets:\n"
            "• Download links from each page\n"
            "• Complete descriptions\n"
            "• File sizes & versions\n\n"
            "💡 Use `/quickscrapesoft` for fast scraping without download links.",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/fullscrapesoft <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 0:
            await update.message.reply_text("❌ Page number must be 0 (unlimited) or positive number")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer (use 0 for unlimited)")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual)\n" if custom_category else "📂 Category will be auto-detected\n"
    pages_msg = "📄 **UNLIMITED PAGES**" if max_pages == 0 else f"📄 Pages: {max_pages}"
    
    await update.message.reply_text(
        f"🚀 **Full Scraping (With Download Links)**\n\n"
        f"🌐 Target: {url}\n"
        f"{pages_msg}\n"
        f"{category_msg}\n"
        f"⏱️ This will take 2-3 seconds per item...\n"
        f"☕ Please wait, fetching complete details...",
        parse_mode='Markdown'
    )
    
    try:
        items_list, error = full_scrape_with_details(url, max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found. Check the URL and try again.")
            return
        
        added_count = 0
        duplicate_count = 0
        error_count = 0
        links_found = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                download_links_data = [{"url": link, "type": "direct"} for link in item_data.get('download_links', [])[:5]]
                if download_links_data:
                    links_found += len(download_links_data)
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'Latest'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:500],
                    "os": ["Windows"],
                    "download_links": download_links_data,
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": False
                }
                
                db.software_collection.insert_one(item_doc)
                added_count += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        result_msg = f"✅ **Full Scraping Complete!**\n\n"
        result_msg += f"💻 **Software added:** {added_count}\n"
        result_msg += f"🔗 **Download links found:** {links_found}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += f"💾 Database updated with complete information!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Full scraping error: {str(e)}")

async def fullscrapegame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full scrape games WITH download links - visits each page individually"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Full Scrape Games (With Download Links)**\n\n"
            "`/fullscrapegame <url> page <number>`\n"
            "`/fullscrapegame <url> page <number> category <name>`\n"
            "`/fullscrapegame <url> page 0` - **UNLIMITED!**\n\n"
            "**Examples:**\n"
            "`/fullscrapegame https://www.apunkagames.com/action-games-for-pc page 5`\n"
            "`/fullscrapegame https://www.apunkagames.com/fighting-games-for-pc page 0`\n\n"
            "⚠️ **This is SLOWER** (2-3s per item) but gets:\n"
            "• Download links from each page\n"
            "• Complete descriptions\n"
            "• File sizes & versions\n\n"
            "💡 Use `/quickscrapegame` for fast scraping without download links.",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    if context.args[1].lower() != 'page':
        await update.message.reply_text("❌ Invalid format. Use: `/fullscrapegame <url> page <number>`", parse_mode='Markdown')
        return
    
    try:
        max_pages = int(context.args[2])
        if max_pages < 0:
            await update.message.reply_text("❌ Page number must be 0 (unlimited) or positive number")
            return
    except ValueError:
        await update.message.reply_text("❌ Page number must be a valid integer (use 0 for unlimited)")
        return
    
    custom_category = None
    if len(context.args) >= 5 and context.args[3].lower() == 'category':
        custom_category = ' '.join(context.args[4:])
    
    category_msg = f"📂 Category: **{custom_category}** (manual)\n" if custom_category else "📂 Category will be auto-detected\n"
    pages_msg = "📄 **UNLIMITED PAGES**" if max_pages == 0 else f"📄 Pages: {max_pages}"
    
    await update.message.reply_text(
        f"🚀 **Full Scraping Games (With Download Links)**\n\n"
        f"🌐 Target: {url}\n"
        f"{pages_msg}\n"
        f"{category_msg}\n"
        f"⏱️ This will take 2-3 seconds per game...\n"
        f"☕ Please wait, fetching complete details...",
        parse_mode='Markdown'
    )
    
    try:
        items_list, error = full_scrape_with_details(url, max_pages, custom_category)
        
        if error:
            await update.message.reply_text(f"❌ **Scraping Error:**\n{error}", parse_mode='Markdown')
            return
        
        if not items_list:
            await update.message.reply_text("❌ No items found. Check the URL and try again.")
            return
        
        added_count = 0
        duplicate_count = 0
        error_count = 0
        links_found = 0
        
        for item_data in items_list:
            try:
                existing = db.software_collection.find_one({"name": item_data['name']})
                
                if existing:
                    duplicate_count += 1
                    continue
                
                download_links_data = [{"url": link, "type": "direct"} for link in item_data.get('download_links', [])[:5]]
                if download_links_data:
                    links_found += len(download_links_data)
                
                item_doc = {
                    "name": item_data.get('name', 'Unknown'),
                    "version": item_data.get('version', 'Latest'),
                    "category": item_data.get('category', 'Uncategorized'),
                    "file_size": item_data.get('file_size', 'Unknown'),
                    "description": item_data.get('description', '')[:500],
                    "os": ["Windows"],
                    "download_links": download_links_data,
                    "downloads_count": 0,
                    "average_rating": 0,
                    "reviews_count": 0,
                    "date_added": datetime.now().isoformat(),
                    "added_by": update.effective_user.id,
                    "source_url": item_data.get('source_url', url),
                    "scraped": True,
                    "is_game": True
                }
                
                db.software_collection.insert_one(item_doc)
                added_count += 1
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error adding item: {str(e)}")
        
        result_msg = f"✅ **Full Scraping Complete!**\n\n"
        result_msg += f"🎮 **Games added:** {added_count}\n"
        result_msg += f"🔗 **Download links found:** {links_found}\n"
        result_msg += f"⊗ **Duplicates skipped:** {duplicate_count}\n"
        
        if error_count > 0:
            result_msg += f"⚠️ **Errors:** {error_count}\n"
        
        result_msg += f"\n📊 Total processed: {len(items_list)}\n"
        result_msg += f"💾 Database updated with complete information!"
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Scraping failed:** {str(e)}")
        logging.error(f"Full game scraping error: {str(e)}")

# NFT Management Commands
async def addnft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new NFT for users to claim"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Add NFT Usage:**\n"
            "`/addnft <nft_id> | <name> | <link> | <description (optional)>`\n\n"
            "**Example:**\n"
            "`/addnft nft001 | Cool Ape NFT | https://opensea.io/nft/coolape | Limited edition digital art`\n"
            "`/addnft nft002 | Crypto Punk | https://rarible.com/punk123`",
            parse_mode='Markdown'
        )
        return
    
    parts = ' '.join(context.args).split('|')
    
    if len(parts) < 3:
        await update.message.reply_text("❌ Please provide: nft_id | name | link | description (optional)")
        return
    
    nft_id = parts[0].strip()
    name = parts[1].strip()
    link = parts[2].strip()
    description = parts[3].strip() if len(parts) > 3 else ""
    
    success = db.add_nft(nft_id, name, link, description)
    
    if success:
        await update.message.reply_text(
            f"✅ **NFT Added Successfully!**\n\n"
            f"🆔 **ID:** `{nft_id}`\n"
            f"📛 **Name:** {name}\n"
            f"🔗 **Link:** {link}\n"
            f"📝 **Description:** {description if description else 'None'}\n\n"
            f"💡 Users can now claim this NFT using `/claimnft`!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to add NFT! Maybe the ID already exists.")

async def listnfts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all NFTs in the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    all_nfts = db.get_all_nfts()
    
    if not all_nfts:
        await update.message.reply_text("📭 No NFTs in database yet.\n\nUse `/addnft` to add one!", parse_mode='Markdown')
        return
    
    msg = "🎨 **All NFTs in Database:**\n\n"
    
    for nft in all_nfts:
        status = "✅ Active" if nft.get('active', True) else "❌ Inactive"
        msg += f"🆔 **ID:** `{nft['nft_id']}`\n"
        msg += f"📛 **Name:** {nft['name']}\n"
        msg += f"🔗 **Link:** {nft['link']}\n"
        msg += f"📊 **Status:** {status}\n"
        msg += f"👥 **Claims:** {nft.get('claimed_count', 0)}\n"
        
        if nft.get('description'):
            msg += f"📝 **Desc:** {nft['description'][:50]}...\n"
        
        msg += "\n"
    
    msg += f"📊 **Total NFTs:** {len(all_nfts)}"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def removenft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove an NFT from the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Remove NFT Usage:**\n"
            "`/removenft <nft_id>`\n\n"
            "**Example:**\n"
            "`/removenft nft001`",
            parse_mode='Markdown'
        )
        return
    
    nft_id = context.args[0]
    
    success = db.remove_nft(nft_id)
    
    if success:
        await update.message.reply_text(
            f"✅ **NFT Removed!**\n\n"
            f"🆔 **ID:** `{nft_id}` has been deleted from the database.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ NFT with ID `{nft_id}` not found!", parse_mode='Markdown')

# Game Scripts Management Commands
async def addgamescript_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new game script for users to access"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Add Game Script Usage:**\n"
            "`/addgamescript <script_id> | <name> | <link> | <description (optional)>`\n\n"
            "**Example:**\n"
            "`/addgamescript script001 | Auto Aim Script | https://example.com/script1 | Advanced auto-aim for FPS games`\n"
            "`/addgamescript script002 | Resource Manager | https://example.com/script2`",
            parse_mode='Markdown'
        )
        return
    
    parts = ' '.join(context.args).split('|')
    
    if len(parts) < 3:
        await update.message.reply_text("❌ Please provide: script_id | name | link | description (optional)")
        return
    
    script_id = parts[0].strip()
    name = parts[1].strip()
    link = parts[2].strip()
    description = parts[3].strip() if len(parts) > 3 else ""
    
    success = db.add_game_script(script_id, name, link, description)
    
    if success:
        await update.message.reply_text(
            f"✅ **Game Script Added Successfully!**\n\n"
            f"🆔 **ID:** `{script_id}`\n"
            f"📛 **Name:** {name}\n"
            f"🔗 **Link:** {link}\n"
            f"📝 **Description:** {description if description else 'None'}\n\n"
            f"💡 Users can now access this script using `/gamescripts`!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to add game script! Maybe the ID already exists.")

async def listgamescripts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all game scripts in the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    all_scripts = db.get_all_game_scripts()
    
    if not all_scripts:
        await update.message.reply_text("📭 No game scripts in database yet.\n\nUse `/addgamescript` to add one!", parse_mode='Markdown')
        return
    
    msg = "🎮 **All Game Scripts in Database:**\n\n"
    
    for script in all_scripts:
        status = "✅ Active" if script.get('active', True) else "❌ Inactive"
        msg += f"🆔 **ID:** `{script['script_id']}`\n"
        msg += f"📛 **Name:** {script['name']}\n"
        msg += f"🔗 **Link:** {script['link']}\n"
        msg += f"📊 **Status:** {status}\n"
        msg += f"👁️ **Views:** {script.get('views_count', 0)}\n"
        
        if script.get('description'):
            msg += f"📝 **Desc:** {script['description'][:50]}...\n"
        
        msg += "\n"
    
    msg += f"📊 **Total Scripts:** {len(all_scripts)}"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def removegamescript_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a game script from the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Remove Game Script Usage:**\n"
            "`/removegamescript <script_id>`\n\n"
            "**Example:**\n"
            "`/removegamescript script001`",
            parse_mode='Markdown'
        )
        return
    
    script_id = context.args[0]
    
    success = db.remove_game_script(script_id)
    
    if success:
        await update.message.reply_text(
            f"✅ **Game Script Removed!**\n\n"
            f"🆔 **ID:** `{script_id}` has been deleted from the database.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ Game script with ID `{script_id}` not found!", parse_mode='Markdown')

async def setscriptviews_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually set the view count for a game script"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 **Set Script Views Usage:**\n"
            "`/setscriptviews <script_id> <views_count>`\n\n"
            "**Example:**\n"
            "`/setscriptviews script001 1000`",
            parse_mode='Markdown'
        )
        return
    
    script_id = context.args[0]
    
    try:
        views_count = int(context.args[1])
        if views_count < 0:
            await update.message.reply_text("❌ Views count must be a positive number!")
            return
    except ValueError:
        await update.message.reply_text("❌ Views count must be a valid number!")
        return
    
    success = db.set_script_views(script_id, views_count)
    
    if success:
        await update.message.reply_text(
            f"✅ **Script Views Updated!**\n\n"
            f"🆔 **ID:** `{script_id}`\n"
            f"👁️ **Views:** {views_count}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ Game script with ID `{script_id}` not found!", parse_mode='Markdown')

# Movies Management Commands
async def addmovie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new movie for users to access"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Add Movie Usage:**\n"
            "`/addmovie <movie_id> | <name> | <link> | <description (optional)>`\n\n"
            "**Example:**\n"
            "`/addmovie movie001 | The Matrix | https://example.com/matrix | Sci-fi action film`\n"
            "`/addmovie movie002 | Inception | https://example.com/inception`",
            parse_mode='Markdown'
        )
        return
    
    parts = ' '.join(context.args).split('|')
    
    if len(parts) < 3:
        await update.message.reply_text("❌ Please provide: movie_id | name | link | description (optional)")
        return
    
    movie_id = parts[0].strip()
    name = parts[1].strip()
    link = parts[2].strip()
    description = parts[3].strip() if len(parts) > 3 else ""
    
    success = db.add_movie(movie_id, name, link, description)
    
    if success:
        await update.message.reply_text(
            f"✅ **Movie Added Successfully!**\n\n"
            f"🆔 **ID:** `{movie_id}`\n"
            f"🎬 **Name:** {name}\n"
            f"🔗 **Link:** {link}\n"
            f"📝 **Description:** {description if description else 'None'}\n\n"
            f"💡 Users can now access this movie using `/movies`!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to add movie! Maybe the ID already exists.")

async def listmovies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all movies in the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    all_movies = db.get_all_movies()
    
    if not all_movies:
        await update.message.reply_text("📭 No movies in database yet.\n\nUse `/addmovie` to add one!", parse_mode='Markdown')
        return
    
    msg = "🎬 **All Movies in Database:**\n\n"
    
    for movie in all_movies:
        status = "✅ Active" if movie.get('active', True) else "❌ Inactive"
        msg += f"🆔 **ID:** `{movie['movie_id']}`\n"
        msg += f"🎬 **Name:** {movie['name']}\n"
        msg += f"🔗 **Link:** {movie['link']}\n"
        msg += f"📊 **Status:** {status}\n"
        msg += f"👁️ **Views:** {movie.get('views_count', 0)}\n"
        
        if movie.get('description'):
            msg += f"📝 **Desc:** {movie['description'][:50]}...\n"
        
        msg += "\n"
    
    msg += f"📊 **Total Movies:** {len(all_movies)}"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def removemovie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a movie from the database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Remove Movie Usage:**\n"
            "`/removemovie <movie_id>`\n\n"
            "**Example:**\n"
            "`/removemovie movie001`",
            parse_mode='Markdown'
        )
        return
    
    movie_id = context.args[0]
    
    success = db.remove_movie(movie_id)
    
    if success:
        await update.message.reply_text(
            f"✅ **Movie Removed!**\n\n"
            f"🆔 **ID:** `{movie_id}` has been deleted from the database.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ Movie with ID `{movie_id}` not found!", parse_mode='Markdown')

async def setmovieviews_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually set the view count for a movie"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 **Set Movie Views Usage:**\n"
            "`/setmovieviews <movie_id> <views_count>`\n\n"
            "**Example:**\n"
            "`/setmovieviews movie001 5000`",
            parse_mode='Markdown'
        )
        return
    
    movie_id = context.args[0]
    
    try:
        views_count = int(context.args[1])
        if views_count < 0:
            await update.message.reply_text("❌ Views count must be a positive number!")
            return
    except ValueError:
        await update.message.reply_text("❌ Views count must be a valid number!")
        return
    
    success = db.set_movie_views(movie_id, views_count)
    
    if success:
        await update.message.reply_text(
            f"✅ **Movie Views Updated!**\n\n"
            f"🆔 **ID:** `{movie_id}`\n"
            f"👁️ **Views:** {views_count}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ Movie with ID `{movie_id}` not found!", parse_mode='Markdown')

async def moviescrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scrape movies from a category and save to database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        categories = get_available_categories()
        total_movies = db.count_movies_by_category()
        
        msg = "🎬 **Movie Scraper**\n\n"
        msg += f"📊 **Database:** {total_movies} total movies\n\n"
        msg += "**Usage:**\n"
        msg += "`/moviescrape <category> <pages>`\n\n"
        msg += "**Available Categories:**\n"
        
        for cat in categories:
            count = db.count_movies_by_category(cat)
            msg += f"• {cat}: {count} movies\n"
        
        msg += "\n**Examples:**\n"
        msg += "`/moviescrape NETFLIX 1` - Scrape 1 page\n"
        msg += "`/moviescrape BOLLYWOOD 10` - Scrape 10 pages\n"
        msg += "`/moviescrape HOLLYWOOD 50` - Scrape 50 pages\n\n"
        msg += "⚠️ **Note:** Each page takes ~30-60 seconds\n"
        msg += "✨ **Duplicates auto-skipped!** Safe to re-run!\n"
        msg += "🔗 **Links stored as original** (shortened on user request)"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    category = context.args[0].upper()
    num_pages = 1
    
    # Parse number of pages
    if len(context.args) > 1:
        try:
            num_pages = int(context.args[1])
            if num_pages < 1:
                await update.message.reply_text("❌ Number of pages must be at least 1!")
                return
            if num_pages > 100:
                await update.message.reply_text("❌ Maximum 100 pages per scrape to avoid excessive timeouts!\n\n💡 Tip: You can run the command multiple times.")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid number of pages!")
            return
    
    # Send initial message
    progress_msg = await update.message.reply_text(
        f"🎬 **Starting Movie Scraper**\n\n"
        f"📂 Category: {category}\n"
        f"📄 Pages: {num_pages}\n\n"
        f"⏳ This may take {num_pages * 30}-{num_pages * 60} seconds...\n"
        f"Please wait...",
        parse_mode='Markdown'
    )
    
    try:
        # Run the scraper
        total_saved, total_failed, error = await scrape_and_save_movies(category, num_pages)
        
        if error:
            await progress_msg.edit_text(
                f"❌ **Scraping Failed**\n\n"
                f"Category: {category}\n"
                f"Error: {error}",
                parse_mode='Markdown'
            )
            return
        
        # Success message
        total_in_db = db.count_movies_by_category(category)
        
        msg = f"✅ **Scraping Complete!**\n\n"
        msg += f"📂 **Category:** {category}\n"
        msg += f"📄 **Pages Scraped:** {num_pages}\n\n"
        msg += f"**Results:**\n"
        msg += f"✅ Saved: {total_saved} movies\n"
        msg += f"❌ Failed: {total_failed} movies\n\n"
        msg += f"📊 **Total in database:** {total_in_db} {category} movies\n\n"
        msg += "🔍 Users can now search with:\n"
        msg += f"`/searchmovie <name>`\n"
        msg += f"`/netflix <name>`"
        
        await progress_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Error in moviescrape: {e}")
        await progress_msg.edit_text(
            f"❌ **Error Occurred**\n\n"
            f"Error: {str(e)}\n\n"
            "Please check logs and try again.",
            parse_mode='Markdown'
        )

async def fixcategories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fix categorization for existing items in database"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    progress_msg = await update.message.reply_text(
        "🔧 **Fixing Database Categories**\n\n"
        "⏳ Analyzing and updating items...",
        parse_mode='Markdown'
    )
    
    try:
        # Find items that might need fixing:
        # 1. Items without type field
        # 2. Items marked as software but might be games (have "game" in category or from game sites)
        items_to_check = list(db.software_collection.find({
            "$or": [
                {"type": {"$exists": False}},
                {
                    "type": "software",
                    "$or": [
                        {"category": {"$regex": "game", "$options": "i"}},
                        {"source_url": {"$regex": "apunkagames|pcgamestorrents|fitgirl|oceanofgames|skidrow|igg-games|steamunlocked|codex|cpy|repack", "$options": "i"}}
                    ]
                }
            ]
        }))
        
        games_fixed = 0
        software_fixed = 0
        categories_updated = 0
        
        for item in items_to_check:
            category_original = item.get('category', '')
            category = category_original.lower()
            name = item.get('name', '').lower()
            source_url = item.get('source_url', '').lower()
            
            # Conservative approach - only fix obvious cases, leave ambiguous items unchanged
            
            # Software keywords that indicate it's a tool/utility (high priority override)
            software_keywords = ['booster', 'maker', 'engine', 'bar', 'recorder', 'capture',
                                'launcher', 'manager', 'tools', 'toolkit', 'utility',
                                'activator', 'crack', 'keygen', 'patch', 'loader',
                                'browser', 'security', 'antivirus', 'vpn', 'office',
                                'productivity', 'editor', 'converter', 'compiler', 'ide',
                                'framework', 'sdk', 'plugin', 'addon', 'mod tool']
            
            # Comprehensive list of game site domains - aligned with quick_scraper
            game_sites = ['apunkagames', 'pcgamestorrents', 'fitgirl-repacks', 'oceanofgames',
                         'skidrowreloaded', 'igg-games', 'steamunlocked', 'skidrowcodex',
                         'codexgames', 'cpygames', 'repack-games', 'gog-games', 'crohasit',
                         'downloadpcgames', 'pcgamesn', 'crackwatch', 'dodi-repacks']
            
            # Check if it's clearly software (highest priority)
            is_software_tool = any(kw in category or kw in name for kw in software_keywords)
            
            # Check if it's from a trusted game source
            is_from_game_site = any(site in source_url for site in game_sites)
            
            if is_software_tool:
                # Explicitly software - don't misclassify tools
                item_type = 'software'
            elif 'game' in category and not is_software_tool:
                # Category contains "game" and it's not a software tool → game
                item_type = 'game'
            elif is_from_game_site and not is_software_tool:
                # From trusted game site and not a software tool → game
                item_type = 'game'
            else:
                # Ambiguous - keep as software (safer default)
                # The main fix is in quick_scraper.py for NEW items
                item_type = 'software'
            updates = {"type": item_type}
            
            # Fix category name for games
            if item_type == 'game' and 'game' not in category:
                if category_original and category_original != 'Uncategorized':
                    new_category = f"{category_original} Games"
                else:
                    new_category = 'Games'
                updates["category"] = new_category
                categories_updated += 1
            
            # Update the item
            db.software_collection.update_one(
                {"_id": item["_id"]},
                {"$set": updates}
            )
            
            if item_type == 'game':
                games_fixed += 1
            else:
                software_fixed += 1
        
        # Get updated counts
        total_games = db.software_collection.count_documents({
            "$or": [
                {"type": "game"},
                {"category": {"$regex": "game", "$options": "i"}}
            ]
        })
        total_software = db.software_collection.count_documents({
            "$and": [
                {
                    "$or": [
                        {"type": {"$exists": False}},
                        {"type": "software"}
                    ]
                },
                {"category": {"$not": {"$regex": "game", "$options": "i"}}}
            ]
        })
        
        await progress_msg.edit_text(
            f"✅ **Database Categories Fixed!**\n\n"
            f"**Items Updated:**\n"
            f"🎮 Games: {games_fixed}\n"
            f"💻 Software: {software_fixed}\n"
            f"📂 Categories renamed: {categories_updated}\n\n"
            f"**New Totals:**\n"
            f"🎮 Total Games: {total_games}\n"
            f"💻 Total Software: {total_software}\n\n"
            f"✨ Games should now appear correctly in the mini app!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Error in fixcategories: {e}")
        await progress_msg.edit_text(
            f"❌ **Error Occurred**\n\n"
            f"Error: {str(e)}",
            parse_mode='Markdown'
        )
