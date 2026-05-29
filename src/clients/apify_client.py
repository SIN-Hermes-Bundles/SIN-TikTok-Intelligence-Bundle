"""Apify TikTok Shop Client (PRIMARY data source).

Uses PRO100CHOK TikTok Shop Scraper actor.
Free Tier: $5/month credit, ~$2/1000 records = ~2,500 products/month.

No TikTok login, cookies, or account needed.
"""

import json
import os
from typing import Optional

from apify_client import ApifyClient, ApifyClientError


ACTOR_ID = "pro100chok/tiktok-shop-scraper-usage"


class ApifyTikTokClient:
    """Apify-based TikTok Shop scraper client.

    Scrape types:
    - search: Search by keyword, get top products
    - category: Pull bestsellers from category
    - store: Get all products from a store
    - creator: Get creator storefront
    - reviews: Get verified-buyer reviews
    """

    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or self._load_token()
        self.client = ApifyClient(self.token) if self.token else None

    def _load_token(self) -> str:
        config_path = os.path.expanduser(
            "~/.hermes/bundles/tiktok-intelligence/config/apify.json"
        )
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f).get("api_token", "")
        return os.getenv("APIFY_API_TOKEN", "")

    def _call_actor(self, run_input: dict, timeout: int = 900) -> list[dict]:
        """Call Apify actor and return dataset items."""
        if not self.client:
            raise RuntimeError("No Apify API token. Set APIFY_API_TOKEN or create config/apify.json")

        run = self.client.actor(ACTOR_ID).call(
            run_input=run_input,
            timeout_secs=timeout,
        )

        if not run or run.get("status") != "SUCCEEDED":
            status = run.get("status") if run else "no run"
            raise RuntimeError(f"Actor run not SUCCEEDED: {status}")

        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError("No dataset ID in run result")

        items = list(self.client.dataset(dataset_id).iterate_items())
        return items

    def search_products(
        self,
        keyword: str,
        max_items: int = 50,
        sort_by: str = "best_sellers",
        region: str = "us",
    ) -> list[dict]:
        """Search TikTok Shop products by keyword.

        Returns list of:
        - title: Product name
        - price: Current price (string, e.g. "$12.99")
        - salesCount: Total units sold
        - rating: Average rating (1-5)
        - reviewCount: Number of reviews
        - storeName: Seller store name
        - productUrl: Product page URL
        """
        return self._call_actor({
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

    def get_category_products(
        self,
        category: str,
        max_items: int = 100,
        region: str = "us",
    ) -> list[dict]:
        """Get top products from a TikTok Shop category."""
        return self._call_actor({
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

    def get_store_products(
        self,
        store_name: str,
        max_items: int = 50,
        region: str = "us",
    ) -> list[dict]:
        """Get all products from a TikTok Shop store."""
        return self._call_actor({
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

    def get_creator_products(
        self,
        creator_username: str,
        max_items: int = 50,
        region: str = "us",
    ) -> list[dict]:
        """Get products from a creator's TikTok Shop storefront."""
        return self._call_actor({
            "scrapeType": "creator",
            "creatorUsername": creator_username,
            "maxItems": max_items,
            "region": region,
            "proxyConfiguration": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": region.upper(),
            },
        })

    def get_product_reviews(
        self,
        product_url: str,
        max_reviews: int = 100,
        min_stars: Optional[int] = None,
        only_verified: bool = True,
        region: str = "us",
    ) -> list[dict]:
        """Get reviews for a TikTok Shop product.

        Args:
            product_url: Full product page URL
            max_reviews: Max reviews to fetch
            min_stars: Filter by minimum star rating (1-5)
            only_verified: Only verified-buyer reviews
        """
        run_input = {
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
        }
        if min_stars:
            run_input["minStars"] = min_stars
        return self._call_actor(run_input)
