import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    exit(1)

if not WEBHOOK_URL:
    print("❌ WEBHOOK_URL not found in environment variables!")
    print("Set it to your Vercel deployment URL + /api/webhook")
    print("Example: https://your-app.vercel.app/api/webhook")
    exit(1)

webhook_url = f"{WEBHOOK_URL}/api/webhook" if not WEBHOOK_URL.endswith('/api/webhook') else WEBHOOK_URL

print(f"🔄 Setting webhook to: {webhook_url}")

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={'url': webhook_url}
)

if response.status_code == 200:
    result = response.json()
    if result.get('ok'):
        print("✅ Webhook set successfully!")
        print(f"📍 URL: {webhook_url}")
    else:
        print(f"❌ Error: {result.get('description')}")
else:
    print(f"❌ HTTP Error: {response.status_code}")

info_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
if info_response.status_code == 200:
    info = info_response.json()
    print("\n📊 Webhook Info:")
    print(f"URL: {info['result'].get('url', 'Not set')}")
    print(f"Pending updates: {info['result'].get('pending_update_count', 0)}")
    if info['result'].get('last_error_message'):
        print(f"⚠️ Last error: {info['result']['last_error_message']}")
