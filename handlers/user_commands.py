import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.translations import get_text, get_language_keyboard, LANGUAGES
from utils.database import get_or_create_user, get_user_language, set_user_language, is_favorite
import utils.database as db
from services.ai_service import ai_search_software, web_search_and_extract
from services.url_shortener import shorten_url
from services.movie_scraper import get_movies_from_category, get_available_categories
from bson import ObjectId

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name, user.last_name)
    lang = get_user_language(user.id)
    
    welcome_msg = f"╔═══════════════════════════╗\n"
    welcome_msg += f"    🎉 {get_text(lang, 'welcome')} 🎉\n"
    welcome_msg += f"╚═══════════════════════════╝\n\n"
    welcome_msg += f"🌟 **Your Ultimate Digital Hub!** 🌟\n\n"
    welcome_msg += f"┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
    welcome_msg += f"  🎮 **Games** - Latest & Best!\n"
    welcome_msg += f"  💻 **Software** - Professional Tools!\n"
    welcome_msg += f"  🎬 **Movies** - HD Entertainment!\n"
    welcome_msg += f"  🎨 **NFTs** - Free Digital Art!\n"
    welcome_msg += f"  🎯 **Game Scripts** - Pro Mods!\n"
    welcome_msg += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    welcome_msg += f"💎 All downloads are **FREE** with monetized links!\n"
    welcome_msg += f"🌍 Available in **6 languages**!\n"
    welcome_msg += f"🤖 Powered by **AI Search**!\n\n"
    welcome_msg += f"{get_text(lang, 'select_language')}"
    
    keyboard = get_language_keyboard()
    
    await update.message.reply_text(welcome_msg, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    help_msg = f"╔═══════════════════════════════╗\n"
    help_msg += f"      📚 **COMMAND CENTER** 📚\n"
    help_msg += f"╚═══════════════════════════════╝\n\n"
    
    help_msg += f"┏━━ 🎮 **GAMES & SOFTWARE** ━━┓\n"
    help_msg += f"┃ 🔍 /search <name> - Search anything\n"
    help_msg += f"┃ 🤖 /aisearch <query> - AI-powered search\n"
    help_msg += f"┃    🌐 *Searches web if not in database!*\n"
    help_msg += f"┃ 🎮 /browsegame - Browse games catalog\n"
    help_msg += f"┃ 💻 /browsesoft - Browse software catalog\n"
    help_msg += f"┃ 🔥 /popular - Trending downloads\n"
    help_msg += f"┃ 🆕 /new - Latest releases\n"
    help_msg += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    
    help_msg += f"┏━━ 🎬 **MOVIES & SHOWS** ━━┓\n"
    help_msg += f"┃ 📂 /movies <category> - Browse by category\n"
    help_msg += f"┃ 🔍 /searchmovie <name> - Search all movies\n"
    help_msg += f"┃\n"
    help_msg += f"┃ 🎯 **Streaming Platforms:**\n"
    help_msg += f"┃ 📺 /movienetflix - Netflix content\n"
    help_msg += f"┃ 🎭 /movieprime - Prime Video content\n"
    help_msg += f"┃ 🌟 /moviehotstar - Hotstar content\n"
    help_msg += f"┃ 📺 /moviewebseries - Web Series\n"
    help_msg += f"┃\n"
    help_msg += f"┃ 🌍 **By Industry:**\n"
    help_msg += f"┃ 🎬 /moviebollywood - Bollywood films\n"
    help_msg += f"┃ 🎥 /moviehollywood - Hollywood films\n"
    help_msg += f"┃ 🌴 /moviesouth - South Indian cinema\n"
    help_msg += f"┃\n"
    help_msg += f"┃ 🗣️ **By Language:**\n"
    help_msg += f"┃ 🇮🇳 /moviehindi - Hindi movies\n"
    help_msg += f"┃ 🇺🇸 /movieenglish - English movies\n"
    help_msg += f"┃ 🎭 /movietamil - Tamil movies\n"
    help_msg += f"┃ 🎬 /movietelugu - Telugu movies\n"
    help_msg += f"┃ 🌟 /moviemalayalam - Malayalam movies\n"
    help_msg += f"┃ 🎥 /moviekannada - Kannada movies\n"
    help_msg += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    
    help_msg += f"┏━━ 🎨 **SPECIAL FEATURES** ━━┓\n"
    help_msg += f"┃ 🎨 /claimnft - Claim FREE NFTs!\n"
    help_msg += f"┃ 🎯 /gamescripts - Pro game scripts & mods\n"
    help_msg += f"┃ 🌐 /webapp - Open Web Interface\n"
    help_msg += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    
    help_msg += f"┏━━ 👤 **YOUR ACCOUNT** ━━┓\n"
    help_msg += f"┃ ❤️ /favorites - Your favorite items\n"
    help_msg += f"┃ 📥 /mydownloads - Download history\n"
    help_msg += f"┃ 👤 /profile - Your profile stats\n"
    help_msg += f"┃ 🌍 /language - Change language\n"
    help_msg += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    
    help_msg += f"💡 **Tip:** All downloads are FREE and support the bot!\n"
    help_msg += f"🚀 **Powered by AI** for the best results!"
    
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    if not context.args:
        await update.message.reply_text(get_text(lang, 'search_prompt'))
        return
    
    query = ' '.join(context.args)
    
    results = list(db.software_collection.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}}
        ]
    }).limit(10))
    
    if not results:
        await update.message.reply_text(get_text(lang, 'no_results'))
        return
    
    for software in results:
        await send_software_details(update, software, lang, user.id)

async def ai_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    if not context.args:
        await update.message.reply_text(f"{get_text(lang, 'ai_search')}\n\n{get_text(lang, 'search_prompt')}")
        return
    
    query = ' '.join(context.args)
    
    await update.message.reply_text(get_text(lang, 'ai_searching'))
    
    # First, try searching in database
    results = ai_search_software(query, db.software_collection, lang)
    
    if results is None:
        # API error (no keys or quota exceeded)
        await update.message.reply_text(
            "⚠️ **AI Search Unavailable**\n\n"
            "AI search couldn't process your request due to one of these reasons:\n\n"
            "• No OpenRouter API keys configured\n"
            "• API quota limits exceeded\n"
            "• Authentication issues\n\n"
            "**What to do:**\n"
            "If you're an admin, add an OpenRouter API key using:\n"
            "`/addapikey <your_key>`\n\n"
            "Get a FREE API key from: https://openrouter.ai/keys\n\n"
            "Searching the web instead...",
            parse_mode='Markdown'
        )
        # Fall through to web search below
        results = []
    
    if results:
        # Found in database
        for software in results[:5]:
            await send_software_details(update, software, lang, user.id)
    else:
        # Not found in database - search the web
        await update.message.reply_text(
            "🔍 Not found in our database. Searching the internet for download links...",
            parse_mode='Markdown'
        )
        
        # Search the web for download links
        web_results = web_search_and_extract(query)
        
        if web_results:
            await update.message.reply_text(
                f"🌐 **Found {len(web_results)} result(s) from the web:**\n\n"
                "⚠️ These are external links. Please verify authenticity before downloading.",
                parse_mode='Markdown'
            )
            
            # Display each web result
            for idx, item in enumerate(web_results, 1):
                msg = f"🔹 **{item['name']}**\n\n"
                msg += f"📝 {item['description']}\n\n"
                msg += f"📂 Category: {item.get('category', 'Unknown')}\n"
                msg += f"💾 Size: {item.get('file_size', 'Unknown')}\n"
                msg += f"🔖 Version: {item.get('version', 'Latest')}\n\n"
                
                if item.get('download_links'):
                    msg += "📥 **Download Links:**\n"
                    for link_idx, link in enumerate(item['download_links'][:3], 1):
                        # Shorten the link if available
                        try:
                            shortened, service = shorten_url(link, db.url_cache_collection)
                            msg += f"{link_idx}. {shortened}\n"
                        except:
                            msg += f"{link_idx}. {link}\n"
                else:
                    msg += f"🌐 Source: {item.get('source_url', 'N/A')}\n"
                
                await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            # Web search also failed
            await update.message.reply_text(
                f"{get_text(lang, 'no_results')}\n\n"
                "❌ No matches found in our database or on the web.\n\n"
                "💡 **Suggestions:**\n"
                "• Try different keywords\n"
                "• Check spelling\n"
                "• Use `/browsegame` to browse all games\n"
                "• Use `/browsesoft` to browse all software\n"
                "• Ask an admin to add this to the database",
                parse_mode='Markdown'
            )

async def browse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    msg = "🔍 **Browse Content**\n\n"
    msg += "Please use the specific browse commands:\n"
    msg += "🎮 `/browsegame` - Browse games\n"
    msg += "💻 `/browsesoft` - Browse software\n\n"
    msg += "This command is deprecated. Use the commands above instead."
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def browsegame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    categories = db.software_collection.distinct("category", {"is_game": True})
    
    if not categories:
        await update.message.reply_text("🎮 No game categories available yet.")
        return
    
    keyboard = []
    row = []
    for category in sorted(categories):
        row.append(InlineKeyboardButton(category, callback_data=f"gamecat_{category}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    await update.message.reply_text(
        "🎮 **Browse Games by Category**\n\nSelect a game category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def browsesoft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    categories = db.software_collection.distinct("category", {"is_game": {"$ne": True}})
    
    if not categories:
        await update.message.reply_text("💻 No software categories available yet.")
        return
    
    keyboard = []
    row = []
    for category in sorted(categories):
        row.append(InlineKeyboardButton(category, callback_data=f"softcat_{category}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    await update.message.reply_text(
        "💻 **Browse Software by Category**\n\nSelect a software category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    popular = list(db.software_collection.find().sort("downloads_count", -1).limit(10))
    
    if not popular:
        await update.message.reply_text("No software available yet.")
        return
    
    for software in popular:
        await send_software_details(update, software, lang, user.id)

async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    new_software = list(db.software_collection.find().sort("date_added", -1).limit(10))
    
    if not new_software:
        await update.message.reply_text("No software available yet.")
        return
    
    for software in new_software:
        await send_software_details(update, software, lang, user.id)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    user_data = db.users_collection.find_one({"user_id": user.id})
    
    if not user_data:
        await update.message.reply_text("User not found.")
        return
    
    profile_msg = f"👤 **Your Profile**\n\n"
    profile_msg += f"**Name:** {user.first_name} {user.last_name or ''}\n"
    profile_msg += f"**Username:** @{user.username or 'N/A'}\n"
    profile_msg += f"**Language:** {LANGUAGES[lang]['name']} {LANGUAGES[lang]['flag']}\n"
    profile_msg += f"**Total Downloads:** {user_data.get('total_downloads', 0)}\n"
    profile_msg += f"**Favorites:** {len(user_data.get('favorites', []))}\n"
    profile_msg += f"**Joined:** {user_data.get('joined_at', 'N/A')[:10]}"
    
    await update.message.reply_text(profile_msg, parse_mode='Markdown')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    keyboard = get_language_keyboard()
    await update.message.reply_text(get_text(lang, 'select_language'), reply_markup=keyboard)

async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    user_data = db.users_collection.find_one({"user_id": user.id})
    
    if not user_data or not user_data.get('favorites'):
        await update.message.reply_text(f"{get_text(lang, 'favorites')}\n\nNo favorites yet.")
        return
    
    for software_id in user_data['favorites']:
        software = db.software_collection.find_one({"_id": ObjectId(software_id)})
        if software:
            await send_software_details(update, software, lang, user.id)

async def mydownloads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    
    user_data = db.users_collection.find_one({"user_id": user.id})
    
    if not user_data or not user_data.get('downloads'):
        await update.message.reply_text(f"{get_text(lang, 'my_downloads')}\n\nNo downloads yet.")
        return
    
    recent_downloads = user_data['downloads'][-10:]
    
    for software_id in reversed(recent_downloads):
        software = db.software_collection.find_one({"_id": ObjectId(software_id)})
        if software:
            await send_software_details(update, software, lang, user.id)

async def send_software_details(update, software, lang, user_id):
    msg = f"📦 **{software['name']}**\n\n"
    msg += f"{software.get('description', 'No description')[:200]}\n\n"
    msg += f"📂 **{get_text(lang, 'category')}** {software.get('category', 'N/A')}\n"
    msg += f"💻 **{get_text(lang, 'os')}:** {', '.join(software.get('os', ['N/A']))}\n"
    msg += f"📏 **{get_text(lang, 'size')}:** {software.get('file_size', 'N/A')}\n"
    msg += f"🔢 **{get_text(lang, 'version')}:** {software.get('version', 'N/A')}\n"
    msg += f"⭐ **{get_text(lang, 'rating')}:** {software.get('average_rating', 0):.1f}/5\n"
    msg += f"⬇️ **{get_text(lang, 'downloads')}:** {software.get('downloads_count', 0):,}"
    
    keyboard = []
    
    if software.get('download_links'):
        keyboard.append([InlineKeyboardButton(f"⬇️ {get_text(lang, 'download_link')}", callback_data=f"download_{str(software['_id'])}")])
    
    keyboard.append([InlineKeyboardButton(f"⭐ {get_text(lang, 'rate_software')}", callback_data=f"rate_{str(software['_id'])}")])
    
    fav_text = get_text(lang, 'remove_favorite') if is_favorite(user_id, software['_id']) else get_text(lang, 'add_favorite')
    keyboard.append([InlineKeyboardButton(fav_text, callback_data=f"fav_{str(software['_id'])}")])
    
    if update.callback_query:
        await update.callback_query.message.reply_text(
            msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(
            msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )

async def claimnft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow users to claim free NFTs"""
    user = update.effective_user
    lang = get_user_language(user.id)
    
    active_nfts = db.get_active_nfts()
    
    if not active_nfts:
        await update.message.reply_text(
            "📭 **No NFTs Available**\n\n"
            "There are currently no NFTs available for claiming.\n"
            "Check back later!",
            parse_mode='Markdown'
        )
        return
    
    msg = "🎨 **Free NFTs Available!**\n\n"
    msg += "Claim these amazing NFTs for FREE:\n\n"
    
    for i, nft in enumerate(active_nfts, 1):
        already_claimed = db.has_claimed_nft(user.id, nft['nft_id'])
        
        msg += f"**{i}. {nft['name']}**\n"
        
        if nft.get('description'):
            msg += f"📝 {nft['description']}\n"
        
        if already_claimed:
            msg += f"✅ **Already Claimed!**\n"
        else:
            msg += f"🔗 **Claim Now:** {nft['link']}\n"
        
        msg += f"👥 {nft.get('claimed_count', 0)} people claimed\n\n"
    
    msg += "💡 **How to claim:**\n"
    msg += "1. Click the link above\n"
    msg += "2. Follow the instructions on the NFT platform\n"
    msg += "3. The NFT will be added to your wallet!\n\n"
    msg += "⚡ These are **100% FREE** NFTs!"
    
    keyboard = []
    for nft in active_nfts:
        if not db.has_claimed_nft(user.id, nft['nft_id']):
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Mark '{nft['name']}' as Claimed",
                    callback_data=f"claim_nft_{nft['nft_id']}"
                )
            ])
    
    if keyboard:
        await update.message.reply_text(
            msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

async def gamescripts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available game scripts to users"""
    user = update.effective_user
    lang = get_user_language(user.id)
    
    active_scripts = db.get_active_game_scripts()
    
    if not active_scripts:
        await update.message.reply_text(
            "📭 **No Game Scripts Available**\n\n"
            "There are currently no game scripts available.\n"
            "Check back later!",
            parse_mode='Markdown'
        )
        return
    
    msg = "🎮 **Game Scripts Available!**\n\n"
    msg += "Access these game scripts:\n\n"
    
    for i, script in enumerate(active_scripts, 1):
        msg += f"**{i}. {script['name']}**\n"
        
        if script.get('description'):
            msg += f"📝 {script['description']}\n"
        
        msg += f"🔗 **Access:** {script['link']}\n"
        msg += f"👁️ {script.get('views_count', 0)} views\n\n"
        
        db.increment_script_views(script['script_id'])
    
    msg += "💡 **How to use:**\n"
    msg += "1. Click the link above\n"
    msg += "2. Follow the instructions on the page\n"
    msg += "3. Enjoy the game script!\n\n"
    msg += "⚡ Use responsibly and have fun!"
    
    await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

async def searchmovie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search movies from database"""
    user = update.effective_user
    lang = get_user_language(user.id)
    
    if not context.args:
        # Show usage instructions
        total_movies = db.count_movies_by_category()
        
        msg = "🔍 **Search Movies (ALL Categories)**\n\n"
        msg += f"Database contains **{total_movies}** total movies\n\n"
        msg += "**Usage:**\n"
        msg += "`/searchmovie <movie name>`\n\n"
        msg += "**Examples:**\n"
        msg += "`/searchmovie Avengers`\n"
        msg += "`/searchmovie Stranger Things`\n\n"
        msg += "🌍 **Searches ALL categories!**\n\n"
        msg += "💡 **Category-Specific Search:**\n"
        msg += "• `/movienetflix` - Netflix only\n"
        msg += "• `/moviebollywood` - Bollywood only\n"
        msg += "• `/moviehollywood` - Hollywood only\n"
        msg += "• And more! See /help"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    query = ' '.join(context.args)
    
    # Search in database
    results = db.search_movies(query, limit=10)
    
    if not results:
        msg = f"❌ **No Results Found**\n\n"
        msg += f"Search: `{query}`\n\n"
        msg += "💡 **Suggestions:**\n"
        msg += "- Try different keywords\n"
        msg += "- Check spelling\n"
        msg += "- Try `/movies <category>` to browse\n"
        msg += "- Ask admin to scrape more movies"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    # Send results
    msg = f"🎬 **Search Results: \"{query}\"**\n\n"
    msg += f"Found {len(results)} movie(s):\n\n"
    
    for i, movie in enumerate(results, 1):
        # Shorten the link on-demand when user requests it
        shortened_link = movie['download_link']
        if db.url_cache_collection is not None:
            try:
                shortened_link, service = shorten_url(movie['download_link'], db.url_cache_collection)
                logger.info(f"Shortened link using {service} for: {movie['title']}")
            except Exception as e:
                logger.warning(f"Failed to shorten link: {e}, using original")
                shortened_link = movie['download_link']
        
        msg += f"**{i}. {movie['title']}**\n"
        msg += f"📂 Category: {movie.get('category', 'Unknown')}\n"
        msg += f"🔗 **Download:** {shortened_link}\n"
        msg += f"👁️ Views: {movie.get('views_count', 0)}\n\n"
        
        # Increment view count
        db.increment_movie_views(movie['movie_id'])
    
    msg += "🍿 **How to download:**\n"
    msg += "1. Click the download link above\n"
    msg += "2. Complete verification if needed\n"
    msg += "3. Download and enjoy!\n\n"
    msg += "⚡ Links are auto-shortened!"
    
    await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

async def category_movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Search movies within a specific category"""
    user = update.effective_user
    lang = get_user_language(user.id)
    
    if not context.args:
        total_movies = db.count_movies_by_category(category)
        
        msg = f"🎬 **Search {category} Movies**\n\n"
        msg += f"Database contains **{total_movies}** {category} movies\n\n"
        msg += "**Usage:**\n"
        msg += f"`/movie{category.lower()} <movie name>`\n\n"
        msg += "**Examples:**\n"
        msg += f"`/movie{category.lower()} Avengers`\n"
        msg += f"`/movie{category.lower()} Stranger Things`\n\n"
        msg += f"💡 **Tip:** This searches only {category} category!"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    query = ' '.join(context.args)
    
    # Search in database (category-specific)
    results = db.search_movies(query, category=category, limit=10)
    
    if not results:
        msg = f"❌ **No Results Found in {category}**\n\n"
        msg += f"Search: `{query}`\n\n"
        msg += "💡 **Suggestions:**\n"
        msg += "- Try different keywords\n"
        msg += "- Check spelling\n"
        msg += f"- Try `/movies {category}` to browse all\n"
        msg += "- Use `/searchmovie` to search ALL categories"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    # Send results
    msg = f"🎬 **{category} Search: \"{query}\"**\n\n"
    msg += f"Found {len(results)} movie(s):\n\n"
    
    for i, movie in enumerate(results, 1):
        # Shorten the link on-demand when user requests it
        shortened_link = movie['download_link']
        if db.url_cache_collection is not None:
            try:
                shortened_link, service = shorten_url(movie['download_link'], db.url_cache_collection)
                logger.info(f"Shortened link using {service} for: {movie['title']}")
            except Exception as e:
                logger.warning(f"Failed to shorten link: {e}, using original")
                shortened_link = movie['download_link']
        
        msg += f"**{i}. {movie['title']}**\n"
        msg += f"🔗 **Download:** {shortened_link}\n"
        msg += f"👁️ Views: {movie.get('views_count', 0)}\n\n"
        
        # Increment view count
        db.increment_movie_views(movie['movie_id'])
    
    msg += "🍿 **How to download:**\n"
    msg += "1. Click the download link above\n"
    msg += "2. Complete verification if needed\n"
    msg += "3. Download and enjoy!\n\n"
    msg += "⚡ Links are auto-shortened!"
    
    await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

# Category-specific search commands
async def movienetflix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Netflix movies only"""
    await category_movie_search(update, context, "NETFLIX")

async def movieprime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Prime movies only"""
    await category_movie_search(update, context, "PRIME")

async def moviehotstar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Hotstar movies only"""
    await category_movie_search(update, context, "HOTSTAR")

async def moviehindi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Hindi movies only"""
    await category_movie_search(update, context, "HINDI")

async def movieenglish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search English movies only"""
    await category_movie_search(update, context, "ENGLISH")

async def movietamil_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Tamil movies only"""
    await category_movie_search(update, context, "TAMIL")

async def movietelugu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Telugu movies only"""
    await category_movie_search(update, context, "TELUGU")

async def moviemalayalam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Malayalam movies only"""
    await category_movie_search(update, context, "MALAYALAM")

async def moviekannada_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Kannada movies only"""
    await category_movie_search(update, context, "KANNADA")

async def moviebollywood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Bollywood movies only"""
    await category_movie_search(update, context, "BOLLYWOOD")

async def moviehollywood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Hollywood movies only"""
    await category_movie_search(update, context, "HOLLYWOOD")

async def moviesouth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search South movies only"""
    await category_movie_search(update, context, "SOUTH")

async def moviewebseries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search Web-Series only"""
    await category_movie_search(update, context, "WEB-SERIES")

async def movies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse movies from different categories"""
    user = update.effective_user
    lang = get_user_language(user.id)
    
    if not context.args:
        categories = get_available_categories()
        
        msg = "🎬 **Movie Categories**\n\n"
        msg += "Browse movies by category!\n\n"
        msg += "**Available Categories:**\n"
        
        for cat in categories:
            msg += f"• {cat}\n"
        
        msg += "\n**Usage:**\n"
        msg += "`/movies <category>`\n\n"
        msg += "**Examples:**\n"
        msg += "`/movies NETFLIX`\n"
        msg += "`/movies BOLLYWOOD`\n"
        msg += "`/movies HOLLYWOOD`\n\n"
        msg += "💡 **Tip:** Use `/searchmovie` or `/netflix` to search by name!"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    category = context.args[0].upper()
    page = 1
    
    # Check if page number is provided
    if len(context.args) > 1:
        try:
            page = int(context.args[1])
        except ValueError:
            pass
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        f"🎬 **Loading {category} Movies**\n\n"
        "⏳ Fetching movies from website...\n"
        "This may take a moment...",
        parse_mode='Markdown'
    )
    
    try:
        # Get movies from category
        movies, error = await get_movies_from_category(category, page, max_movies=10)
        
        if error or not movies:
            await loading_msg.edit_text(
                f"❌ **Failed to Load Movies**\n\n"
                f"Category: {category}\n"
                f"Error: {error or 'No movies found'}\n\n"
                "💡 Try:\n"
                "- Using `/movies` to see available categories\n"
                "- Checking the category name\n"
                "- Trying a different category",
                parse_mode='Markdown'
            )
            return
        
        # Build response message
        msg = f"🎬 **{category} Movies** (Page {page})\n\n"
        msg += f"Found {len(movies)} movies:\n\n"
        
        for i, movie in enumerate(movies, 1):
            # Shorten the link on-demand when user requests it
            shortened_link = movie['download_link']
            if db.url_cache_collection is not None:
                try:
                    shortened_link, service = shorten_url(movie['download_link'], db.url_cache_collection)
                    logger.info(f"Shortened link using {service} for: {movie['title']}")
                except Exception as e:
                    logger.warning(f"Failed to shorten link: {e}, using original")
                    shortened_link = movie['download_link']
            
            msg += f"**{i}. {movie['title']}**\n"
            msg += f"🔗 **Download:** {shortened_link}\n\n"
        
        msg += "🍿 **How to download:**\n"
        msg += "1. Click the download link above\n"
        msg += "2. Complete verification if needed\n"
        msg += "3. Download and enjoy!\n\n"
        
        if page == 1:
            msg += f"📄 **Next page:** `/movies {category} 2`\n"
        else:
            msg += f"📄 **Next page:** `/movies {category} {page + 1}`\n"
        
        msg += "⚡ Links are auto-shortened!"
        
        await loading_msg.edit_text(msg, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error in movies command: {e}")
        await loading_msg.edit_text(
            f"❌ **An error occurred**\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again later.",
            parse_mode='Markdown'
        )

async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import WebAppInfo
    import os
    
    user = update.effective_user
    lang = get_user_language(user.id)
    
    # Get the webapp URL from environment or construct it from Replit domain
    webapp_url = os.getenv('WEBAPP_URL')
    if not webapp_url:
        replit_domain = os.getenv('REPLIT_DEV_DOMAIN') or os.getenv('REPLIT_DOMAINS', '').split(',')[0]
        if replit_domain:
            webapp_url = f"https://{replit_domain}"
        else:
            webapp_url = 'http://localhost:5000'
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🚀 Launch Mini App", 
            web_app=WebAppInfo(url=webapp_url)
        )]
    ])
    
    msg = "🎮 **Game Hub Mini App**\n\n"
    msg += "Experience a beautiful visual interface to browse:\n\n"
    msg += "🎮 Games\n"
    msg += "🎬 Movies\n"
    msg += "🎨 NFTs\n"
    msg += "📜 Game Scripts\n"
    msg += "👤 Your Profile\n\n"
    msg += "Click the button below to launch the mini app!"
    
    await update.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
