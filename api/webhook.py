import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

import sys
sys.path.append('..')

from utils.database import init_database
import utils.database as db
from services.ai_service import init_openrouter

from handlers.user_commands import (
    start_command, help_command, search_command, ai_search_command,
    browse_command, browsegame_command, browsesoft_command,
    popular_command, new_command, profile_command,
    language_command, favorites_command, mydownloads_command, claimnft_command,
    gamescripts_command, movies_command, searchmovie_command,
    movienetflix_command, movieprime_command, moviehotstar_command,
    moviehindi_command, movieenglish_command, movietamil_command,
    movietelugu_command, moviemalayalam_command, moviekannada_command,
    moviebollywood_command, moviehollywood_command, moviesouth_command,
    moviewebseries_command, webapp_command
)
from handlers.admin_commands import (
    addsoft_command, quickadd_command, addsite_command, addlink_command,
    stats_command, earnings_command, scrapesoft_command, scrapegame_command,
    deletesoft_command, editsoft_command, dbinfo_command,
    cleardownloads_command, resetdb_command,
    quickscrapesoft_command, quickscrapegame_command,
    fullscrapesoft_command, fullscrapegame_command,
    addnft_command, listnfts_command, removenft_command,
    addgamescript_command, listgamescripts_command, removegamescript_command, setscriptviews_command,
    addmovie_command, listmovies_command, removemovie_command, setmovieviews_command,
    moviescrape_command
)
from handlers.api_key_commands import (
    add_api_key_command, list_api_keys_command, remove_api_key_command,
    toggle_api_key_command, apikey_stats_command
)
from handlers.download_handler import (
    handle_download_button, handle_category_callback,
    handle_language_callback, handle_rating_callback, handle_favorite_callback,
    handle_nft_claim_callback
)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')

application = None

def get_application():
    global application
    if application is None:
        try:
            init_database()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
        
        init_openrouter(db.api_keys_collection)
        logger.info("OpenRouter AI service initialized")
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("aisearch", ai_search_command))
        application.add_handler(CommandHandler("browse", browse_command))
        application.add_handler(CommandHandler("browsegame", browsegame_command))
        application.add_handler(CommandHandler("browsesoft", browsesoft_command))
        application.add_handler(CommandHandler("popular", popular_command))
        application.add_handler(CommandHandler("new", new_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("language", language_command))
        application.add_handler(CommandHandler("favorites", favorites_command))
        application.add_handler(CommandHandler("mydownloads", mydownloads_command))
        application.add_handler(CommandHandler("claimnft", claimnft_command))
        application.add_handler(CommandHandler("gamescripts", gamescripts_command))
        application.add_handler(CommandHandler("webapp", webapp_command))
        application.add_handler(CommandHandler("movies", movies_command))
        application.add_handler(CommandHandler("searchmovie", searchmovie_command))
        
        application.add_handler(CommandHandler("movienetflix", movienetflix_command))
        application.add_handler(CommandHandler("movieprime", movieprime_command))
        application.add_handler(CommandHandler("moviehotstar", moviehotstar_command))
        application.add_handler(CommandHandler("moviehindi", moviehindi_command))
        application.add_handler(CommandHandler("movieenglish", movieenglish_command))
        application.add_handler(CommandHandler("movietamil", movietamil_command))
        application.add_handler(CommandHandler("movietelugu", movietelugu_command))
        application.add_handler(CommandHandler("moviemalayalam", moviemalayalam_command))
        application.add_handler(CommandHandler("moviekannada", moviekannada_command))
        application.add_handler(CommandHandler("moviebollywood", moviebollywood_command))
        application.add_handler(CommandHandler("moviehollywood", moviehollywood_command))
        application.add_handler(CommandHandler("moviesouth", moviesouth_command))
        application.add_handler(CommandHandler("moviewebseries", moviewebseries_command))
        
        application.add_handler(CommandHandler("addsoft", addsoft_command))
        application.add_handler(CommandHandler("quickadd", quickadd_command))
        application.add_handler(CommandHandler("addsite", addsite_command))
        application.add_handler(CommandHandler("addlink", addlink_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("earnings", earnings_command))
        application.add_handler(CommandHandler("scrapesoft", scrapesoft_command))
        application.add_handler(CommandHandler("scrapegame", scrapegame_command))
        application.add_handler(CommandHandler("deletesoft", deletesoft_command))
        application.add_handler(CommandHandler("editsoft", editsoft_command))
        application.add_handler(CommandHandler("dbinfo", dbinfo_command))
        application.add_handler(CommandHandler("cleardownloads", cleardownloads_command))
        application.add_handler(CommandHandler("resetdb", resetdb_command))
        application.add_handler(CommandHandler("quickscrapesoft", quickscrapesoft_command))
        application.add_handler(CommandHandler("quickscrapegame", quickscrapegame_command))
        application.add_handler(CommandHandler("fullscrapesoft", fullscrapesoft_command))
        application.add_handler(CommandHandler("fullscrapegame", fullscrapegame_command))
        
        application.add_handler(CommandHandler("addapikey", add_api_key_command))
        application.add_handler(CommandHandler("listapikeys", list_api_keys_command))
        application.add_handler(CommandHandler("removeapikey", remove_api_key_command))
        application.add_handler(CommandHandler("toggleapikey", toggle_api_key_command))
        application.add_handler(CommandHandler("apikeystats", apikey_stats_command))
        
        application.add_handler(CommandHandler("addnft", addnft_command))
        application.add_handler(CommandHandler("listnfts", listnfts_command))
        application.add_handler(CommandHandler("removenft", removenft_command))
        
        application.add_handler(CommandHandler("addgamescript", addgamescript_command))
        application.add_handler(CommandHandler("listgamescripts", listgamescripts_command))
        application.add_handler(CommandHandler("removegamescript", removegamescript_command))
        application.add_handler(CommandHandler("setscriptviews", setscriptviews_command))
        
        application.add_handler(CommandHandler("addmovie", addmovie_command))
        application.add_handler(CommandHandler("listmovies", listmovies_command))
        application.add_handler(CommandHandler("removemovie", removemovie_command))
        application.add_handler(CommandHandler("setmovieviews", setmovieviews_command))
        application.add_handler(CommandHandler("moviescrape", moviescrape_command))
        
        application.add_handler(CallbackQueryHandler(handle_download_button, pattern=r'^download_'))
        application.add_handler(CallbackQueryHandler(handle_category_callback, pattern=r'^cat_'))
        application.add_handler(CallbackQueryHandler(handle_category_callback, pattern=r'^gamecat_'))
        application.add_handler(CallbackQueryHandler(handle_category_callback, pattern=r'^softcat_'))
        application.add_handler(CallbackQueryHandler(handle_language_callback, pattern=r'^lang_'))
        application.add_handler(CallbackQueryHandler(handle_rating_callback, pattern=r'^rate_'))
        application.add_handler(CallbackQueryHandler(handle_rating_callback, pattern=r'^rating_'))
        application.add_handler(CallbackQueryHandler(handle_favorite_callback, pattern=r'^fav_'))
        application.add_handler(CallbackQueryHandler(handle_nft_claim_callback, pattern=r'^claim_nft_'))
        
        logger.info("✅ All handlers registered successfully")
    
    return application

async def handler(request):
    try:
        if request.method == 'POST':
            app = get_application()
            
            body = await request.json()
            update = Update.de_json(body, app.bot)
            
            await app.initialize()
            await app.process_update(update)
            
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'ok'})
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'Telegram Bot Webhook is running',
                    'info': 'Send POST requests with Telegram updates'
                })
            }
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
