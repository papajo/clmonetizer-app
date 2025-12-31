from playwright.async_api import async_playwright
import logging

class ScraperService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def scrape_category(self, url: str):
        """
        Scrapes a Craigslist category page and returns a list of listing URLs.
        """
        self.logger.info(f"Scraping category URL: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle")
                
                # Extract listing elements
                # Craigslist structure: 'li.cl-static-search-result' or similar. 
                # We need to adapt to current CL structure. 
                # Often it's `li.result-row` or `li.cl-search-result`
                
                # Check for standard 'li.cl-search-result'
                listings_data = []
                
                # Get page content for AI parsing later if needed, but for now extract basic links
                # Let's extract URLs from 'a.cl-app-anchor' inside 'li'
                
                # Using a generic strategy: find all links that look like posting links
                # Usually contain '/cto/', '/ctd/', etc. or just end in .html
                
                # Let's grab all 'li' elements with class 'cl-search-result'
                results = await page.evaluate('''() => {
                    const items = document.querySelectorAll('li.cl-search-result');
                    const data = [];
                    items.forEach(item => {
                         const titleParams = item.getAttribute('title');
                         const aTag = item.querySelector('a');
                         if (aTag) {
                             data.push({
                                 url: aTag.href,
                                 title: aTag.innerText
                             });
                         }
                    });
                    if (data.length === 0) {
                        // Fallback for older/different CL layouts (like lists)
                        const listItems = document.querySelectorAll('.result-row');
                        listItems.forEach(row => {
                            const a = row.querySelector('.result-title.hdrlnk');
                            const meta = row.querySelector('.result-meta .result-price');
                            if (a) {
                                data.push({
                                    url: a.href,
                                    title: a.innerText,
                                    price: meta ? meta.innerText : null
                                });
                            }
                        });
                    }
                    return data;
                }''')
                
                listings_data = results
                self.logger.info(f"Found {len(listings_data)} listings.")
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                listings_data = []
            finally:
                await browser.close()
                
            return listings_data

    async def scrape_listing_details(self, url: str):
        """
        Scrapes detailed information from a specific listing page.
        """
        self.logger.info(f"Scraping listing details: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            details = {}
            try:
                await page.goto(url, wait_until="load", timeout=30000)
                
                # Extract Title
                try:
                    title = await page.title()
                    details['title'] = title
                except Exception as e:
                    self.logger.warning(f"Could not extract title from {url}: {e}")
                    details['title'] = "Unknown"
                
                # Extract Body/Description
                try:
                    body = await page.locator('#postingbody').inner_text(timeout=5000)
                    details['description'] = body
                except Exception as e:
                    self.logger.warning(f"Could not extract body from {url}: {e}")
                    details['description'] = ""
                
                # Extract Price
                try:
                    price_elem = await page.locator('.price').first.inner_text(timeout=3000)
                    details['price'] = price_elem
                except Exception:
                    # Try alternative selectors
                    try:
                        price_elem = await page.locator('[class*="price"]').first.inner_text(timeout=2000)
                        details['price'] = price_elem
                    except Exception:
                        details['price'] = None
                
                # Extract Location
                try:
                    location_elem = await page.locator('.postingtitletext .postingtitle').first.inner_text(timeout=3000)
                    details['location'] = location_elem
                except Exception:
                    try:
                        location_elem = await page.locator('[class*="location"]').first.inner_text(timeout=2000)
                        details['location'] = location_elem
                    except Exception:
                        details['location'] = None
                
                # Extract Attributes (like odometer, etc.)
                try:
                    attrs = await page.evaluate('''() => {
                        const attrGroups = document.querySelectorAll('.attrgroup span');
                        const result = {};
                        attrGroups.forEach(span => {
                            const text = span.innerText;
                            const parts = text.split(':');
                            if (parts.length === 2) {
                                result[parts[0].trim().toLowerCase()] = parts[1].trim();
                            } else {
                                result['tag'] = result['tag'] ? result['tag'] + ',' + text : text;
                            }
                        });
                        return result;
                    }''')
                    details.update(attrs)
                except Exception as e:
                    self.logger.warning(f"Could not extract attributes from {url}: {e}")
                
            except Exception as e:
                self.logger.error(f"Error scraping listing {url}: {e}")
            finally:
                await browser.close()
                
            return details
            
scraper_service = ScraperService()
