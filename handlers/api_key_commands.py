from telegram import Update
from telegram.ext import ContextTypes
import os
from datetime import datetime
import utils.database as db
from services.ai_service import init_openrouter, openrouter_clients

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

async def add_api_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add a new OpenRouter API key to the system
    Usage: /addapikey <api_key>
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Add OpenRouter API Key**\n\n"
            "**Usage:**\n"
            "`/addapikey <your_openrouter_api_key>`\n\n"
            "**Example:**\n"
            "`/addapikey sk-or-v1-abc123xyz456...`\n\n"
            "💡 Get your API key from https://openrouter.ai/keys",
            parse_mode='Markdown'
        )
        return
    
    api_key = context.args[0].strip()
    
    if not api_key.startswith('sk-'):
        await update.message.reply_text(
            "❌ Invalid API key format!\n"
            "OpenRouter API keys should start with 'sk-'"
        )
        return
    
    try:
        # Check if database is initialized
        if db.api_keys_collection is None:
            await update.message.reply_text(
                "❌ **Database Error!**\n\n"
                "The database is not properly initialized.\n"
                "Please restart the bot or contact the developer."
            )
            return
        
        # Check if key already exists
        existing = db.api_keys_collection.find_one({
            'service': 'openrouter',
            'api_key': api_key
        })
        
        if existing:
            await update.message.reply_text(
                "⚠️ This API key is already in the system!\n"
                f"Added by: {existing.get('added_by', 'Unknown')}\n"
                f"Added at: {existing.get('added_at', 'Unknown')}\n"
                f"Status: {'🟢 Active' if existing.get('active', True) else '🔴 Inactive'}"
            )
            return
        
        # Add new API key
        key_doc = {
            'service': 'openrouter',
            'api_key': api_key,
            'added_by': update.effective_user.id,
            'added_at': datetime.now().isoformat(),
            'active': True,
            'usage_count': 0,
            'last_used': None
        }
        
        result = db.api_keys_collection.insert_one(key_doc)
        
        print(f"🔄 Reinitializing OpenRouter clients after adding key...")
        # Reinitialize OpenRouter clients
        success = init_openrouter(db.api_keys_collection)
        print(f"🔄 Reinitialization complete. Success: {success}")
        
        await update.message.reply_text(
            "✅ **API Key Added Successfully!**\n\n"
            f"🔑 **Key:** `{api_key[:8]}...{api_key[-4:]}`\n"
            f"👤 **Added by:** {update.effective_user.first_name}\n"
            f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"🔢 **ID:** `{str(result.inserted_id)}`\n\n"
            f"🔄 **Total active keys:** {len([c for c in openrouter_clients if c.get('active', True)])}\n\n"
            "💡 The bot will now use this key in rotation with others for load balancing!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown database error"
        import traceback
        print(f"Error adding API key: {error_msg}")
        print(traceback.format_exc())
        
        await update.message.reply_text(
            f"❌ **Error adding API key**\n\n"
            f"Error details: {error_msg}\n\n"
            "Common fixes:\n"
            "• Make sure your API key is valid (get from https://openrouter.ai/keys)\n"
            "• Check that the database is connected\n"
            "• Try again in a moment\n\n"
            "If the problem persists, contact the developer."
        )

async def list_api_keys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    List all OpenRouter API keys in the system
    Usage: /listapikeys
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    try:
        # Get all OpenRouter keys from database
        db_keys = list(db.api_keys_collection.find({'service': 'openrouter'}))
        
        # Get environment key
        env_key = os.getenv('OPENROUTER_API')
        
        msg = "🔑 **OpenRouter API Keys**\n\n"
        
        # Environment key
        if env_key:
            msg += "**📌 Environment Key:**\n"
            msg += f"└ `{env_key[:8]}...{env_key[-4:]}`\n"
            msg += f"  Status: 🟢 Active (Primary)\n\n"
        
        # Database keys
        if db_keys:
            msg += f"**💾 Database Keys ({len(db_keys)}):**\n\n"
            for idx, key in enumerate(db_keys, 1):
                status_icon = "🟢" if key.get('active', True) else "🔴"
                msg += f"{idx}. `{key['api_key'][:8]}...{key['api_key'][-4:]}`\n"
                msg += f"   Status: {status_icon} {'Active' if key.get('active', True) else 'Inactive'}\n"
                msg += f"   Added by: {key.get('added_by', 'Unknown')}\n"
                msg += f"   Usage: {key.get('usage_count', 0)} times\n"
                msg += f"   ID: `{str(key['_id'])}`\n\n"
        else:
            msg += "**💾 Database Keys:**\n"
            msg += "└ No keys in database\n\n"
        
        # Current status
        active_count = len([c for c in openrouter_clients if c.get('active', True)])
        msg += f"**📊 Current Status:**\n"
        msg += f"└ Active clients: {active_count}\n"
        msg += f"└ Load balancing: {'✅ Enabled' if active_count > 1 else '⚠️ Single key'}\n\n"
        
        msg += "**Commands:**\n"
        msg += "`/addapikey <key>` - Add new key\n"
        msg += "`/removeapikey <key_id>` - Remove key\n"
        msg += "`/toggleapikey <key_id>` - Enable/disable key"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error listing API keys: {str(e)}"
        )

async def remove_api_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove an OpenRouter API key from the system
    Usage: /removeapikey <key_id>
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Remove API Key**\n\n"
            "**Usage:**\n"
            "`/removeapikey <key_id>`\n\n"
            "Use `/listapikeys` to see all key IDs",
            parse_mode='Markdown'
        )
        return
    
    key_id = context.args[0].strip()
    
    try:
        from bson import ObjectId
        
        # Find and delete the key
        result = db.api_keys_collection.delete_one({
            '_id': ObjectId(key_id),
            'service': 'openrouter'
        })
        
        if result.deleted_count > 0:
            # Reinitialize OpenRouter clients
            init_openrouter(db.api_keys_collection)
            
            await update.message.reply_text(
                "✅ **API Key Removed Successfully!**\n\n"
                f"🔑 Key ID: `{key_id}`\n"
                f"🔄 Remaining active keys: {len([c for c in openrouter_clients if c.get('active', True)])}\n\n"
                "💡 The bot has been updated with the remaining keys.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ API key not found!\n\n"
                "Use `/listapikeys` to see all available keys.",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error removing API key: {str(e)}\n\n"
            "Make sure the key ID is correct."
        )

async def toggle_api_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Toggle an API key active/inactive status
    Usage: /toggleapikey <key_id>
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **Toggle API Key Status**\n\n"
            "**Usage:**\n"
            "`/toggleapikey <key_id>`\n\n"
            "Use `/listapikeys` to see all key IDs",
            parse_mode='Markdown'
        )
        return
    
    key_id = context.args[0].strip()
    
    try:
        from bson import ObjectId
        
        # Find the key
        key_doc = db.api_keys_collection.find_one({
            '_id': ObjectId(key_id),
            'service': 'openrouter'
        })
        
        if not key_doc:
            await update.message.reply_text(
                "❌ API key not found!\n\n"
                "Use `/listapikeys` to see all available keys.",
                parse_mode='Markdown'
            )
            return
        
        # Toggle active status
        new_status = not key_doc.get('active', True)
        
        db.api_keys_collection.update_one(
            {'_id': ObjectId(key_id)},
            {'$set': {'active': new_status}}
        )
        
        # Reinitialize OpenRouter clients
        init_openrouter(db.api_keys_collection)
        
        status_text = "🟢 Active" if new_status else "🔴 Inactive"
        
        await update.message.reply_text(
            "✅ **API Key Status Updated!**\n\n"
            f"🔑 Key: `{key_doc['api_key'][:8]}...{key_doc['api_key'][-4:]}`\n"
            f"📊 New status: {status_text}\n"
            f"🔄 Active keys: {len([c for c in openrouter_clients if c.get('active', True)])}\n\n"
            "💡 The bot has been updated with the new configuration.",
            parse_mode='Markdown'
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error toggling API key: {str(e)}\n\n"
            "Make sure the key ID is correct."
        )

async def apikey_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show API key usage statistics
    Usage: /apikeystats
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command!")
        return
    
    try:
        # Get all keys
        all_keys = list(db.api_keys_collection.find({'service': 'openrouter'}))
        
        msg = "📊 **API Key Statistics**\n\n"
        
        if not all_keys:
            msg += "No API keys in database.\n"
            msg += "Environment key is being used (if configured).\n\n"
        else:
            total_usage = sum(key.get('usage_count', 0) for key in all_keys)
            active_keys = [k for k in all_keys if k.get('active', True)]
            
            msg += f"**Overview:**\n"
            msg += f"└ Total keys: {len(all_keys)}\n"
            msg += f"└ Active keys: {len(active_keys)}\n"
            msg += f"└ Total API calls: {total_usage}\n\n"
            
            msg += "**Per Key Usage:**\n\n"
            for idx, key in enumerate(sorted(all_keys, key=lambda x: x.get('usage_count', 0), reverse=True), 1):
                status_icon = "🟢" if key.get('active', True) else "🔴"
                msg += f"{idx}. {status_icon} `{key['api_key'][:8]}...`\n"
                msg += f"   Calls: {key.get('usage_count', 0)}\n"
                msg += f"   Last used: {key.get('last_used', 'Never')}\n\n"
        
        # Current loaded clients
        msg += f"**🔄 Currently Loaded:**\n"
        msg += f"└ Active clients: {len([c for c in openrouter_clients if c.get('active', True)])}\n"
        msg += f"└ Rotation: Round-robin\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error getting statistics: {str(e)}"
        )
