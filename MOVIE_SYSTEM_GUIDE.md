# Movie Scraping & Search System Guide

## Overview
Complete movie management system with scraping, database storage, URL shortening, and search capabilities.

## Features Implemented

### ✅ 1. Movie Scraping
- Scrape movies from TheNextPlanet.beer
- Support for multiple pages (pagination)
- Automatic download link extraction from `<center><a><button>` structure
- URL shortening with URL2Cash and Adrino
- Database storage with auto-deduplication

### ✅ 2. Movie Search
- Fast search from database
- Case-insensitive search
- Search across all categories or specific category
- View count tracking

### ✅ 3. Database Integration
- Movies collection with unique IDs
- Category-based organization
- Automatic URL caching
- View count tracking

## User Commands

### `/searchmovie <movie name>`
Search movies by name from the database.

**Examples:**
```
/searchmovie Avengers
/searchmovie Stranger Things
/searchmovie Inception
```

**Response includes:**
- Movie title
- Category
- Download link (shortened)
- View count

### `/netflix <movie name>`
Alias for `/searchmovie` - same functionality.

**Examples:**
```
/netflix Breaking Bad
/netflix Money Heist
```

### `/movies <category>`
Browse movies by category (scrapes live from website).

**Available Categories:**
- NETFLIX
- PRIME
- HOTSTAR
- BOLLYWOOD
- HOLLYWOOD
- HINDI
- ENGLISH
- TAMIL
- TELUGU
- MALAYALAM
- KANNADA
- SOUTH
- WEB-SERIES

**Examples:**
```
/movies NETFLIX
/movies BOLLYWOOD
/movies HOLLYWOOD 2  (for page 2)
```

## Admin Commands

### `/moviescrape <category> <pages>`
Scrape movies from a category and save to database.

**Usage:**
```
/moviescrape NETFLIX 1
/moviescrape BOLLYWOOD 3
/moviescrape HOLLYWOOD 5
```

**Features:**
- Scrapes 1-10 pages (max 10 to avoid timeouts)
- Each page takes ~30-60 seconds
- Auto-shortens URLs with URL2Cash/Adrino
- Saves to database with category
- Shows progress and statistics
- Prevents duplicates using URL-based IDs

**Example Response:**
```
✅ Scraping Complete!

📂 Category: NETFLIX
📄 Pages Scraped: 3

Results:
✅ Saved: 54 movies
❌ Failed: 0 movies

📊 Total in database: 54 NETFLIX movies

🔍 Users can now search with:
`/searchmovie <name>`
`/netflix <name>`
```

## Database Schema

### Movies Collection
```javascript
{
  "movie_id": "16-char-hash",        // MD5 hash of page_url
  "title": "Movie Title",            // Full movie title
  "page_url": "https://...",         // Source page URL
  "download_link": "https://...",    // Shortened download link
  "category": "NETFLIX",             // Category (uppercase)
  "active": true,                    // Active status
  "views_count": 0,                  // View counter
  "created_at": "2025-10-25T..."     // Timestamp
}
```

## Technical Details

### Title Extraction
Fixed to use the `title` attribute from `<a>` tags instead of text content.

**Before:**
```python
title = title_link.get_text(strip=True)  # Returns empty
```

**After:**
```python
title = title_link.get('title', '')      # Returns actual title
```

### Download Link Extraction
Enhanced to find buttons inside `<center>` tags.

**Pattern:**
```html
<center>
  <a href="/unlock-links/...">
    <button>Download Links</button>
  </a>
</center>
```

**Code:**
```python
center_tags = soup.find_all('center')
for center in center_tags:
    link = center.find('a', href=True)
    if link and link.find('button'):
        download_url = link.get('href')
```

### URL Shortening
Automatically shortens download links using:
1. URL2Cash API
2. Adrino Links API

Alternates between services for load balancing.

## Workflow

### For Users:
1. Browse categories: `/movies NETFLIX`
2. Or search database: `/searchmovie Avengers`
3. Click shortened download link
4. Complete verification
5. Download movie

### For Admins:
1. Scrape movies: `/moviescrape NETFLIX 3`
2. Wait for completion (90-180 seconds for 3 pages)
3. Movies saved to database
4. Users can now search them

## Statistics Commands

### Check Database Status
Use `/moviescrape` without arguments to see:
- Total movies in database
- Movies per category
- Usage instructions

**Example Response:**
```
🎬 Movie Scraper

📊 Database: 324 total movies

Available Categories:
• NETFLIX: 54 movies
• BOLLYWOOD: 120 movies
• HOLLYWOOD: 95 movies
• HINDI: 55 movies

Usage:
`/moviescrape <category> <pages>`
```

## Best Practices

### For Admins:
1. **Start Small**: Test with 1 page first
2. **Monitor**: Check success/failure counts
3. **Avoid Overload**: Max 10 pages per scrape
4. **Regular Updates**: Scrape new content periodically
5. **Check Logs**: Monitor for errors

### For Users:
1. **Search First**: Use `/searchmovie` for faster results
2. **Browse When**: Use `/movies` for newest content
3. **Be Specific**: Include year or details in search
4. **Try Variations**: Try different keywords if no results

## Performance

- **Live Scraping** (`/movies`): 30-60 seconds for 10 movies
- **Database Search** (`/searchmovie`): < 1 second
- **Bulk Scraping** (`/moviescrape`): 30-60 seconds per page

## Error Handling

### Common Errors:
1. **No movies found**: Category might be empty or misspelled
2. **Scraping timeout**: Reduce pages or try again
3. **URL shortening failed**: Falls back to original URL
4. **Database error**: Check MongoDB connection

### Solutions:
- Check category spelling
- Try smaller page count
- Check internet connection
- Verify MongoDB credentials

## Future Enhancements

Potential improvements:
- Background scraping jobs
- Movie metadata (year, language, quality)
- User ratings and reviews
- Favorites list for movies
- Download tracking
- Trending movies
- Recently added movies
- Advanced filters (year, language, quality)

## Support

For issues or questions:
1. Check this guide
2. Contact admin
3. Check bot logs
4. Review error messages
