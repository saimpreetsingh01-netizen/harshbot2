from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bson import ObjectId
from datetime import datetime
from utils.database import get_user_language
import utils.database as db
from utils.translations import get_text
from services.url_shortener import shorten_url
from services.ai_service import get_alternative_suggestions

async def handle_download_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    software_id = query.data.split('_')[1]
    
    await query.message.edit_text(get_text(lang, 'downloading'))
    
    software = db.software_collection.find_one({"_id": ObjectId(software_id)})
    
    if not software:
        await query.message.edit_text(get_text(lang, 'software_not_found'))
        return
    
    original_links = software.get('download_links', [])
    
    if not original_links:
        await query.message.edit_text(get_text(lang, 'no_links'))
        return
    
    shortened_links = []
    
    for link_obj in original_links[:5]:
        original_url = link_obj['url'] if isinstance(link_obj, dict) else link_obj
        
        shortened_url, service_used = shorten_url(original_url, db.url_cache_collection)
        
        shortened_links.append({
            'url': shortened_url,
            'original': original_url,
            'service': service_used
        })
    
    db.downloads_collection.insert_one({
        "user_id": query.from_user.id,
        "username": query.from_user.username or "Unknown",
        "software_id": ObjectId(software_id),
        "software_name": software['name'],
        "timestamp": datetime.now().isoformat(),
        "links_sent": shortened_links,
        "shorteners_used": [link['service'] for link in shortened_links]
    })
    
    db.software_collection.update_one(
        {"_id": ObjectId(software_id)},
        {"$inc": {"downloads_count": 1}}
    )
    
    db.users_collection.update_one(
        {"user_id": query.from_user.id},
        {
            "$push": {"downloads": ObjectId(software_id)},
            "$inc": {"total_downloads": 1}
        },
        upsert=True
    )
    
    download_msg = f"📦 **{software['name']}**\n\n"
    download_msg += f"💻 **{get_text(lang, 'os')}:** {', '.join(software['os'])}\n"
    download_msg += f"📏 **{get_text(lang, 'size')}:** {software['file_size']}\n"
    download_msg += f"⭐ **{get_text(lang, 'rating')}:** {software.get('average_rating', 0)}/5\n\n"
    download_msg += f"⬇️ **{get_text(lang, 'download_title')}:**\n\n"
    
    for i, link in enumerate(shortened_links, 1):
        emoji = "💰" if link['service'] == 'url2cash' else "💵" if link['service'] == 'adrinolinks' else "🔗"
        download_msg += f"{emoji} [{get_text(lang, 'download_link')} {i}]({link['url']})\n"
    
    download_msg += get_text(lang, 'download_instructions')
    
    alternatives = get_alternative_suggestions(ObjectId(software_id), db.software_collection, limit=3)
    
    if alternatives:
        download_msg += f"\n\n{get_text(lang, 'alternative_suggestions')}\n"
        for alt in alternatives:
            download_msg += f"• {alt['name']}\n"
    
    await query.message.edit_text(
        download_msg,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def handle_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    callback_data = query.data
    
    if callback_data.startswith('gamecat_'):
        category = callback_data.split('_', 1)[1]
        software_list = list(db.software_collection.find({
            "category": category,
            "is_game": True
        }).sort("downloads_count", -1).limit(10))
        not_found_msg = f"🎮 No games found in category: {category}"
    elif callback_data.startswith('softcat_'):
        category = callback_data.split('_', 1)[1]
        software_list = list(db.software_collection.find({
            "category": category,
            "is_game": {"$ne": True}
        }).sort("downloads_count", -1).limit(10))
        not_found_msg = f"💻 No software found in category: {category}"
    else:
        category = callback_data.split('_', 1)[1]
        software_list = list(db.software_collection.find({"category": category}).sort("downloads_count", -1).limit(10))
        not_found_msg = f"No items found in category: {category}"
    
    if not software_list:
        await query.message.edit_text(not_found_msg)
        return
    
    from handlers.user_commands import send_software_details
    
    for software in software_list:
        await send_software_details(update, software, lang, user_id)

async def handle_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    from utils.database import set_user_language
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    set_user_language(user_id, lang_code)
    
    await query.message.edit_text(get_text(lang_code, 'language_set'))

async def handle_rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    if query.data.startswith('rate_'):
        software_id = query.data.split('_')[1]
        
        keyboard = []
        for i in range(1, 6):
            keyboard.append([InlineKeyboardButton(
                f"{'⭐' * i} ({i} stars)", 
                callback_data=f"rating_{software_id}_{i}"
            )])
        
        await query.message.reply_text(
            get_text(lang, 'rate_software'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer()
    
    elif query.data.startswith('rating_'):
        parts = query.data.split('_')
        software_id = parts[1]
        rating = int(parts[2])
        
        existing_review = db.reviews_collection.find_one({
            "user_id": user_id,
            "software_id": ObjectId(software_id)
        })
        
        if existing_review:
            await query.answer(get_text(lang, 'already_rated'), show_alert=True)
            return
        
        db.reviews_collection.insert_one({
            "user_id": user_id,
            "software_id": ObjectId(software_id),
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        
        all_reviews = list(db.reviews_collection.find({"software_id": ObjectId(software_id)}))
        avg_rating = sum(r['rating'] for r in all_reviews) / len(all_reviews)
        
        db.software_collection.update_one(
            {"_id": ObjectId(software_id)},
            {
                "$set": {
                    "average_rating": avg_rating,
                    "reviews_count": len(all_reviews)
                }
            }
        )
        
        await query.answer(get_text(lang, 'thanks_rating'), show_alert=True)
        await query.message.edit_text(f"{get_text(lang, 'thanks_rating')}\n\n{'⭐' * rating}")

async def handle_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    software_id = ObjectId(query.data.split('_')[1])
    
    from utils.database import is_favorite, add_to_favorites, remove_from_favorites
    
    if is_favorite(user_id, software_id):
        remove_from_favorites(user_id, software_id)
        await query.answer(get_text(lang, 'remove_favorite'), show_alert=True)
    else:
        add_to_favorites(user_id, software_id)
        await query.answer(get_text(lang, 'add_favorite'), show_alert=True)

async def handle_nft_claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle NFT claim button callback"""
    query = update.callback_query
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    nft_id = query.data.split('_')[-1]
    
    # Attempt to claim the NFT (returns False if already claimed)
    claim_success = db.claim_nft(user_id, nft_id)
    
    if not claim_success:
        await query.answer("✅ You already claimed this NFT!", show_alert=True)
        return
    
    await query.answer("🎉 NFT marked as claimed! Check your wallet!", show_alert=True)
    
    await query.message.edit_text(
        f"✅ **NFT Claimed Successfully!**\n\n"
        f"🎨 You've claimed this NFT!\n"
        f"📦 Check your crypto wallet for the NFT.\n\n"
        f"💡 Use /claimnft to see all available NFTs!",
        parse_mode='Markdown'
    )
