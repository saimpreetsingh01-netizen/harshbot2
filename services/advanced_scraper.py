import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from groq import Groq
import os
import json
import re
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 20):
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = None
    
    def wait_if_needed(self):
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

class AdvancedScraper:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=20)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=8'
        })
        
        GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    
    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        self.rate_limiter.wait_if_needed()
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def detect_pagination_urls(self, soup: BeautifulSoup, base_url: str, max_pages: int) -> List[str]:
        """Intelligently detect pagination URLs from the page"""
        urls = [base_url]
        
        pagination_patterns = [
            r'/page/(\d+)/?',
            r'\?page=(\d+)',
            r'[?&]currentPage=(\d+)',
            r'/p(\d+)/?',
            r'\?p=(\d+)',
            r'[?&]paged=(\d+)',
            r'/(\d+)/?$'
        ]
        
        page_links = soup.find_all('a', href=True)
        detected_urls = {}
        detected_pattern = None
        
        for link in page_links:
            href = link.get('href', '')
            if not isinstance(href, str):
                continue
            full_url = urljoin(base_url, href)
            
            for pattern in pagination_patterns:
                match = re.search(pattern, full_url)
                if match:
                    page_num = int(match.group(1))
                    if 2 <= page_num <= 10:
                        detected_urls[page_num] = full_url
                        if not detected_pattern:
                            detected_pattern = pattern
        
        if detected_urls:
            for page in range(2, max_pages + 1):
                if page in detected_urls:
                    urls.append(detected_urls[page])
                else:
                    sample_url = list(detected_urls.values())[0]
                    for i in range(2, 11):
                        if i in detected_urls:
                            template_url = re.sub(detected_pattern, lambda m: m.group(0).replace(str(i), '{}'), detected_urls[i])
                            urls.append(template_url.format(page))
                            break
        
        return urls[:max_pages]
    
    def find_article_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Universal article link finder - works with any website structure"""
        articles = []
        
        article_containers = soup.find_all([
            'article',
            'div',
            'section',
            'li'
        ], class_=re.compile(
            r'(post|entry|item|game|software|product|card|article|content-item|list-item|bloghash)',
            re.IGNORECASE
        ))
        
        if not article_containers:
            article_containers = soup.find_all(['article', 'div', 'section'])
        
        logging.info(f"Found {len(article_containers)} potential article containers")
        
        seen_urls = set()
        
        for container in article_containers[:50]:
            try:
                title_elem = None
                link_elem = None
                
                title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5'], class_=re.compile(r'(entry-title|post-title|title)', re.IGNORECASE))
                if title_elem:
                    link_elem = title_elem.find('a', href=True)
                
                if not link_elem:
                    for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        title_elem = container.find(heading_tag)
                        if title_elem:
                            link_elem = title_elem.find('a', href=True)
                            if link_elem:
                                break
                
                if not link_elem:
                    link_elem = container.find('a', class_=re.compile(r'(entry-image-link|post-link|permalink)', re.IGNORECASE), href=True)
                
                if not link_elem:
                    link_elem = container.find('a', href=True)
                
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if not href or not isinstance(href, str):
                    continue
                if href.startswith('#'):
                    continue
                
                full_url = urljoin(base_url, href)
                
                if full_url in seen_urls:
                    continue
                
                parsed = urlparse(full_url)
                if parsed.netloc and parsed.netloc != urlparse(base_url).netloc:
                    continue
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    title = link_elem.get_text(strip=True) or link_elem.get('title', '') or 'Untitled'
                
                if len(title) < 3 or len(title) > 200:
                    continue
                
                exclude_keywords = ['category', 'tag', 'author', 'search', '/page/', 'comments', 'feed', 'login', 'register']
                if not any(keyword in full_url.lower() for keyword in exclude_keywords):
                    articles.append({
                        'title': title[:150],
                        'url': full_url
                    })
                    seen_urls.add(full_url)
                
            except Exception as e:
                logging.debug(f"Error processing container: {str(e)}")
                continue
        
        logging.info(f"Extracted {len(articles)} unique article links")
        return articles
    
    def extract_content_from_article(self, soup: BeautifulSoup) -> str:
        """Extract main content from article page - universal method"""
        content_selectors = [
            {'name': 'div', 'class': re.compile(r'(content|entry-content|post-content|article-content|main-content)', re.IGNORECASE)},
            {'name': 'article', 'class': re.compile(r'(content|post|entry)', re.IGNORECASE)},
            {'name': 'div', 'id': re.compile(r'(content|main|post)', re.IGNORECASE)},
            {'name': 'main'},
            {'name': 'article'},
        ]
        
        for selector in content_selectors:
            content = soup.find(**selector)
            if content:
                for unwanted in content.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                    unwanted.decompose()
                
                text = str(content)[:15000]
                if len(text) > 500:
                    return text
        
        body = soup.find('body')
        if body:
            for unwanted in body.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                unwanted.decompose()
            return str(body)[:15000]
        
        return str(soup)[:15000]
    
    def organize_with_ai(self, items_data: List[Dict]) -> List[Dict]:
        """Use AI to organize all scraped data and extract information"""
        if not self.groq_client or not items_data:
            return []
        
        batch_size = 10
        all_results = []
        
        for i in range(0, len(items_data), batch_size):
            batch = items_data[i:i+batch_size]
            
            items_text = ""
            for idx, item in enumerate(batch, 1):
                truncated_html = item['html'][:3000]
                items_text += f"\n--- ITEM {idx} ---\nTitle: {item['title']}\nURL: {item['url']}\nHTML snippet:\n{truncated_html}\n\n"
            
            prompt = f"""Extract software/game information from the following items. For each item, extract:

Return ONLY a valid JSON array where each object has these exact fields:
{{
  "name": "full name of the software/game",
  "type": "game" or "software" (determine from content - games are video games, software is applications/tools)",
  "version": "version number if found, else 'Latest'",
  "category": "category/genre - for games: Action, Adventure, Racing, RPG, Sports, Strategy, etc. For software: Video, Graphics, Utilities, Productivity, Security, etc.",
  "file_size": "file size with unit if found (e.g., 2GB, 500MB), else 'Unknown'",
  "description": "brief description from the content (max 200 chars)",
  "download_links": ["extract ALL download URLs from HTML - look for links containing: mediafire, mega, drive.google, dropbox, direct file links (.exe, .zip, .rar), uploadhaven, etc."]
}}

IMPORTANT RULES:
1. Set "type" to "game" if it's a video game, or "software" if it's an application/program/tool
2. Extract ACTUAL download URLs from the HTML (look for mediafire, mega, google drive, dropbox, direct links, etc.)
3. Category must be specific (not just "Game" or "Software")
4. Return array of {len(batch)} objects in the same order as items
5. If you can't find download links in the HTML, return empty array for download_links

Items to extract:
{items_text}

Return ONLY the JSON array, no explanations:"""
            
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a data extraction expert. Always respond with valid JSON array only. No markdown, no explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    max_tokens=8000
                )
                
                response_text = chat_completion.choices[0].message.content
                if response_text:
                    response_text = response_text.strip()
                else:
                    response_text = "[]"
                
                response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group()
                
                data_list = json.loads(response_text)
                
                for idx, data in enumerate(data_list):
                    if i + idx < len(items_data):
                        data['source_url'] = items_data[i + idx]['url']
                
                all_results.extend(data_list)
                logging.info(f"✓ AI processed batch {i//batch_size + 1}, extracted {len(data_list)} items")
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"AI organization error for batch {i//batch_size + 1}: {str(e)}")
                continue
        
        return all_results
    
    def scrape_page_raw(self, url: str) -> List[Dict]:
        """Scrape raw data from a page - universal method"""
        soup = self.get_soup(url)
        if not soup:
            return []
        
        articles = self.find_article_links(soup, url)
        
        if not articles:
            logging.warning(f"No articles found on {url}")
            return []
        
        raw_items = []
        
        for article in articles[:15]:
            try:
                logging.info(f"📥 Scraping: {article['title']}")
                
                article_soup = self.get_soup(article['url'])
                if not article_soup:
                    continue
                
                content_html = self.extract_content_from_article(article_soup)
                
                if content_html and len(content_html) > 300:
                    raw_items.append({
                        'title': article['title'],
                        'url': article['url'],
                        'html': content_html
                    })
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error collecting article {article.get('title', 'Unknown')}: {str(e)}")
                continue
        
        logging.info(f"✓ Collected {len(raw_items)} raw items from page")
        return raw_items


def scrape_multiple_pages(base_url: str, site_type: str, max_pages: int = 1, custom_category: Optional[str] = None) -> tuple[List[Dict], Optional[str]]:
    """Universal scraper - works with any website structure
    
    Args:
        base_url: URL to scrape from
        site_type: Type of site (kept for compatibility)
        max_pages: Maximum number of pages to scrape
        custom_category: Optional category to override AI-detected categories
    """
    scraper = AdvancedScraper()
    
    if not scraper.groq_client:
        return [], "Groq AI is not configured. Please set GROQ_API_KEY environment variable."
    
    category_msg = f" (category: {custom_category})" if custom_category else ""
    logging.info(f"🚀 Starting universal scraping from {base_url} ({max_pages} pages){category_msg}")
    logging.info(f"📋 Phase 1: Collecting raw data...")
    
    all_raw_items = []
    
    first_soup = scraper.get_soup(base_url)
    if not first_soup:
        return [], f"Failed to fetch base URL: {base_url}"
    
    page_urls = scraper.detect_pagination_urls(first_soup, base_url, max_pages)
    
    if len(page_urls) == 1 and max_pages == 1:
        logging.info(f"📄 Scraping single page (no pagination)")
    elif len(page_urls) == 1 and max_pages > 1:
        logging.info(f"📄 No pagination detected - will scrape only the main page")
        logging.info(f"💡 This might be a single-page site or pagination wasn't found")
    else:
        logging.info(f"📄 Detected {len(page_urls)} pages to scrape")
    
    pages_scraped = 0
    consecutive_failures = 0
    
    for page_num, page_url in enumerate(page_urls, 1):
        logging.info(f"📄 Scraping page {page_num}/{len(page_urls)}: {page_url}")
        
        raw_items = scraper.scrape_page_raw(page_url)
        
        if raw_items:
            all_raw_items.extend(raw_items)
            pages_scraped += 1
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logging.warning(f"⚠️ No items found on page {page_num}")
            
            if consecutive_failures >= 2 and page_num > 1:
                logging.info(f"⏹️ Stopping - {consecutive_failures} consecutive pages with no items")
                break
        
        if page_num < len(page_urls):
            time.sleep(2)
    
    if not all_raw_items:
        return [], "No items found during scraping. The website structure may be unusual, protected, or this is a single-page site with no accessible content."
    
    logging.info(f"✅ Collected {len(all_raw_items)} total items from {pages_scraped} pages")
    logging.info(f"🤖 Phase 2: Using AI to organize and categorize all data...")
    
    organized_items = scraper.organize_with_ai(all_raw_items)
    
    if not organized_items:
        return [], "AI failed to organize the scraped data"
    
    if custom_category:
        logging.info(f"📂 Overriding all categories with: {custom_category}")
        for item in organized_items:
            item['category'] = custom_category
    
    logging.info(f"✅ AI organized {len(organized_items)} items successfully")
    
    return organized_items, None
