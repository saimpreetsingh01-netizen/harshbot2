from openai import OpenAI
import os
import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import random

openrouter_clients = []
current_key_index = 0

def init_openrouter(api_keys_collection=None):
    """
    Initialize OpenRouter clients with API keys from database and environment
    Supports multiple API keys for load balancing and rate limit handling
    """
    global openrouter_clients, current_key_index
    openrouter_clients = []
    
    # Get API key from environment (primary)
    env_api_key = os.getenv('OPENROUTER_API')
    if env_api_key:
        try:
            client = OpenAI(
                api_key=env_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            openrouter_clients.append({
                'client': client,
                'api_key': env_api_key[:8] + '...',
                'source': 'environment',
                'active': True
            })
            print(f"✅ Loaded OpenRouter API key from environment")
        except Exception as e:
            print(f"❌ Error loading environment API key: {str(e)}")
    
    # Get additional API keys from database
    if api_keys_collection is not None:
        try:
            print(f"📊 Querying database for OpenRouter API keys...")
            db_keys = list(api_keys_collection.find({'service': 'openrouter', 'active': True}))
            print(f"📊 Found {len(db_keys)} active API key(s) in database")
            
            for key_doc in db_keys:
                try:
                    print(f"🔐 Loading key: {key_doc['api_key'][:8]}...")
                    client = OpenAI(
                        api_key=key_doc['api_key'],
                        base_url="https://openrouter.ai/api/v1"
                    )
                    openrouter_clients.append({
                        'client': client,
                        'api_key': key_doc['api_key'][:8] + '...',
                        'source': 'database',
                        'key_id': str(key_doc['_id']),
                        'active': True,
                        'added_by': key_doc.get('added_by', 'unknown')
                    })
                    print(f"✅ Loaded OpenRouter API key from database: {key_doc['api_key'][:8]}...")
                except Exception as e:
                    print(f"❌ Error loading database API key: {str(e)}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"❌ Error reading API keys from database: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️ api_keys_collection is None, cannot load database keys")
    
    current_key_index = 0
    print(f"🔑 Initialized {len(openrouter_clients)} OpenRouter API key(s)")
    return len(openrouter_clients) > 0

def get_next_openrouter_client():
    """
    Get next available OpenRouter client using round-robin rotation
    Returns None if no clients available
    """
    global current_key_index
    
    if not openrouter_clients:
        return None
    
    # Filter active clients
    active_clients = [c for c in openrouter_clients if c.get('active', True)]
    if not active_clients:
        return None
    
    # Round-robin selection
    client_data = active_clients[current_key_index % len(active_clients)]
    current_key_index = (current_key_index + 1) % len(active_clients)
    
    return client_data['client']

def ai_search_software(query, software_collection, language='en'):
    """
    AI-powered software search using OpenRouter (free models)
    Automatically rotates through available API keys and handles rate limits
    """
    client = get_next_openrouter_client()
    if not client:
        print("❌ No OpenRouter API clients available")
        print("💡 Please add an OpenRouter API key using /addapikey command")
        print("   Get free API key from: https://openrouter.ai/keys")
        return None
    
    all_software = list(software_collection.find().limit(100))
    
    if not all_software:
        return []
    
    software_list = "\n".join([
        f"{i+1}. {s['name']} - {s.get('description', 'N/A')} (Category: {s.get('category', 'N/A')}, OS: {', '.join(s.get('os', []))})"
        for i, s in enumerate(all_software)
    ])
    
    prompt = f"""You are an intelligent software search assistant. A user is searching for: "{query}"

Here is the available software catalog:
{software_list}

Based on the user's query, identify the most relevant software matches. Return ONLY a JSON array of software numbers (1-based index) that match the query, ordered by relevance.

Example response format: [1, 5, 12, 3]

If no software matches, return an empty array: []

Return only the JSON array, nothing else."""
    
    # Free models to try in order (fallback chain) - all verified working models
    free_models = [
        "qwen/qwen-2.5-7b-instruct:free",              # Fast and reliable
        "meta-llama/llama-3.2-3b-instruct:free",       # Good fallback  
        "google/gemini-flash-1.5:free",                # Google's free tier
        "mistralai/mistral-7b-instruct:free"           # Mistral fallback
    ]
    
    # Try with current client and different models if rate limited
    max_attempts = min(3, len(openrouter_clients))
    
    for attempt in range(max_attempts):
        chat_completion = None
        
        # Try each model in the fallback chain
        for model_name in free_models:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful software search assistant. Always respond with valid JSON arrays only. No explanations, no reasoning, just the JSON array."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=model_name,
                    temperature=0.1,
                    max_tokens=300
                )
                
                print(f"✅ Using model: {model_name}")
                break  # Success! Exit model loop
                
            except Exception as model_error:
                error_msg = str(model_error).lower()
                if 'rate' in error_msg or 'limit' in error_msg or '429' in error_msg:
                    print(f"⚠️ Model {model_name} rate-limited, trying next model...")
                    if model_name == free_models[-1]:  # Last model also failed
                        # All models failed, will trigger API key rotation below
                        chat_completion = None
                    continue  # Try next model
                elif '404' in error_msg or 'not found' in error_msg:
                    print(f"⚠️ Model {model_name} not found, trying next model...")
                    continue  # Try next model
                else:
                    # Other error (auth, etc.) - re-raise to handle in outer try/catch
                    raise model_error
        
        # If no model succeeded, try next API key
        if chat_completion is None:
            print(f"⚠️ All models rate-limited, trying next API key...")
            client = get_next_openrouter_client()
            if not client:
                print("❌ No more API keys available")
                return None
            continue
        
        try:
            
            response = chat_completion.choices[0].message.content.strip()
            
            #Debug print
            print(f"🔍 OpenRouter AI response: {response[:200]}")
            
            # Extract JSON array from response - handle various formats
            indices = None
            
            # Method 1: Try direct JSON parse first
            try:
                indices = json.loads(response)
                if isinstance(indices, list):
                    print(f"✅ Successfully parsed direct JSON array")
            except:
                pass
            
            # Method 2: Extract JSON array from text (handles reasoning models)
            if indices is None and '[' in response and ']' in response:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                json_str = response[json_start:json_end]
                try:
                    indices = json.loads(json_str)
                    if isinstance(indices, list):
                        print(f"✅ Extracted JSON array from response text")
                except:
                    pass
            
            # Method 3: Use regex to find number arrays (e.g., [1, 2, 3] or [1,2,3])
            if indices is None:
                import re
                array_pattern = r'\[[\s\d,]+\]'
                matches = re.findall(array_pattern, response)
                if matches:
                    try:
                        indices = json.loads(matches[0])
                        if isinstance(indices, list):
                            print(f"✅ Found JSON array using regex: {matches[0]}")
                    except:
                        pass
            
            # If still no valid array found, return empty results
            if indices is None or not isinstance(indices, list):
                print(f"⚠️ No valid JSON array found in response")
                print(f"📝 Full response: {response}")
                return []
            
            if not indices or indices == []:
                return []
            
            results = []
            for idx in indices:
                if 1 <= idx <= len(all_software):
                    results.append(all_software[idx - 1])
            
            return results
        
        except Exception as e:
            error_msg = str(e).lower()
            print(f"🔍 OpenRouter error: {str(e)}")
            
            if 'rate' in error_msg or 'limit' in error_msg or 'quota' in error_msg or '429' in error_msg:
                print(f"⚠️ Rate/Quota limit hit on API key, trying next one... (attempt {attempt + 1}/{max_attempts})")
                print(f"💡 Tip: OpenRouter free models have limits (20 req/min, 50 req/day)")
                print(f"   Add $10 credits to get 1000 req/day: https://openrouter.ai/credits")
                client = get_next_openrouter_client()
                if not client:
                    print("❌ No more API keys available")
                    print("💡 Add more API keys with /addapikey or wait for quota reset")
                    return None
                continue
            elif 'auth' in error_msg or 'key' in error_msg or '401' in error_msg or '403' in error_msg:
                print(f"❌ Authentication error: Invalid or expired API key")
                print(f"💡 Check your API key or add a new one with /addapikey")
                return None
            else:
                print(f"❌ AI search error: {str(e)}")
                print(f"💡 Check OpenRouter status at: https://status.openrouter.ai/")
                return None
    
    print("❌ All API keys exhausted or rate limited")
    print("💡 Solutions:")
    print("   1. Wait for quota reset (daily limits reset at 12:00 AM UTC)")
    print("   2. Add more OpenRouter API keys with /addapikey")
    print("   3. Add credits to your OpenRouter account for higher limits")
    return None

def get_alternative_suggestions(software_id, software_collection, limit=3):
    current_software = software_collection.find_one({"_id": software_id})
    
    if not current_software:
        return []
    
    category = current_software.get('category')
    os_list = current_software.get('os', [])
    
    query = {
        "_id": {"$ne": software_id},
        "category": category
    }
    
    if os_list:
        query["os"] = {"$in": os_list}
    
    alternatives = list(software_collection.find(query).sort("average_rating", -1).limit(limit))
    
    if len(alternatives) < limit:
        additional = list(software_collection.find({
            "_id": {"$ne": software_id},
            "category": category
        }).sort("downloads_count", -1).limit(limit - len(alternatives)))
        alternatives.extend(additional)
    
    return alternatives[:limit]

def web_search_and_extract(query):
    """
    Search the web for games/software and extract download information
    Returns a list of results with name, description, and download links
    """
    results = []
    
    try:
        # Search using DuckDuckGo HTML search with optimized query for download links
        search_query = f"download link of {query} pc game store"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Try DuckDuckGo search
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(search_query)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract search result links
        search_results = soup.find_all('a', class_='result__a', limit=5)
        
        for result in search_results:
            try:
                result_url = result.get('href', '')
                result_title = result.get_text(strip=True)
                
                # Fix relative URLs from DuckDuckGo (add https: scheme)
                if result_url.startswith('//'):
                    result_url = 'https:' + result_url
                elif not result_url.startswith('http'):
                    result_url = 'https://' + result_url
                
                # Skip non-game/software sites
                if not result_url or any(skip in result_url.lower() for skip in ['youtube', 'facebook', 'twitter', 'reddit']):
                    continue
                
                # Visit the page and extract download info
                page_response = requests.get(result_url, headers=headers, timeout=10)
                if page_response.status_code != 200:
                    continue
                
                page_soup = BeautifulSoup(page_response.content, 'html.parser')
                
                # Extract download links
                download_links = []
                download_patterns = [
                    r'https?://.*apunkagameslinks\.com/vlink/.*',
                    r'https?://(mediafire|mega|drive\.google|dropbox|uploadhaven|gofile)\..*',
                    r'https?://.*?(download|dl|mirror).*',
                ]
                
                all_links = page_soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    if 'download' in text or 'get' in text:
                        for pattern in download_patterns:
                            if re.search(pattern, href, re.IGNORECASE):
                                if href not in download_links and len(href) > 20:
                                    download_links.append(href)
                                break
                
                if download_links:
                    # Extract description
                    description = result_title
                    meta_desc = page_soup.find('meta', {'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        description = meta_desc.get('content', '')[:200]
                    
                    results.append({
                        'name': result_title,
                        'description': description,
                        'download_links': download_links[:3],  # Max 3 links
                        'source_url': result_url,
                        'file_size': 'Unknown',
                        'version': 'Latest',
                        'category': 'Web Search Result'
                    })
                    
                    # Stop after finding 3 good results
                    if len(results) >= 3:
                        break
                        
            except Exception as e:
                print(f"Error processing search result: {str(e)}")
                continue
        
        return results
        
    except Exception as e:
        print(f"Web search error: {str(e)}")
        return []
