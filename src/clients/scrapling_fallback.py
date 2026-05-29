"""Scrapling Fallback for TikTok Shop.

Uses Scrapling (Open Source, BSD-3-Clause) as fallback when:
- APIs are rate-limited
- Data is missing from APIs
- Direct page scraping is needed

https://github.com/D4Vinci/Scrapling
"""

from scrapling.fetchers import StealthyFetcher


class ScraplingFallback:
    """Scrapling-based fallback scraper for TikTok.

    Features:
    - Cloudflare Turnstile/Interstitial bypass
    - Stealth mode (headless browser)
    - Adaptive selectors (survives layout changes)
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._fetcher = None

    def _get_fetcher(self):
        """Lazy init StealthyFetcher."""
        if self._fetcher is None:
            self._fetcher = StealthyFetcher()
            self._fetcher.configure(headless=self.headless, solve_cloudflare=True)
        return self._fetcher

    def get_tiktok_creative_trends(self, keyword: str = "") -> list[dict]:
        """Scrape TikTok Creative Center for trending content.

        Fallback when APIs don't provide hashtag/trend data.
        """
        url = f"https://creativecenter.tiktok.com/trends?keyword={keyword}"
        fetcher = self._get_fetcher()
        try:
            page = fetcher.fetch(url)
            # Extract trending items
            items = page.css("[data-testid='trend-item'], [class*='trend-item'], [class*='trending']")
            trends = []
            for item in items[:20]:
                title = item.css("[class*='title'], h3, h2").first
                views = item.css("[class*='views'], [class*='count']").first
                trends.append({
                    "title": title.text if title else None,
                    "views": views.text if views else None,
                    "source": "scrapling_creative_center",
                })
            return trends
        except Exception as e:
            print(f"[Scrapling] Creative trends failed: {e}")
            return []

    def get_tiktok_search_results(self, query: str) -> list[dict]:
        """Scrape TikTok search results for product discovery.

        Note: TikTok Shop search is NOT publicly accessible.
        This scrapes TikTok video search as proxy for trending products.
        """
        url = f"https://www.tiktok.com/search?q={query.replace(' ', '+')}"
        fetcher = self._get_fetcher()
        try:
            page = fetcher.fetch(url)
            items = page.css("[class*='search-item'], [data-e2e='search-card']")
            results = []
            for item in items[:20]:
                title = item.css("[class*='title'], h3, h4").first
                creator = item.css("[class*='author'], [class*='user']").first
                views = item.css("[class*='views'], [class*='stats']").first
                results.append({
                    "title": title.text if title else None,
                    "creator": creator.text if creator else None,
                    "views": views.text if views else None,
                    "source": "scrapling_tiktok_search",
                })
            return results
        except Exception as e:
            print(f"[Scrapling] Search failed: {e}")
            return []

    def get_tiktok_affiliate_products(self, keyword: str = "") -> list[dict]:
        """Scrape TikTok Shop Affiliate Marketplace.

        Note: Requires login. Scraping may not work without auth.
        """
        url = "https://affiliate.tiktok.com/"
        if keyword:
            url += f"?keyword={keyword}"
        fetcher = self._get_fetcher()
        try:
            page = fetcher.fetch(url)
            items = page.css("[class*='product-card'], [class*='affiliate-item']")
            products = []
            for item in items[:20]:
                title = item.css("[class*='title'], h3").first
                price = item.css("[class*='price']").first
                commission = item.css("[class*='commission']").first
                products.append({
                    "title": title.text if title else None,
                    "price": price.text if price else None,
                    "commission": commission.text if commission else None,
                    "source": "scrapling_affiliate",
                })
            return products
        except Exception as e:
            print(f"[Scrapling] Affiliate failed: {e}")
            return []

    def close(self):
        if self._fetcher:
            try:
                self._fetcher.close()
            except Exception:
                pass
            self._fetcher = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
