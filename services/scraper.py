import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def extract_download_links(url, timeout=15):
    """Extract download links from a webpage - works with multiple file hosting services"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        download_links = []
        
        file_extensions = r'\.(exe|msi|zip|rar|7z|dmg|pkg|deb|rpm|apk|tar\.gz|tar|iso|img)'
        
        link_patterns = [
            r'https?://.*?' + file_extensions,
            r'https?://.*?download.*',
            r'https?://.*?dl\.',
            r'https?://(www\.)?(mediafire|mega|drive\.google|dropbox|github|uploadhaven|gofile|anonfiles|pixeldrain|krakenfiles|sendspace|zippyshare|1fichier)\..*',
            r'https?://.*?(uploadhaven|upload|mirror|server\d+).*'
        ]
        
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '').strip()
            
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            if not href.startswith('http'):
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(url, href)
                else:
                    continue
            
            parsed = urlparse(href)
            if not parsed.netloc:
                continue
            
            for pattern in link_patterns:
                if re.search(pattern, href, re.IGNORECASE):
                    if href not in download_links:
                        download_links.append(href)
                    break
            
            link_text = link.get_text().lower().strip()
            download_keywords = ['download', 'get', 'installer', 'setup', 'mirror', 'direct', 'link']
            
            if any(keyword in link_text for keyword in download_keywords):
                if href not in download_links and len(href) > 20:
                    download_links.append(href)
        
        return download_links[:15]
    
    except Exception as e:
        print(f"Scraper error for {url}: {str(e)}")
        return []

def scrape_software_info(url):
    """Extract basic software information from a webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        info = {
            'name': '',
            'description': '',
            'version': '',
            'file_size': '',
            'download_links': []
        }
        
        title_tag = soup.find('title')
        if title_tag:
            info['name'] = title_tag.get_text().strip()[:100]
        
        h1 = soup.find('h1')
        if h1 and not info['name']:
            info['name'] = h1.get_text().strip()[:100]
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            info['description'] = meta_desc.get('content', '')[:500]
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc and not info['description']:
            info['description'] = og_desc.get('content', '')[:500]
        
        info['download_links'] = extract_download_links(url)
        
        return info
    
    except Exception as e:
        print(f"Info scraper error: {str(e)}")
        return None
