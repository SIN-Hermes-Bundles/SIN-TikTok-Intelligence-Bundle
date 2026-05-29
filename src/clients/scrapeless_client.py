"""Scrapeless TikTok Client (SECONDARY data source).

Free trial with TikTok Shop + Social Media data.
Adds video analytics, hashtag trends, and live stream data
that Apify doesn't cover.

https://scrapeless.com/en/solutions/tiktok
"""

import json
import os
from typing import Optional

import httpx


class ScrapelessClient:
    """Scrapeless TikTok API client.

    Features:
    - TikTok Shop products
    - Video analytics
    - Hashtag trends
    - Live stream data
    - Creator profiles
    """

    BASE_URL = "https://api.scrapeless.com/api/v1"
    DEFAULT_TIMEOUT = 60.0

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._load_key()
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=self.DEFAULT_TIMEOUT,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def _load_key(self) -> str:
        config_path = os.path.expanduser(
            "~/.hermes/bundles/tiktok-intelligence/config/scrapeless.json"
        )
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f).get("api_key", "")
        return os.getenv("SCRAPELESS_API_KEY", "")

    def search_products(self, keyword: str, limit: int = 50) -> list[dict]:
        """Search TikTok Shop products."""
        try:
            resp = self.client.post("/tiktok/shop/search", json={
                "keyword": keyword,
                "limit": limit,
            })
            resp.raise_for_status()
            return resp.json().get("data", {}).get("products", [])
        except Exception as e:
            print(f"[Scrapeless] Search failed: {e}")
            return []

    def get_product_detail(self, product_id: str) -> dict:
        """Get detailed product info."""
        try:
            resp = self.client.get(f"/tiktok/shop/product/{product_id}")
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            print(f"[Scrapeless] Product detail failed: {e}")
            return {}

    def get_hashtag_trends(self, hashtag: str = "") -> list[dict]:
        """Get hashtag trends and velocity."""
        try:
            params = {}
            if hashtag:
                params["hashtag"] = hashtag
            resp = self.client.get("/tiktok/hashtags/trending", params=params)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("hashtags", [])
        except Exception as e:
            print(f"[Scrapeless] Hashtags failed: {e}")
            return []

    def get_top_videos(self, keyword: str = "", limit: int = 20) -> list[dict]:
        """Get top TikTok videos by keyword/hashtag."""
        try:
            params = {"limit": limit}
            if keyword:
                params["keyword"] = keyword
            resp = self.client.get("/tiktok/videos/top", params=params)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("videos", [])
        except Exception as e:
            print(f"[Scrapeless] Videos failed: {e}")
            return []

    def get_live_streams(self, limit: int = 20) -> list[dict]:
        """Get trending live streams."""
        try:
            resp = self.client.get("/tiktok/live/trending", params={"limit": limit})
            resp.raise_for_status()
            return resp.json().get("data", {}).get("lives", [])
        except Exception as e:
            print(f"[Scrapeless] Live streams failed: {e}")
            return []

    def get_creator_profile(self, username: str) -> dict:
        """Get creator profile with stats."""
        try:
            resp = self.client.get(f"/tiktok/creator/{username}")
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            print(f"[Scrapeless] Creator failed: {e}")
            return {}

    def close(self):
        self.client.close()
