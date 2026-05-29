"""SimpTok API Client (Free Tier).

Light API for trending products, competitor grid, and category revenue.
https://simptok.com

Free Tier: Core metrics, limited exports, no credit card.
"""

import json
import os
from typing import Optional

import httpx


class SimpTokClient:
    """Client for SimpTok Free Tier API.

    Features:
    - Category revenue (real-time)
    - Competitor grid (top shops)
    - Top products (hourly refresh)
    - Launch tracker
    - Price simulator
    """

    BASE_URL = "https://api.simptok.com/v1"  # Assumed API endpoint
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
        config_path = os.path.expanduser("~/.hermes/bundles/tiktok-intelligence/config/simptok.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
                return config.get("api_key", "")
        return os.getenv("SIMPTOK_API_KEY", "")

    def get_trending_categories(self, region: str = "US") -> list[dict]:
        """Get trending categories with revenue data.

        Returns list of categories with:
        - name: Category name
        - revenue: Real-time revenue
        - growth: Month-over-month growth
        - score: AI Opportunity Score (0-100)
        """
        try:
            resp = self.client.get("/categories/trending", params={"region": region})
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[SimpTok] Categories failed: {e}")
            return []

    def get_competitor_grid(self, category: str, region: str = "US") -> list[dict]:
        """Get competitor grid for a category.

        Returns list of shops with:
        - name: Shop name
        - rank: Category rank
        - revenue: Revenue
        - avg_price: Average product price
        - score: AI Opportunity Score
        """
        try:
            resp = self.client.get("/shops/grid", params={
                "category": category,
                "region": region,
            })
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[SimpTok] Competitor grid failed: {e}")
            return []

    def get_top_products(self, category: str, region: str = "US", limit: int = 100) -> list[dict]:
        """Get top products (hourly refresh).

        Returns list of products with:
        - title: Product title
        - price: Current price
        - revenue: Revenue
        - growth: Week-over-week growth
        - velocity: Recent sales velocity
        - inventory_signal: Stock status
        """
        try:
            resp = self.client.get("/products/top", params={
                "category": category,
                "region": region,
                "limit": limit,
            })
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[SimpTok] Top products failed: {e}")
            return []

    def get_launches(self, days: int = 7, region: str = "US") -> list[dict]:
        """Get recent product launches.

        Returns list of launches with:
        - product_id: SKU identifier
        - launch_date: Launch date
        - initial_stock: Starting inventory
        - first_day_revenue: Day 1 revenue
        - seven_day_retention: 7-day retention rate
        - creators: List of creators who touched the launch
        """
        try:
            resp = self.client.get("/products/launches", params={
                "days": days,
                "region": region,
            })
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            print(f"[SimpTok] Launches failed: {e}")
            return []

    def get_product_detail(self, product_id: str) -> dict:
        """Get detailed product info."""
        try:
            resp = self.client.get(f"/products/{product_id}")
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            print(f"[SimpTok] Product detail failed: {e}")
            return {}

    def close(self):
        self.client.close()
