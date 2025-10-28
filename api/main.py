from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
import os
import json
import hashlib
import hmac
from urllib.parse import parse_qsl
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database utilities
import sys
sys.path.append('..')
from utils.database import (
    software_collection, movies_collection, nfts_collection,
    game_scripts_collection, users_collection, downloads_collection,
    init_database
)
from services.url_shortener import shorten_url

# Initialize database
init_database()

app = FastAPI(title="Telegram Mini App API")

# CORS configuration for Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

def verify_telegram_webapp_data(init_data: str) -> Optional[Dict]:
    """
    Verify Telegram WebApp init data
    Returns user data if valid, None if invalid
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
        
        # Extract hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return None
        
        # Create data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate hash
        secret_key = hmac.new(
            "WebAppData".encode(),
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify hash
        if calculated_hash != received_hash:
            return None
        
        # Parse user data
        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data
    except Exception as e:
        print(f"Error verifying webapp data: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "Telegram Mini App API", "status": "online"}

@app.get("/api/games")
async def get_games(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get games with optional filtering"""
    try:
        query = {"category": {"$regex": "game", "$options": "i"}}
        
        if category and category != "all":
            query["category"] = {"$regex": category, "$options": "i"}
        
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        
        skip = (page - 1) * limit
        
        games = list(software_collection.find(query)
                    .sort("downloads_count", -1)
                    .skip(skip)
                    .limit(limit))
        
        total = software_collection.count_documents(query)
        
        # Convert ObjectId to string
        for game in games:
            game['_id'] = str(game['_id'])
        
        return {
            "games": games,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/software")
async def get_software(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get software with optional filtering"""
    try:
        query = {}
        
        if category and category != "all":
            query["category"] = {"$regex": category, "$options": "i"}
        
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        
        skip = (page - 1) * limit
        
        software = list(software_collection.find(query)
                       .sort("downloads_count", -1)
                       .skip(skip)
                       .limit(limit))
        
        total = software_collection.count_documents(query)
        
        # Convert ObjectId to string
        for item in software:
            item['_id'] = str(item['_id'])
        
        return {
            "software": software,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies")
async def get_movies(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get movies with optional filtering"""
    try:
        query = {}
        
        if category and category != "all":
            query["category"] = category.upper()
        
        if search:
            query["title"] = {"$regex": search, "$options": "i"}
        
        skip = (page - 1) * limit
        
        movies = list(movies_collection.find(query)
                     .sort("date_added", -1)
                     .skip(skip)
                     .limit(limit))
        
        total = movies_collection.count_documents(query)
        
        # Convert ObjectId to string
        for movie in movies:
            movie['_id'] = str(movie['_id'])
        
        return {
            "movies": movies,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nfts")
async def get_nfts():
    """Get all available NFTs"""
    try:
        nfts = list(nfts_collection.find({"active": True}))
        
        # Convert ObjectId to string
        for nft in nfts:
            nft['_id'] = str(nft['_id'])
        
        return {"nfts": nfts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gamescripts")
async def get_game_scripts():
    """Get all game scripts"""
    try:
        scripts = list(game_scripts_collection.find({"active": True}).sort("views", -1))
        
        # Convert ObjectId to string
        for script in scripts:
            script['_id'] = str(script['_id'])
        
        return {"scripts": scripts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/profile")
async def get_user_profile(authorization: str = Header(None)):
    """Get user profile with download history and favorites"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_data = verify_telegram_webapp_data(authorization)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authorization")
        
        user_id = user_data.get('id')
        user = users_collection.find_one({"user_id": user_id})
        
        if not user:
            # Create user if doesn't exist
            user = {
                "user_id": user_id,
                "username": user_data.get('username'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "language": "en",
                "total_downloads": 0,
                "downloads": [],
                "favorites": [],
                "date_joined": datetime.now().isoformat()
            }
            users_collection.insert_one(user)
        
        # Get download history
        downloads = list(downloads_collection.find({"user_id": user_id})
                        .sort("timestamp", -1)
                        .limit(50))
        
        for download in downloads:
            download['_id'] = str(download['_id'])
            if 'software_id' in download:
                download['software_id'] = str(download['software_id'])
        
        # Get favorites
        favorite_ids = user.get('favorites', [])
        favorites = []
        if favorite_ids:
            favorites = list(software_collection.find({"_id": {"$in": favorite_ids}}))
            for fav in favorites:
                fav['_id'] = str(fav['_id'])
        
        user['_id'] = str(user['_id'])
        
        return {
            "user": user,
            "downloads": downloads,
            "favorites": favorites
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/download/{item_id}")
async def create_download(item_id: str, authorization: str = Header(None)):
    """Create download record and return shortened links"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_data = verify_telegram_webapp_data(authorization)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authorization")
        
        user_id = user_data.get('id')
        
        # Get item from database
        item = software_collection.find_one({"_id": ObjectId(item_id)})
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        original_links = item.get('download_links', [])
        
        if not original_links:
            raise HTTPException(status_code=404, detail="No download links available")
        
        # Shorten URLs
        from utils.database import url_cache_collection
        shortened_links = []
        
        for link_obj in original_links[:5]:
            original_url = link_obj['url'] if isinstance(link_obj, dict) else link_obj
            shortened_url, service_used = shorten_url(original_url, url_cache_collection)
            
            shortened_links.append({
                'url': shortened_url,
                'original': original_url,
                'service': service_used
            })
        
        # Record download
        downloads_collection.insert_one({
            "user_id": user_id,
            "username": user_data.get('username', 'Unknown'),
            "software_id": ObjectId(item_id),
            "software_name": item['name'],
            "timestamp": datetime.now().isoformat(),
            "links_sent": shortened_links,
            "shorteners_used": [link['service'] for link in shortened_links]
        })
        
        # Update counters
        software_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$inc": {"downloads_count": 1}}
        )
        
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"downloads": ObjectId(item_id)},
                "$inc": {"total_downloads": 1}
            },
            upsert=True
        )
        
        return {"links": shortened_links}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get all available categories"""
    try:
        # Get software categories
        software_categories = software_collection.distinct("category")
        
        # Get movie categories
        movie_categories = [
            "NETFLIX", "PRIME", "HOTSTAR", "HINDI", "ENGLISH",
            "TAMIL", "TELUGU", "MALAYALAM", "KANNADA",
            "BOLLYWOOD", "HOLLYWOOD", "SOUTH", "WEB-SERIES"
        ]
        
        return {
            "software": sorted(software_categories),
            "movies": movie_categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
