# How to Check if Listings are in the Database

## Quick Check Methods

### 1. Via API (Easiest)
```bash
# Check total listings count
curl http://localhost:8000/api/listings/count

# Check stats (includes listings count)
curl http://localhost:8000/api/stats

# Get recent listings
curl http://localhost:8000/api/listings/recent?limit=5

# Get all listings
curl http://localhost:8000/api/listings
```

### 2. Via Frontend
- Go to **Dashboard** (`/dashboard`) - shows total listings count
- Go to **Listings** (`/dashboard/listings`) - shows all scraped listings
- The scraper page now shows listings count after starting a job

### 3. Via Backend Logs
Check the backend server console for messages like:
```
Starting background scrape for https://...
Scraper returned X listings to process
Scrape job completed: X added, Y processed, Z errors
```

### 4. Direct Database Access (if using SQLite)
```bash
# If using SQLite (default for development)
sqlite3 backend/clmonetizer.db

# Then run SQL queries:
SELECT COUNT(*) FROM listings;
SELECT * FROM listings ORDER BY date_scraped DESC LIMIT 10;
SELECT title, url, price, date_scraped FROM listings LIMIT 5;
```

### 5. Check if Scraper Found Listings
The scraper logs will show:
- `"Found X listings from ..."` - means listings were found
- `"No listings found"` - means the page structure might have changed or no listings on page
- `"Scrape job completed: 0 added"` - means no new listings were added

## Troubleshooting

### If listings count is 0:
1. **Check backend logs** - Look for errors or warnings
2. **Verify URL format** - Make sure the Craigslist URL is correct
3. **Check if page structure changed** - Craigslist may have updated their HTML
4. **Wait a bit longer** - Scraping can take a few minutes for large pages

### If you see errors in logs:
- Check if Playwright browsers are installed: `playwright install chromium`
- Check if database is accessible
- Check if OpenAI API key is set (for AI analysis)

