import requests
import hashlib
from datetime import datetime
import os

URL2CASH_API = os.getenv('URL2CASH_API', 'Ns7bGKR9fD2037H3XhI9Ab3chw8BbDdA4b4C')
ADRINOLINKS_API = os.getenv('ADRINOLINKS_API', '730eb23c10b70ba35d1a7d1d210c5cada3b2dab3')

shortener_counter = {'url2cash': 0, 'adrinolinks': 0}

def shorten_url2cash(original_url):
    try:
        api_url = f"https://url2cash.in/api?api={URL2CASH_API}&url={original_url}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['shortenedUrl']
            else:
                print(f"URL2cash error: {data.get('message', 'Unknown error')}")
                return original_url
        else:
            print(f"URL2cash HTTP {response.status_code}")
            return original_url
    except Exception as e:
        print(f"URL2cash exception: {str(e)}")
        return original_url

def shorten_adrinolinks(original_url):
    try:
        api_url = f"https://adrinolinks.in/api?api={ADRINOLINKS_API}&url={original_url}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['shortenedUrl']
            else:
                print(f"AdrinoLinks error: {data.get('message', 'Unknown error')}")
                return original_url
        else:
            print(f"AdrinoLinks HTTP {response.status_code}")
            return original_url
    except Exception as e:
        print(f"AdrinoLinks exception: {str(e)}")
        return original_url

def get_from_cache(original_url, url_cache_collection):
    cache_key = hashlib.md5(original_url.encode()).hexdigest()
    cached = url_cache_collection.find_one({"cache_key": cache_key})
    
    if cached:
        url_cache_collection.update_one(
            {"cache_key": cache_key},
            {"$inc": {"usage_count": 1}}
        )
        return cached
    return None

def save_to_cache(original_url, shortened_url, service, url_cache_collection):
    cache_key = hashlib.md5(original_url.encode()).hexdigest()
    url_cache_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {
            "original_url": original_url,
            "shortened_url": shortened_url,
            "service": service,
            "created_at": datetime.now().isoformat(),
            "usage_count": 1
        }},
        upsert=True
    )

def shorten_url(original_url, url_cache_collection):
    global shortener_counter
    
    cached = get_from_cache(original_url, url_cache_collection)
    if cached:
        return cached['shortened_url'], 'cached'
    
    # Prioritize AdRINo first
    if shortener_counter['adrinolinks'] <= shortener_counter['url2cash']:
        shortened_url = shorten_adrinolinks(original_url)
        service_used = 'adrinolinks'
        shortener_counter['adrinolinks'] += 1
    else:
        shortened_url = shorten_url2cash(original_url)
        service_used = 'url2cash'
        shortener_counter['url2cash'] += 1
    
    save_to_cache(original_url, shortened_url, service_used, url_cache_collection)
    return shortened_url, service_used
