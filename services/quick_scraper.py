"""
Quick scraper that works without AI - extracts info directly from listing pages
Perfect for category pages like https://www.apunkagames.com/action-games-for-pc
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)


def extract_category_from_url(url: str) -> Optional[str]:
    """Auto-detect category from URL patterns"""
    url_lower = url.lower()
    
    category_patterns = {
        'action': ['action-games', 'action/', '/action', 'aksiyon'],
        'adventure': ['adventure-games', 'adventure/', '/adventure', 'macera'],
        'racing': ['racing-games', 'racing/', '/racing', 'yaris'],
        'sports': ['sports-games', 'sports/', '/sports', 'spor'],
        'strategy': ['strategy-games', 'strategy/', '/strategy', 'strateji'],
        'rpg': ['rpg-games', 'rpg/', '/rpg', 'role-playing'],
        'shooter': ['shooter-games', 'shooter/', '/shooter', 'fps'],
        'simulation': ['simulation-games', 'simulation/', '/simulation', 'simulasyon'],
        'horror': ['horror-games', 'horror/', '/horror', 'korku'],
        'puzzle': ['puzzle-games', 'puzzle/', '/puzzle', 'bulmaca'],
        
        '3D Tools': ['3d-tools', '3dtools', '3d/', 'modeling'],
        'Activator': ['activator', 'activation', 'keygen'],
        'Audio': ['audio', 'sound', 'music', 'daw'],
        'Browser': ['browser', 'web-browser'],
        'Graphics': ['graphics', 'design', 'photo', 'image'],
        'Multimedia': ['multimedia', 'media', 'video'],
        'Office': ['office', 'productivity', 'word', 'excel'],
        'Security': ['security', 'antivirus', 'firewall', 'vpn'],
        'Utilities': ['utilities', 'tools', 'system'],
        'Video': ['video-editor', 'video/', 'editing'],
    }
    
    for category, patterns in category_patterns.items():
        for pattern in patterns:
            if pattern in url_lower:
                return category
    
    parts = url.strip('/').split('/')
    for part in reversed(parts):
        part_clean = part.replace('-', ' ').replace('_', ' ').title()
        if 3 < len(part_clean) < 30 and not part_clean.isdigit():
            return part_clean
    
    return None


def extract_download_links_from_html(html: str, base_url: str) -> List[str]:
    """Extract download links from HTML content"""
    soup = BeautifulSoup(html, 'html.parser')
    download_links = []
    
    link_patterns = [
        r'https?://.*apunkagameslinks\.com/vlink/.*',  # Apunkagames redirect links
        r'https?://(mediafire|mega|drive\.google|dropbox|uploadhaven|gofile|anonfiles|pixeldrain|krakenfiles|1fichier|sendspace|zippyshare|workupload)\..*',
        r'https?://.*?\.(exe|zip|rar|7z|iso|dmg|pkg|msi|apk|tar\.gz)(\?.*)?$',
        r'https?://.*?(download|dl|mirror|upload).*',
    ]
    
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '').strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
        
        full_url = urljoin(base_url, href)
        
        for pattern in link_patterns:
            if re.search(pattern, full_url, re.IGNORECASE):
                if full_url not in download_links and len(full_url) > 20:
                    download_links.append(full_url)
                break
    
    return download_links[:10]


def quick_scrape_listing_page(url: str, custom_category: Optional[str] = None) -> List[Dict]:
    """
    Quickly scrape a listing/category page without visiting individual articles
    Extracts info directly from the listing page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        auto_category = extract_category_from_url(url)
        # Comprehensive list of game site domains
        game_sites = ['apunkagames', 'pcgamestorrents', 'fitgirl-repacks', 'oceanofgames',
                     'skidrowreloaded', 'igg-games', 'steamunlocked', 'skidrowcodex',
                     'codexgames', 'cpygames', 'repack-games', 'gog-games', 'crohasit',
                     'downloadpcgames', 'pcgamesn', 'crackwatch', 'dodi-repacks']
        is_game_site = any(site in url.lower() for site in game_sites)
        item_type = 'game' if is_game_site else 'software'
        
        # Ensure game categories contain 'Games' for proper filtering
        if custom_category:
            category = custom_category
            if item_type == 'game' and 'game' not in category.lower():
                category = f"{category} Games"
        elif auto_category:
            category = auto_category
            if item_type == 'game' and 'game' not in category.lower():
                category = f"{category} Games"
        else:
            category = 'Games' if item_type == 'game' else 'Uncategorized'
        
        items = []
        
        # Special handling for apunkagames.com - multiple extraction methods
        if 'apunkagames.com' in url.lower():
            # Method 1: Try lcp_catlist (some category pages)
            game_list = soup.find('ul', class_='lcp_catlist')
            if game_list:
                list_items = game_list.find_all('li')
                logging.info(f"Found {len(list_items)} items in lcp_catlist")
                
                for li in list_items:
                    link = li.find('a', href=True)
                    if link:
                        title = link.get_text(strip=True)
                        item_url = link.get('href', '')
                        
                        if title and len(title) > 2:
                            items.append({
                                'name': title,
                                'type': item_type,
                                'version': 'Latest',
                                'category': category,
                                'file_size': 'Unknown',
                                'description': f"{title} - Free Download",
                                'download_links': [],
                                'source_url': item_url
                            })
                
                logging.info(f"✅ Extracted {len(items)} items from lcp_catlist")
                return items
            
            # Method 2: Extract from table structure (most category pages)
            all_tables = soup.find_all('table')
            logging.info(f"Found {len(all_tables)} tables on page")
            
            for table in all_tables:
                cells = table.find_all('td')
                for cell in cells:
                    # Find all links in the cell
                    links = cell.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        # Skip image links, only get text links
                        if not link.find('img'):
                            title = link.get_text(strip=True)
                            if title and len(title) > 2 and '.html' in href:
                                # Avoid duplicates
                                if not any(item['name'] == title for item in items):
                                    items.append({
                                        'name': title,
                                        'type': item_type,
                                        'version': 'Latest',
                                        'category': category,
                                        'file_size': 'Unknown',
                                        'description': f"{title} - Free Download",
                                        'download_links': [],
                                        'source_url': href
                                    })
            
            if items:
                logging.info(f"✅ Extracted {len(items)} items from table structure")
                return items
            
            # Method 3: Find all links with .html extension (fallback)
            all_links = soup.find_all('a', href=re.compile(r'\.html$'))
            logging.info(f"Found {len(all_links)} .html links as fallback")
            
            for link in all_links[:50]:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Filter out navigation, menu, and short titles
                if (title and len(title) > 3 and len(title) < 200 and
                    not any(skip in title.lower() for skip in ['home', 'menu', 'search', 'password', 'faqs', 'privacy', 'request'])):
                    
                    # Avoid duplicates
                    if not any(item['name'] == title for item in items):
                        items.append({
                            'name': title,
                            'type': item_type,
                            'version': 'Latest',
                            'category': category,
                            'file_size': 'Unknown',
                            'description': f"{title} - Free Download",
                            'download_links': [],
                            'source_url': href
                        })
            
            if items:
                logging.info(f"✅ Extracted {len(items)} items from .html links")
                return items
        
        # Default extraction logic for other sites
        article_containers = soup.find_all([
            'article',
            'div',
            'section',
            'li'
        ], class_=re.compile(
            r'(post|entry|item|game|software|product|card|article|bloghash-article)',
            re.IGNORECASE
        ))
        
        if not article_containers:
            article_containers = soup.find_all(['article', 'div'])[:50]
        
        logging.info(f"Found {len(article_containers)} potential items on page")
        
        seen_titles = set()
        
        for container in article_containers[:30]:
            try:
                title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                if not title_elem:
                    continue
                
                title_text = title_elem.get_text(strip=True)
                
                if len(title_text) < 3 or len(title_text) > 200:
                    continue
                
                if title_text.lower() in seen_titles:
                    continue
                seen_titles.add(title_text.lower())
                
                link_elem = title_elem.find('a', href=True) or container.find('a', href=True)
                item_url = ''
                if link_elem:
                    href = link_elem.get('href', '')
                    item_url = urljoin(url, href)
                
                version = 'Latest'
                version_patterns = [
                    r'v?(\d+\.\d+(?:\.\d+)?)',
                    r'(\d{4})',
                    r'(?:version|ver\.?)\s*(\d+(?:\.\d+)*)'
                ]
                for pattern in version_patterns:
                    match = re.search(pattern, title_text, re.IGNORECASE)
                    if match:
                        version = match.group(1)
                        break
                
                file_size = 'Unknown'
                size_elem = container.find(text=re.compile(r'\d+\s*(MB|GB|KB)', re.IGNORECASE))
                if size_elem:
                    size_match = re.search(r'(\d+(?:\.\d+)?\s*(?:MB|GB|KB))', str(size_elem), re.IGNORECASE)
                    if size_match:
                        file_size = size_match.group(1)
                
                description = ''
                desc_elem = container.find(['p', 'div'], class_=re.compile(r'(excerpt|summary|description|content)', re.IGNORECASE))
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:200]
                elif container.find('p'):
                    description = container.find('p').get_text(strip=True)[:200]
                
                if not description:
                    description = f"{title_text} - Download free"
                
                download_links = []
                
                items.append({
                    'name': title_text,
                    'type': item_type,
                    'version': version,
                    'category': category,
                    'file_size': file_size,
                    'description': description,
                    'download_links': download_links,
                    'source_url': item_url or url
                })
                
            except Exception as e:
                logging.debug(f"Error processing container: {str(e)}")
                continue
        
        logging.info(f"✅ Extracted {len(items)} items from listing page")
        return items
        
    except Exception as e:
        logging.error(f"Error scraping listing page: {str(e)}")
        return []


def quick_scrape_multiple_pages(base_url: str, max_pages: int, custom_category: Optional[str] = None) -> tuple[List[Dict], Optional[str]]:
    """
    Quickly scrape multiple pages without AI
    UNLIMITED pages supported - will continue until no more items found
    """
    all_items = []
    
    auto_category = extract_category_from_url(base_url)
    # Comprehensive list of game site domains
    game_sites = ['apunkagames', 'pcgamestorrents', 'fitgirl-repacks', 'oceanofgames',
                 'skidrowreloaded', 'igg-games', 'steamunlocked', 'skidrowcodex',
                 'codexgames', 'cpygames', 'repack-games', 'gog-games', 'crohasit',
                 'downloadpcgames', 'pcgamesn', 'crackwatch', 'dodi-repacks']
    is_game_site = any(site in base_url.lower() for site in game_sites)
    item_type = 'game' if is_game_site else 'software'
    
    # Ensure game categories contain 'Games' for proper filtering
    if custom_category:
        category = custom_category
        if item_type == 'game' and 'game' not in category.lower():
            category = f"{category} Games"
    elif auto_category:
        category = auto_category
        if item_type == 'game' and 'game' not in category.lower():
            category = f"{category} Games"
    else:
        category = 'Games' if item_type == 'game' else 'Uncategorized'
    
    logging.info(f"🚀 Quick scraping (NO AI) from {base_url}")
    logging.info(f"📂 Category: {category}")
    
    if max_pages == 0:
        logging.info(f"📄 UNLIMITED mode - will scrape until no items found")
    else:
        logging.info(f"📄 Pages to scrape: {max_pages}")
    
    page_num = 1
    consecutive_empty = 0
    
    while True:
        if max_pages > 0 and page_num > max_pages:
            logging.info(f"⏹️ Reached page limit: {max_pages}")
            break
        
        if page_num == 1:
            page_url = base_url
        else:
            # apunkagames.com uses /p2, /p3 format
            if 'apunkagames.com' in base_url.lower():
                if '/p' in base_url and re.search(r'/p\d+', base_url):
                    page_url = re.sub(r'/p\d+', f'/p{page_num}', base_url)
                elif base_url.endswith('/'):
                    page_url = f"{base_url}p{page_num}"
                else:
                    page_url = f"{base_url}/p{page_num}"
            # Standard /page/ format for other sites
            elif '/page/' in base_url:
                page_url = re.sub(r'/page/\d+', f'/page/{page_num}', base_url)
            elif base_url.endswith('/'):
                page_url = f"{base_url}page/{page_num}/"
            else:
                page_url = f"{base_url}/page/{page_num}/"
        
        logging.info(f"📄 Scraping page {page_num}: {page_url}")
        
        items = quick_scrape_listing_page(page_url, category)
        
        if items:
            all_items.extend(items)
            logging.info(f"✓ Page {page_num}: Found {len(items)} items (Total: {len(all_items)})")
            consecutive_empty = 0
        else:
            consecutive_empty += 1
            logging.warning(f"⚠️ Page {page_num}: No items found ({consecutive_empty} empty in a row)")
            if page_num > 1:
                logging.info(f"⏹️ Stopping - no more items found")
                break
        
        page_num += 1
        time.sleep(0.5)
    
    if not all_items:
        return [], "No items found on any page"
    
    logging.info(f"✅ Total items scraped: {len(all_items)}")
    return all_items, None
