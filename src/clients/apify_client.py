"""Apify TikTok Clients.

TWO actors:
1. clockworks/tiktok-scraper (GENERAL): Videos, hashtags, profiles, search
2. pro100chok/tiktok-shop-scraper-usage (SHOP): Products, prices, sales, stores

Both: $5/month free credit, no TikTok login needed.
"""

import json
import os
from typing import Optional
from apify_client import ApifyClient


class ApifyTikTokVideoClient:
    """General TikTok scraper — videos, hashtags, profiles, search.

    Actor: clockworks/tiktok-scraper
    Data: Video engagement, hashtag velocity, creator profiles
    Best for: Trend discovery, influencer research, content analysis
    """

    ACTOR_ID = "clockworks/tiktok-scraper"

    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or _load_token("apify.json")
        self.client = ApifyClient(self.token) if self.token else None

    def _call(self, run_input: dict, timeout_secs: int = 600) -> list[dict]:
        if not self.client:
            raise RuntimeError("No Apify API token. Set APIFY_API_TOKEN or create config/apify.json")
        from datetime import timedelta
        run = self.client.actor(self.ACTOR_ID).call(
            run_input=run_input,
            wait_duration=timedelta(seconds=timeout_secs),
        )
        if run.status != "SUCCEEDED":
            raise RuntimeError(f"Actor failed: {run.status}")
        if not run.default_dataset_id:
            raise RuntimeError("No dataset ID")
        return list(self.client.dataset(run.default_dataset_id).iterate_items())

    def search_hashtags(self, hashtags: list[str], results_per_page: int = 100) -> list[dict]:
        """Get videos for hashtags (e.g. #TikTokMadeMeBuyIt, #skincare).

        Returns: video URLs, play counts, likes, shares, comments, music, author
        """
        return self._call({
            "hashtags": hashtags,
            "resultsPerPage": results_per_page,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "proxyCountryCode": "None",
        })

    def search_videos(self, queries: list[str], results_per_page: int = 50,
                      section: str = "/video", sort: str = "MOST_RELEVANT") -> list[dict]:
        """Search TikTok videos by keyword.

        section: '' (top), '/video', '/user'
        sort: MOST_RELEVANT, MOST_LIKED, LATEST
        """
        return self._call({
            "searchQueries": queries,
            "searchSection": section,
            "resultsPerPage": results_per_page,
            "videoSearchSorting": sort,
            "shouldDownloadVideos": False,
            "proxyCountryCode": "None",
        })

    def get_profiles(self, usernames: list[str], results_per_page: int = 30) -> list[dict]:
        """Get TikTok profiles and their videos."""
        return self._call({
            "profiles": usernames,
            "resultsPerPage": results_per_page,
            "profileScrapeSections": ["videos"],
            "profileSorting": "latest",
            "shouldDownloadVideos": False,
            "proxyCountryCode": "None",
        })

    def get_posts(self, urls: list[str]) -> list[dict]:
        """Get specific TikTok posts by URL."""
        return self._call({
            "postURLs": urls,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "proxyCountryCode": "None",
        })


class ApifyTikTokShopClient:
    """TikTok Shop scraper — products, prices, sales, stores, creators.

    Actor: pro100chok/tiktok-shop-scraper-usage
    Data: Product titles, prices, soldCount, rating, reviews, stores
    Best for: Product discovery, competitor analysis, sales tracking
    Cost: ~$2/1000 records
    """

    ACTOR_ID = "pro100chok/tiktok-shop-scraper-usage"

    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or _load_token("apify.json")
        self.client = ApifyClient(self.token) if self.token else None

    def _call(self, run_input: dict, timeout: int = 900) -> list[dict]:
        if not self.client:
            raise RuntimeError("No Apify API token. Set APIFY_API_TOKEN or create config/apify.json")
        from datetime import timedelta
        run = self.client.actor(self.ACTOR_ID).call(
            run_input=run_input,
            wait_duration=timedelta(seconds=timeout),
        )
        if run.status != "SUCCEEDED":
            raise RuntimeError(f"Actor failed: {run.status}")
        if not run.default_dataset_id:
            raise RuntimeError("No dataset ID")
        return list(self.client.dataset(run.default_dataset_id).iterate_items())

    def search_products(self, keyword: str, max_items: int = 50,
                        sort_by: str = "best_sellers", region: str = "us") -> list[dict]:
        """Search TikTok Shop products by keyword."""
        return self._call({
            "scrapeType": "search",
            "searchKeywords": [keyword],
            "sortBy": sort_by,
            "maxItems": max_items,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_category(self, category: str, max_items: int = 100, region: str = "us") -> list[dict]:
        """Top products from a TikTok Shop category."""
        return self._call({
            "scrapeType": "category",
            "categoryName": category,
            "maxItems": max_items,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_store(self, store_name: str, max_items: int = 50, region: str = "us") -> list[dict]:
        """All products from a TikTok Shop store."""
        return self._call({
            "scrapeType": "store",
            "storeName": store_name,
            "maxItems": max_items,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_creator(self, username: str, max_items: int = 50, region: str = "us") -> list[dict]:
        """Products from a creator's TikTok Shop storefront."""
        return self._call({
            "scrapeType": "creator",
            "creatorUsername": username,
            "maxItems": max_items,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_reviews(self, product_url: str, max_reviews: int = 100,
                    only_verified: bool = True, region: str = "us") -> list[dict]:
        """Verified-buyer reviews for a product."""
        return self._call({
            "scrapeType": "reviews",
            "productUrl": product_url,
            "maxReviews": max_reviews,
            "onlyVerified": only_verified,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_product_details(self, product_urls: list[str],
                            region: str = "us") -> list[dict]:
        """Full product details: price, sales, store, variants, shipping.

        Args:
            product_urls: List of TikTok Shop product URLs
                         (from search results or direct)

        Returns full product data including:
        - title, price (original/discounted), currency
        - soldCount, rating, reviewCount
        - storeName, storeId, storeUrl
        - variants (size, color, price per variant)
        - shipping info, return policy
        - product images, description

        Cost: ~1 record per product URL (~$2/1000)
        """
        return self._call({
            "scrapeType": "product",
            "productUrls": product_urls,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def full_research(self, keyword: str, max_items: int = 20,
                      region: str = "us") -> dict:
        """Complete product research: search + details + reviews.

        Two-step pipeline:
        1. Search → get product names + URLs
        2. Product details → get prices, sales, stores

        Returns structured research data.
        """
        # Step 1: Search
        search_results = self.search_products(keyword, max_items, region=region)
        urls = [p.get("productUrl") for p in search_results if p.get("productUrl")]
        urls = urls[:max_items]  # Limit to avoid excessive cost

        if not urls:
            return {"search_results": search_results, "details": []}

        # Step 2: Full details
        details = self.get_product_details(urls, region=region)

        # Merge search with details
        enriched = []
        for i, (sr, det) in enumerate(zip(search_results, details)):
            enriched.append({
                "title": det.get("title") or sr.get("title"),
                "current_price": det.get("currentPrice") or sr.get("currentPrice"),
                "original_price": det.get("originalPrice") or sr.get("originalPrice"),
                "sales_volume": det.get("salesVolume") or sr.get("salesVolume"),
                "global_sold": det.get("globalSold"),
                "sold_last_30_days": det.get("soldLast30Days"),
                "rating": det.get("rating") or sr.get("rating"),
                "review_count": det.get("reviewCount") or sr.get("reviewCount"),
                "seller_name": det.get("sellerName") or sr.get("sellerName"),
                "seller_location": det.get("sellerLocation"),
                "shop_rating": det.get("shopRating"),
                "shop_total_sold": det.get("shopTotalSold"),
                "shop_followers": det.get("shopFollowers"),
                "shop_url": det.get("shopUrl"),
                "product_url": sr.get("productUrl"),
                "variants": det.get("variants", []),
                "shipping": det.get("shippingInfo"),
                "images": det.get("imageUrls", []),
            })

        return {
            "keyword": keyword,
            "search_count": len(search_results),
            "detail_count": len(details),
            "products": enriched,
        }


def _load_token(config_name: str) -> str:
    config_path = os.path.expanduser(
        f"~/.hermes/bundles/tiktok-intelligence/config/{config_name}"
    )
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f).get("api_token", "")
    return os.getenv("APIFY_API_TOKEN", "")
