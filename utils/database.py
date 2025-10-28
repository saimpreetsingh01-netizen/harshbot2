from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from datetime import datetime
import certifi

mongo_client = None
db = None
users_collection = None
software_collection = None
downloads_collection = None
reviews_collection = None
url_cache_collection = None
api_keys_collection = None
nfts_collection = None
game_scripts_collection = None
movies_collection = None

def init_database():
    global mongo_client, db, users_collection, software_collection, downloads_collection, reviews_collection, url_cache_collection, api_keys_collection, nfts_collection, game_scripts_collection, movies_collection
    
    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        raise Exception("MONGO_URI not found in environment variables")
    
    mongo_client = MongoClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        tlsCAFile=certifi.where()
    )
    db = mongo_client['telegram_bot']
    
    users_collection = db['users']
    software_collection = db['software']
    downloads_collection = db['downloads']
    reviews_collection = db['reviews']
    url_cache_collection = db['url_cache']
    api_keys_collection = db['api_keys']
    nfts_collection = db['nfts']
    game_scripts_collection = db['game_scripts']
    movies_collection = db['movies']
    
    users_collection.create_index("user_id", unique=True)
    software_collection.create_index("name")
    software_collection.create_index("category")
    downloads_collection.create_index("user_id")
    downloads_collection.create_index("software_id")
    reviews_collection.create_index([("user_id", 1), ("software_id", 1)], unique=True)
    api_keys_collection.create_index([("service", 1), ("api_key", 1)], unique=True)
    nfts_collection.create_index("nft_id", unique=True)
    game_scripts_collection.create_index("script_id", unique=True)
    movies_collection.create_index("movie_id", unique=True)
    
    return {
        'users': users_collection,
        'software': software_collection,
        'downloads': downloads_collection,
        'reviews': reviews_collection,
        'url_cache': url_cache_collection,
        'api_keys': api_keys_collection,
        'nfts': nfts_collection,
        'game_scripts': game_scripts_collection,
        'movies': movies_collection
    }

def get_collections():
    return {
        'users': users_collection,
        'software': software_collection,
        'downloads': downloads_collection,
        'reviews': reviews_collection,
        'url_cache': url_cache_collection,
        'api_keys': api_keys_collection,
        'nfts': nfts_collection,
        'game_scripts': game_scripts_collection,
        'movies': movies_collection
    }

def get_or_create_user(user_id, username=None, first_name=None, last_name=None, language='en'):
    user = users_collection.find_one({"user_id": user_id})
    
    if not user:
        user = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "language": language,
            "downloads": [],
            "favorites": [],
            "total_downloads": 0,
            "joined_at": datetime.now().isoformat()
        }
        users_collection.insert_one(user)
    else:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            }}
        )
    
    return users_collection.find_one({"user_id": user_id})

def get_user_language(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get('language', 'en') if user else 'en'

def set_user_language(user_id, language):
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"language": language}},
        upsert=True
    )

def add_to_favorites(user_id, software_id):
    users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"favorites": software_id}}
    )

def remove_from_favorites(user_id, software_id):
    users_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"favorites": software_id}}
    )

def is_favorite(user_id, software_id):
    user = users_collection.find_one({"user_id": user_id})
    if user and 'favorites' in user:
        return software_id in user['favorites']
    return False

# NFT Management Functions
def add_nft(nft_id, name, link, description=""):
    """Add a new NFT to the database"""
    nft = {
        "nft_id": nft_id,
        "name": name,
        "link": link,
        "description": description,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "claimed_count": 0
    }
    try:
        nfts_collection.insert_one(nft)
        return True
    except Exception as e:
        print(f"Error adding NFT: {e}")
        return False

def get_all_nfts():
    """Get all NFTs (for admin)"""
    return list(nfts_collection.find({}))

def get_active_nfts():
    """Get all active NFTs (for users)"""
    return list(nfts_collection.find({"active": True}))

def remove_nft(nft_id):
    """Remove an NFT from the database"""
    result = nfts_collection.delete_one({"nft_id": nft_id})
    return result.deleted_count > 0

def deactivate_nft(nft_id):
    """Deactivate an NFT (make it unavailable for claiming)"""
    result = nfts_collection.update_one(
        {"nft_id": nft_id},
        {"$set": {"active": False}}
    )
    return result.modified_count > 0

def activate_nft(nft_id):
    """Activate an NFT (make it available for claiming)"""
    result = nfts_collection.update_one(
        {"nft_id": nft_id},
        {"$set": {"active": True}}
    )
    return result.modified_count > 0

def claim_nft(user_id, nft_id):
    """Track that a user claimed an NFT"""
    # Add to user's claimed NFTs and check if it was actually added (not a duplicate)
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"claimed_nfts": nft_id}},
        upsert=True
    )
    
    # Only increment NFT claim counter if this was a NEW claim (modified_count > 0)
    # This prevents duplicate claims from inflating the counter
    if result.modified_count > 0 or result.upsert_id:
        nfts_collection.update_one(
            {"nft_id": nft_id},
            {"$inc": {"claimed_count": 1}}
        )
        return True
    
    return False  # User already claimed this NFT

def has_claimed_nft(user_id, nft_id):
    """Check if user has already claimed an NFT"""
    user = users_collection.find_one({"user_id": user_id})
    if user and 'claimed_nfts' in user:
        return nft_id in user['claimed_nfts']
    return False

def get_user_claimed_nfts(user_id):
    """Get all NFTs claimed by a user"""
    user = users_collection.find_one({"user_id": user_id})
    if user and 'claimed_nfts' in user:
        return user.get('claimed_nfts', [])
    return []

# Game Scripts Management Functions
def add_game_script(script_id, name, link, description=""):
    """Add a new game script to the database"""
    script = {
        "script_id": script_id,
        "name": name,
        "link": link,
        "description": description,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "views_count": 0
    }
    try:
        game_scripts_collection.insert_one(script)
        return True
    except Exception as e:
        print(f"Error adding game script: {e}")
        return False

def get_all_game_scripts():
    """Get all game scripts (for admin)"""
    return list(game_scripts_collection.find({}))

def get_active_game_scripts():
    """Get all active game scripts (for users)"""
    return list(game_scripts_collection.find({"active": True}))

def remove_game_script(script_id):
    """Remove a game script from the database"""
    result = game_scripts_collection.delete_one({"script_id": script_id})
    return result.deleted_count > 0

def deactivate_game_script(script_id):
    """Deactivate a game script (make it unavailable)"""
    result = game_scripts_collection.update_one(
        {"script_id": script_id},
        {"$set": {"active": False}}
    )
    return result.modified_count > 0

def activate_game_script(script_id):
    """Activate a game script (make it available)"""
    result = game_scripts_collection.update_one(
        {"script_id": script_id},
        {"$set": {"active": True}}
    )
    return result.modified_count > 0

def increment_script_views(script_id):
    """Increment the view count for a game script"""
    game_scripts_collection.update_one(
        {"script_id": script_id},
        {"$inc": {"views_count": 1}}
    )

def set_script_views(script_id, views_count):
    """Manually set the view count for a game script"""
    result = game_scripts_collection.update_one(
        {"script_id": script_id},
        {"$set": {"views_count": views_count}}
    )
    return result.modified_count > 0

# Movies Management Functions
def add_movie(movie_id, name, link, description=""):
    """Add a new movie to the database"""
    movie = {
        "movie_id": movie_id,
        "name": name,
        "link": link,
        "description": description,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "views_count": 0
    }
    try:
        movies_collection.insert_one(movie)
        return True
    except Exception as e:
        print(f"Error adding movie: {e}")
        return False

def save_scraped_movie(title, page_url, download_link, category=""):
    """Save a scraped movie to the database"""
    import hashlib
    # Create unique movie_id from page_url
    movie_id = hashlib.md5(page_url.encode()).hexdigest()[:16]
    
    movie = {
        "movie_id": movie_id,
        "title": title,
        "page_url": page_url,
        "download_link": download_link,
        "category": category,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "views_count": 0
    }
    try:
        # Use upsert to avoid duplicates
        movies_collection.update_one(
            {"movie_id": movie_id},
            {"$set": movie},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving scraped movie: {e}")
        return False

def search_movies(query, category=None, limit=10):
    """Search movies by title"""
    # Create case-insensitive regex search
    search_filter = {
        "title": {"$regex": query, "$options": "i"},
        "active": True
    }
    
    if category:
        search_filter["category"] = category.upper()
    
    movies = list(movies_collection.find(search_filter).limit(limit))
    return movies

def get_movies_by_category(category, limit=10):
    """Get movies from a specific category"""
    movies = list(movies_collection.find({
        "category": category.upper(),
        "active": True
    }).limit(limit))
    return movies

def count_movies_by_category(category=None):
    """Count movies in database, optionally filtered by category"""
    if category:
        return movies_collection.count_documents({"category": category.upper()})
    return movies_collection.count_documents({})

def get_all_movies():
    """Get all movies (for admin)"""
    return list(movies_collection.find({}))

def get_active_movies():
    """Get all active movies (for users)"""
    return list(movies_collection.find({"active": True}))

def remove_movie(movie_id):
    """Remove a movie from the database"""
    result = movies_collection.delete_one({"movie_id": movie_id})
    return result.deleted_count > 0

def deactivate_movie(movie_id):
    """Deactivate a movie (make it unavailable)"""
    result = movies_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {"active": False}}
    )
    return result.modified_count > 0

def activate_movie(movie_id):
    """Activate a movie (make it available)"""
    result = movies_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {"active": True}}
    )
    return result.modified_count > 0

def increment_movie_views(movie_id):
    """Increment the view count for a movie"""
    movies_collection.update_one(
        {"movie_id": movie_id},
        {"$inc": {"views_count": 1}}
    )

def set_movie_views(movie_id, views_count):
    """Manually set the view count for a movie"""
    result = movies_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {"views_count": views_count}}
    )
    return result.modified_count > 0
