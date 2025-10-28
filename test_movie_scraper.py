import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.thenextplanet.beer"

def test_category_page():
    """Test scraping the category page to see what we're actually getting"""
    url = f"{BASE_URL}/cat/?cat=NETFLIX"
    
    print(f"Fetching: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("=" * 80)
    print("TESTING DIFFERENT SELECTORS")
    print("=" * 80)
    
    # Test different selectors
    selectors = [
        ('article', soup.find_all('article')),
        ('div.post', soup.find_all('div', class_='post')),
        ('div.entry', soup.find_all('div', class_='entry')),
        ('div.movie-item', soup.find_all('div', class_='movie-item')),
        ('div.item', soup.find_all('div', class_='item')),
    ]
    
    for selector_name, posts in selectors:
        print(f"\n{selector_name}: Found {len(posts)} elements")
        
        if posts and len(posts) > 0:
            print(f"\nFirst element from {selector_name}:")
            print("-" * 80)
            print(posts[0].prettify()[:500])
            print("...")
            print("-" * 80)
            
            # Try to extract title and link
            for i, post in enumerate(posts[:3], 1):
                print(f"\nPost {i}:")
                title_link = post.find('a', href=True)
                if title_link:
                    # Try different ways to get the title
                    title_text = title_link.get_text(strip=True)
                    title_attr = title_link.get('title', '')
                    movie_url = title_link.get('href', '')
                    
                    print(f"  Title (text): {title_text[:100] if title_text else 'EMPTY'}")
                    print(f"  Title (attr): {title_attr[:100] if title_attr else 'EMPTY'}")
                    print(f"  URL: {movie_url}")
                    
                    # Check if URL needs to be made absolute
                    if movie_url and not movie_url.startswith('http'):
                        full_url = BASE_URL + movie_url
                        print(f"  Full URL: {full_url}")
                else:
                    print("  No link found")

def test_movie_page():
    """Test extracting download link from a specific movie page"""
    print("\n" + "=" * 80)
    print("TEST MOVIE PAGE LINK EXTRACTION")
    print("=" * 80)
    
    # Use the first movie from the category page
    movie_url = "https://www.thenextplanet.beer/movie/2105/the-elixir/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"\nFetching: {movie_url}\n")
    
    response = requests.get(movie_url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Test finding center tags with buttons
    center_tags = soup.find_all('center')
    print(f"Found {len(center_tags)} center tags\n")
    
    for i, center in enumerate(center_tags[:5], 1):
        print(f"\nCenter tag {i}:")
        print("-" * 80)
        print(center.prettify()[:400])
        print("...")
        print("-" * 80)
        
        link = center.find('a', href=True)
        if link:
            button = link.find('button')
            if button:
                print(f"\n✓ FOUND BUTTON IN CENTER!")
                print(f"  Link href: {link.get('href')}")
                print(f"  Button text: {button.get_text(strip=True)}")
                print(f"  Link title: {link.get('title', 'N/A')}")
            else:
                print(f"  Link found but no button inside")
                print(f"  Link href: {link.get('href')}")
        else:
            print(f"  No link found in this center tag")

if __name__ == "__main__":
    try:
        print("MOVIE SCRAPER DEBUG TEST")
        print("=" * 80)
        
        test_category_page()
        print("\n\n")
        test_movie_page()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
