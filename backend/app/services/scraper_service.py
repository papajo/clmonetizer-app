from playwright.async_api import async_playwright
import logging

class ScraperService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def scrape_category(self, url: str):
        """
        Scrapes a Craigslist category page and returns a list of listing URLs.
        """
        # Remove hash fragments from URL as they can cause issues
        clean_url = url.split('#')[0]
        self.logger.info(f"Scraping category URL: {clean_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Set a longer timeout for slow pages
                await page.goto(clean_url, wait_until="networkidle", timeout=60000)
                
                # Wait a bit for dynamic content to load
                await page.wait_for_timeout(2000)
                
                listings_data = []
                
                # Try multiple selector strategies for different Craigslist layouts
                results = await page.evaluate('''() => {
                    const data = [];
                    
                    // Strategy 1: Modern Craigslist - cl-search-result
                    const modernItems = document.querySelectorAll('li.cl-search-result, li[data-pid]');
                    modernItems.forEach(item => {
                        const aTag = item.querySelector('a[href*="/d/"], a[href*=".html"]');
                        if (aTag && aTag.href) {
                            const title = aTag.textContent?.trim() || aTag.getAttribute('title') || 'Untitled';
                            const priceElem = item.querySelector('.price, [class*="price"]');
                            const price = priceElem ? priceElem.textContent?.trim() : null;
                            data.push({
                                url: aTag.href,
                                title: title,
                                price: price
                            });
                        }
                    });
                    
                    // Strategy 2: Older layout - result-row
                    if (data.length === 0) {
                        const listItems = document.querySelectorAll('.result-row, li.result-row');
                        listItems.forEach(row => {
                            const a = row.querySelector('.result-title.hdrlnk, a.result-title');
                            if (a && a.href) {
                                const meta = row.querySelector('.result-meta .result-price, .result-price');
                                data.push({
                                    url: a.href,
                                    title: a.textContent?.trim() || 'Untitled',
                                    price: meta ? meta.textContent?.trim() : null
                                });
                            }
                        });
                    }
                    
                    // Strategy 3: Generic - find all links that look like posting links
                    if (data.length === 0) {
                        const allLinks = document.querySelectorAll('a[href*="/d/"], a[href*=".html"]');
                        allLinks.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href && (href.includes('/d/') || href.endsWith('.html'))) {
                                const parent = link.closest('li, .result-row, [data-pid]');
                                if (parent) {
                                    const title = link.textContent?.trim() || link.getAttribute('title') || 'Untitled';
                                    const priceElem = parent.querySelector('.price, [class*="price"]');
                                    data.push({
                                        url: href.startsWith('http') ? href : new URL(href, window.location.href).href,
                                        title: title,
                                        price: priceElem ? priceElem.textContent?.trim() : null
                                    });
                                }
                            }
                        });
                    }
                    
                    // Remove duplicates based on URL
                    const unique = [];
                    const seen = new Set();
                    data.forEach(item => {
                        if (!seen.has(item.url)) {
                            seen.add(item.url);
                            unique.push(item);
                        }
                    });
                    
                    return unique;
                }''')
                
                listings_data = results
                self.logger.info(f"Found {len(listings_data)} listings from {clean_url}")
                
                if len(listings_data) == 0:
                    # Log page structure for debugging
                    page_content = await page.content()
                    self.logger.warning(f"No listings found. Page title: {await page.title()}")
                    self.logger.warning(f"Page has {len(page_content)} characters")
                
            except Exception as e:
                self.logger.error(f"Error scraping {clean_url}: {e}", exc_info=True)
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
