"""EchoTik API Client (Free Tier).

TikTok Shop data analytics platform.
https://echotik.live

Free Tier: Basic filters, limited views, browser extension (limited).
"""

import json
import os
from typing import Optional

import httpx


class EchoTikClient:
    """Client for EchoTik Free Tier API.

    Features:
    - Product library (top sold, hot promoted, new products)
    - Shop library (best sellers, cross-border sellers)
    - Influencer library (followers, growth, sales champion)
    - Live stream library (most viewed, top selling)
    - Video library (top videos, top-selling videos)
    """

    BASE_URL = "https://api.echotik.live/v1"  # Assumed API endpoint
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._load_api_key()
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=self.DEFAULT_TIMEOUT,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "SIN-TikTok-Intelligence-Bundle/1.0",
            },
        )

    def _load_api_key(self) -> str:
        """Load API key from config or env."""
        config_path = os.path.expanduser("~/.hermes/bundles/tiktok-intelligence/config/echotik.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
                return config.get("api_key", "")
        return os.getenv("ECHOTIK_API_KEY", "")

    def get_products(self, filter_type: str = "top_sold", category: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Get products from EchoTik library.

        filter_type: top_sold, hot_promoted, new_products
        """
        try:
            params = {"type": filter_type, "limit": limit}
            if category:
                params["category"] = category
            resp = self.client.get("/products", params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[EchoTik] Products failed: {e}")
            return []

    def get_shops(self, filter_type: str = "best_seller", region: str = "US", limit: int = 50) -> list[dict]:
        """Get shops from EchoTik library.

        filter_type: best_seller, best_cross_border_seller
        """
        try:
            resp = self.client.get("/shops", params={
                "type": filter_type,
                "region": region,
                "limit": limit,
            })
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[EchoTik] Shops failed: {e}")
            return []

    def get_influencers(self, filter_type: str = "sales_champion", category: Optional[str] = None, limit: int = 50) -> list[dict]:
        """Get influencers from EchoTik library.

        filter_type: sales_champion, dark_horse, hot_ec_live_streamer
        """
        try:
            params = {"type": filter_type, "limit": limit}
            if category:
                params["category"] = category
            resp = self.client.get("/influencers", params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[EchoTik] Influencers failed: {e}")
            return []

    def get_live_streams(self, filter_type: str = "most_viewed", limit: int = 50) -> list[dict]:
        """Get live streams from EchoTik library.

        filter_type: most_viewed, top_selling, top_live_products
        """
        try:
            resp = self.client.get("/live-streams", params={
                "type": filter_type,
                "limit": limit,
            })
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[EchoTik] Live streams failed: {e}")
            return []

    def get_videos(self, filter_type: str = "top_videos", hashtag: Optional[str] = None, limit: int = 50) -> list[dict]:
        """Get videos from EchoTik library.

        filter_type: top_videos, top_selling_videos, top_hashtags
        """
        try:
            params = {"type": filter_type, "limit": limit}
            if hashtag:
                params["hashtag"] = hashtag
            resp = self.client.get("/videos", params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[EchoTik] Videos failed: {e}")
            return []

    def get_product_detail(self, product_id: str) -> dict:
        """Get detailed product info from EchoTik."""
        try:
            resp = self.client.get(f"/products/{product_id}/detail")
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            print(f"[EchoTik] Product detail failed: {e}")
            return {}

    def close(self):
        self.client.close()
