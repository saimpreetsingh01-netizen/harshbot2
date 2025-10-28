"""
Full scraper that visits individual pages to extract complete information
Gets download links, descriptions, file sizes - NO screenshots to keep database small
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)


def extract_download_info_from_page(url: str) -> Dict:
    """
    Visit individual game/software page and extract complete information
    Returns: dict with download_links, description, file_size, version
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result = {
            'download_links': [],
            'description': '',
            'file_size': 'Unknown',
            'version': 'Latest'
        }
        
        # Extract download links
        download_link_patterns = [
            r'https?://.*apunkagameslinks\.com/vlink/.*',  # Apunkagames redirect links
            r'https?://(mediafire|mega|drive\.google|dropbox|uploadhaven|gofile|anonfiles|pixeldrain|krakenfiles|1fichier|sendspace|zippyshare|workupload)\..*',
            r'https?://.*?(download|dl|mirror).*',
        ]
        
        # Special handling for apunkagames - look for download buttons in specific areas
        if 'apunkagames.com' in url.lower():
            # Look for download buttons in post content areas
            all_buttons = soup.find_all('a', href=True)
            for btn in all_buttons:
                btn_text = btn.get_text(strip=True).lower()
                href = btn.get('href', '').strip() if btn.get('href') else ''
                
                # Look for the actual download button (apunkagameslinks.com/vlink/)
                if 'apunkagameslinks.com/vlink/' in href:
                    full_url = urljoin(url, href)
                    if full_url not in result['download_links']:
                        result['download_links'].append(full_url)
                # Or download buttons with text
                elif 'download this game' in btn_text or 'click here to download' in btn_text:
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Exclude navigation/help pages
                        if not any(skip in href.lower() for skip in ['how-to-download', 'winrar', 'password', 'faqs']):
                            full_url = urljoin(url, href)
                            for pattern in download_link_patterns:
                                if re.search(pattern, full_url, re.IGNORECASE):
                                    if full_url not in result['download_links']:
                                        result['download_links'].append(full_url)
                                    break
        
        # General download link extraction (skip if already found apunkagames links)
        if not result['download_links'] or 'apunkagames.com' not in url.lower():
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '').strip()
                text = link.get_text(strip=True).lower()
                
                # Skip navigation/help pages
                if any(skip in href.lower() for skip in ['how-to-download', 'winrar', 'password', 'faqs', 'privacy', 'game-request']):
                    continue
                
                # Common download button text
                if any(word in text for word in ['download', 'mirror', 'link', 'get']):
                    full_url = urljoin(url, href)
                    for pattern in download_link_patterns:
                        if re.search(pattern, full_url, re.IGNORECASE):
                            if full_url not in result['download_links']:
                                result['download_links'].append(full_url)
                            break
        
        # If no download links found, look for any external links
        if not result['download_links']:
            for link in all_links:
                href = link.get('href', '')
                full_url = urljoin(url, href)
                for pattern in download_link_patterns:
                    if re.search(pattern, full_url, re.IGNORECASE):
                        if full_url not in result['download_links'] and len(full_url) > 20:
                            result['download_links'].append(full_url)
                        if len(result['download_links']) >= 5:
                            break
        
        # Extract description
        desc_selectors = [
            ('div', {'class': re.compile(r'(content|description|entry|post-content)', re.I)}),
            ('div', {'id': re.compile(r'(content|description|entry)', re.I)}),
            ('article', {}),
            ('p', {})
        ]
        
        for tag, attrs in desc_selectors:
            elem = soup.find(tag, attrs)
            if elem:
                # Get text but exclude navigation, footer, etc.
                text = elem.get_text(separator=' ', strip=True)
                # Clean up
                text = re.sub(r'\s+', ' ', text)
                # Take first reasonable chunk
                if len(text) > 50:
                    result['description'] = text[:500]
                    break
        
        # Extract file size
        page_text = soup.get_text()
        size_patterns = [
            r'size[:\s]*(\d+(?:\.\d+)?\s*(?:GB|MB|KB))',
            r'(\d+(?:\.\d+)?\s*(?:GB|MB|KB))',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                result['file_size'] = match.group(1)
                break
        
        # Extract version
        version_patterns = [
            r'version[:\s]*v?(\d+\.\d+(?:\.\d+)?)',
            r'v(\d+\.\d+(?:\.\d+)?)',
            r'(\d{4})',  # Year
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                result['version'] = match.group(1)
                break
        
        return result
        
    except Exception as e:
        logging.error(f"Error extracting from {url}: {str(e)}")
        return {
            'download_links': [],
            'description': '',
            'file_size': 'Unknown',
            'version': 'Latest'
        }


def full_scrape_with_details(listing_url: str, max_pages: int, custom_category: Optional[str] = None) -> tuple[List[Dict], Optional[str]]:
    """
    Full scraping: Get list from category pages, then visit each page for details
    This is slower but gets complete information including download links
    """
    from services.quick_scraper import quick_scrape_multiple_pages, extract_category_from_url
    
    # First, get the list of items from category pages (fast)
    logging.info(f"🚀 Phase 1: Getting list of items from category pages...")
    items_list, error = quick_scrape_multiple_pages(listing_url, max_pages, custom_category)
    
    if error or not items_list:
        return items_list, error
    
    total_items = len(items_list)
    logging.info(f"📋 Found {total_items} items. Now fetching details from each page...")
    
    # Phase 2: Visit each page to get download links and details
    enhanced_items = []
    success_count = 0
    failed_count = 0
    
    for idx, item in enumerate(items_list, 1):
        try:
            source_url = item.get('source_url', '')
            if not source_url or source_url == listing_url:
                logging.warning(f"⚠️ [{idx}/{total_items}] No URL for {item['name']}, skipping...")
                failed_count += 1
                continue
            
            logging.info(f"📄 [{idx}/{total_items}] Fetching details: {item['name'][:50]}...")
            
            # Get detailed info from individual page
            details = extract_download_info_from_page(source_url)
            
            # Merge with existing item data
            item['download_links'] = details['download_links']
            
            # Update description if we got a better one
            if details['description'] and len(details['description']) > len(item.get('description', '')):
                item['description'] = details['description']
            
            # Update file size if found
            if details['file_size'] != 'Unknown':
                item['file_size'] = details['file_size']
            
            # Update version if found
            if details['version'] != 'Latest':
                item['version'] = details['version']
            
            enhanced_items.append(item)
            success_count += 1
            
            links_found = len(details['download_links'])
            logging.info(f"  ✓ Found {links_found} download link(s), size: {details['file_size']}")
            
            # Small delay to be respectful
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"  ✗ Error processing {item.get('name', 'unknown')}: {str(e)}")
            failed_count += 1
            # Still add the item even if details failed
            enhanced_items.append(item)
    
    logging.info(f"✅ Full scraping complete!")
    logging.info(f"  Success: {success_count}/{total_items}")
    logging.info(f"  Failed: {failed_count}/{total_items}")
    
    return enhanced_items, None
