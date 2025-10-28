import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import utils.database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.thenextplanet.beer"

async def scrape_category_page(category="NETFLIX", page=1):
    """
    Scrape movies from a category page asynchronously
    Returns a list of movies with their titles and page URLs
    """
    try:
        url = f"{BASE_URL}/cat/?cat={category}"
        if page > 1:
            url += f"&cpage={page}"
        
        logger.info(f"Scraping category page: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                response.raise_for_status()
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        movies = []
        
        # Find all movie entries - adjust selectors based on actual HTML structure
        post_selectors = [
            soup.find_all('article'),
            soup.find_all('div', class_='post'),
            soup.find_all('div', class_='entry'),
            soup.find_all('div', class_='movie-item'),
            soup.find_all('div', class_='item'),
        ]
        
        for posts in post_selectors:
            if posts and len(posts) > 0:
                logger.info(f"Found {len(posts)} potential movie entries")
                for post in posts:
                    try:
                        # Find title and link
                        title_link = post.find('a', href=True)
                        if not title_link:
                            continue
                        
                        # The title is in the 'title' attribute, not in the text content
                        title = title_link.get('title', '')
                        movie_url = title_link.get('href', '')
                        
                        # Make sure both title and movie_url are strings
                        if not isinstance(movie_url, str) or not isinstance(title, str):
                            continue
                        
                        # Skip if no title
                        if not title.strip():
                            continue
                        
                        # Make sure URL is absolute
                        if not movie_url.startswith('http'):
                            movie_url = BASE_URL + movie_url if movie_url.startswith('/') else BASE_URL + '/' + movie_url
                        
                        # Only include if it looks like a movie page
                        if 'thenextplanet.beer' in movie_url:
                            movies.append({
                                'title': title,
                                'page_url': movie_url
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing post: {e}")
                        continue
                
                if movies:
                    break
        
        # Remove duplicates
        seen_urls = set()
        unique_movies = []
        for movie in movies:
            if movie['page_url'] not in seen_urls:
                seen_urls.add(movie['page_url'])
                unique_movies.append(movie)
        
        logger.info(f"Found {len(unique_movies)} unique movies on page {page}")
        return unique_movies, None
        
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching category page: {e}")
        return None, f"Failed to fetch page: {str(e)}"
    except Exception as e:
        logger.error(f"Error scraping category page: {e}")
        return None, str(e)

async def get_download_link_from_movie_page(movie_url):
    """
    Extract the Download Links button URL from a movie page asynchronously
    Returns the download link URL (not shortened yet)
    """
    try:
        logger.info(f"Fetching download link from: {movie_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(movie_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                response.raise_for_status()
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the Download Links button
        download_button = None
        
        # First, look for buttons inside center tags (the most specific pattern)
        # /html/body/div[7]/div[2]/div[7]/div[3]/center[1]/a/button
        center_tags = soup.find_all('center')
        for center in center_tags:
            link = center.find('a', href=True)
            if link and link.find('button'):
                download_button = link
                logger.info("Found download button inside center tag")
                break
        
        # If not found, try other selectors
        if not download_button:
            selectors = [
                soup.find('a', id='links-area-div'),
            ]
            
            # Try finding links with 'download' in text
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                if 'download' in link_text:
                    selectors.append(link)
                    break
            
            # Also look for links inside specific divs
            links_div = soup.find('div', id='links-area-div')
            if links_div:
                download_button = links_div.find('a', href=True)
            
            # Find first valid selector
            for selector in selectors:
                if selector and selector.get('href'):
                    download_button = selector
                    break
        
        if download_button and download_button.get('href'):
            download_url = download_button.get('href', '')
            
            # Make sure download_url is a string
            if not isinstance(download_url, str):
                logger.warning(f"Download URL is not a string: {type(download_url)}")
                return None, "Invalid download URL format"
            
            # Make sure URL is absolute
            if not download_url.startswith('http'):
                download_url = BASE_URL + download_url if download_url.startswith('/') else BASE_URL + '/' + download_url
            
            logger.info(f"Found download link: {download_url}")
            return download_url, None
        else:
            logger.warning(f"Download button not found on {movie_url}")
            return None, "Download button not found on page"
            
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching movie page: {e}")
        return None, f"Failed to fetch page: {str(e)}"
    except Exception as e:
        logger.error(f"Error extracting download link: {e}")
        return None, str(e)

async def get_movies_from_category(category="NETFLIX", page=1, max_movies=10):
    """
    Get movies from a category with their download links asynchronously
    Returns a list of movies with ORIGINAL download links (not shortened)
    """
    # Scrape the category page
    movies, error = await scrape_category_page(category, page)
    
    if error or not movies:
        return None, error or "No movies found in category"
    
    # Limit to max_movies
    movies = movies[:max_movies]
    
    # Get download links for each movie
    movies_with_links = []
    
    for i, movie in enumerate(movies, 1):
        logger.info(f"Processing movie {i}/{len(movies)}: {movie['title']}")
        
        # Get download link (original, not shortened)
        download_url, error = await get_download_link_from_movie_page(movie['page_url'])
        
        if download_url:
            # Save original URL (do NOT shorten during scraping)
            movies_with_links.append({
                'title': movie['title'],
                'page_url': movie['page_url'],
                'download_link': download_url
            })
            logger.info(f"Got original download link")
        else:
            logger.warning(f"Could not get download link for {movie['title']}: {error}")
        
        # Small async delay to avoid overwhelming the server
        await asyncio.sleep(0.5)
    
    if not movies_with_links:
        return None, "Could not extract download links from any movies"
    
    logger.info(f"Successfully processed {len(movies_with_links)} movies")
    return movies_with_links, None

async def scrape_and_save_movies(category="NETFLIX", num_pages=1):
    """
    Scrape multiple pages of a category and save to database
    Returns: (total_saved, total_failed, error)
    """
    total_saved = 0
    total_failed = 0
    
    logger.info(f"Starting to scrape {num_pages} page(s) of {category}")
    
    for page in range(1, num_pages + 1):
        logger.info(f"Scraping page {page}/{num_pages}")
        
        # Get movies with download links
        movies, error = await get_movies_from_category(category, page=page, max_movies=100)
        
        if error:
            logger.error(f"Error on page {page}: {error}")
            continue
        
        if not movies:
            logger.warning(f"No movies found on page {page}")
            continue
        
        # Save each movie to database
        for movie in movies:
            try:
                success = db.save_scraped_movie(
                    title=movie['title'],
                    page_url=movie['page_url'],
                    download_link=movie['download_link'],
                    category=category
                )
                if success:
                    total_saved += 1
                    logger.debug(f"Saved: {movie['title'][:50]}")
                else:
                    total_failed += 1
            except Exception as e:
                logger.error(f"Failed to save {movie['title'][:50]}: {e}")
                total_failed += 1
        
        # Delay between pages
        if page < num_pages:
            await asyncio.sleep(2)
    
    logger.info(f"Scraping complete: {total_saved} saved, {total_failed} failed")
    return total_saved, total_failed, None

def get_available_categories():
    """
    Returns a list of available movie categories
    """
    return [
        "NETFLIX",
        "PRIME",
        "HOTSTAR",
        "HINDI",
        "ENGLISH",
        "TAMIL",
        "TELUGU",
        "MALAYALAM",
        "KANNADA",
        "BOLLYWOOD",
        "HOLLYWOOD",
        "SOUTH",
        "WEB-SERIES"
    ]
