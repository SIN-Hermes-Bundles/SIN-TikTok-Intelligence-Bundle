"""Trend Fusion Engine.

Combines data from SimpTok, EchoTik, and Scrapling into a unified trend score.

Weights:
- SimpTok AI Opportunity Score: 0.4
- EchoTik Trend Rank: 0.3
- Scrapling Velocity Signal: 0.3
"""

from typing import Optional

import pandas as pd


class TrendEngine:
    """Fusion engine that combines multiple data sources."""

    # Weights for unified scoring
    SIMPTOK_WEIGHT = 0.4
    ECHOTIK_WEIGHT = 0.3
    SCRAPLING_WEIGHT = 0.3

    def __init__(self, simptok_client=None, echotik_client=None, scrapling_client=None):
        self.simptok = simptok_client
        self.echotik = echotik_client
        self.scrapling = scrapling_client

    def calculate_unified_score(
        self,
        simptok_score: Optional[float] = None,
        echotik_rank: Optional[float] = None,
        scrapling_velocity: Optional[float] = None,
    ) -> float:
        """Calculate unified trend score (0-100).

        Args:
            simptok_score: AI Opportunity Score (0-100)
            echotik_rank: Trend rank (lower = better, inverted)
            scrapling_velocity: Velocity signal (0-100)

        Returns:
            Unified score (0-100)
        """
        score = 0.0
        total_weight = 0.0

        if simptok_score is not None:
            score += simptok_score * self.SIMPTOK_WEIGHT
            total_weight += self.SIMPTOK_WEIGHT

        if echotik_rank is not None:
            # Invert rank (rank 1 = 100, rank 100 = 0)
            inverted = max(0, 100 - echotik_rank)
            score += inverted * self.ECHOTIK_WEIGHT
            total_weight += self.ECHOTIK_WEIGHT

        if scrapling_velocity is not None:
            score += scrapling_velocity * self.SCRAPLING_WEIGHT
            total_weight += self.SCRAPLING_WEIGHT

        if total_weight == 0:
            return 0.0

        # Normalize to 0-100
        return min(100, max(0, score / total_weight * 100))

    def fuse_products(self, simptok_products: list[dict], echotik_products: list[dict]) -> list[dict]:
        """Fuse products from multiple sources.

        Matches products by title similarity and merges data.
        """
        fused = []
        simptok_map = {p.get("title", "").lower(): p for p in simptok_products}

        for e_product in echotik_products:
            e_title = e_product.get("title", "").lower()
            s_product = simptok_map.get(e_title)

            if s_product:
                # Merge data
                unified_score = self.calculate_unified_score(
                    simptok_score=s_product.get("score"),
                    echotik_rank=e_product.get("rank", 50),
                )
                fused.append({
                    "title": e_product.get("title", s_product.get("title")),
                    "price": e_product.get("price", s_product.get("price")),
                    "revenue": e_product.get("revenue", s_product.get("revenue")),
                    "growth": e_product.get("growth", s_product.get("growth")),
                    "category": e_product.get("category", s_product.get("category")),
                    "unified_score": round(unified_score, 2),
                    "sources": ["simptok", "echotik"],
                    "simptok_data": s_product,
                    "echotik_data": e_product,
                })
            else:
                # Only EchoTik data
                fused.append({
                    "title": e_product.get("title"),
                    "price": e_product.get("price"),
                    "revenue": e_product.get("revenue"),
                    "growth": e_product.get("growth"),
                    "category": e_product.get("category"),
                    "unified_score": round(self.calculate_unified_score(
                        echotik_rank=e_product.get("rank", 50),
                    ), 2),
                    "sources": ["echotik"],
                    "echotik_data": e_product,
                })

        # Add SimpTok-only products
        for s_product in simptok_products:
            s_title = s_product.get("title", "").lower()
            if not any(f.get("title", "").lower() == s_title for f in fused):
                fused.append({
                    "title": s_product.get("title"),
                    "price": s_product.get("price"),
                    "revenue": s_product.get("revenue"),
                    "growth": s_product.get("growth"),
                    "category": s_product.get("category"),
                    "unified_score": round(self.calculate_unified_score(
                        simptok_score=s_product.get("score"),
                    ), 2),
                    "sources": ["simptok"],
                    "simptok_data": s_product,
                })

        # Sort by unified score
        fused.sort(key=lambda x: x.get("unified_score", 0), reverse=True)
        return fused

    def fuse_competitors(self, simptok_grid: list[dict], echotik_shops: list[dict]) -> list[dict]:
        """Fuse competitor data from SimpTok and EchoTik."""
        fused = []
        simptok_map = {s.get("name", "").lower(): s for s in simptok_grid}

        for e_shop in echotik_shops:
            e_name = e_shop.get("name", "").lower()
            s_shop = simptok_map.get(e_name)

            if s_shop:
                fused.append({
                    "name": e_shop.get("name", s_shop.get("name")),
                    "rank": e_shop.get("rank", s_shop.get("rank")),
                    "revenue": e_shop.get("revenue", s_shop.get("revenue")),
                    "avg_price": e_shop.get("avg_price", s_shop.get("avg_price")),
                    "score": e_shop.get("score", s_shop.get("score")),
                    "sources": ["echotik", "simptok"],
                })
            else:
                fused.append({
                    "name": e_shop.get("name"),
                    "rank": e_shop.get("rank"),
                    "revenue": e_shop.get("revenue"),
                    "avg_price": e_shop.get("avg_price"),
                    "score": e_shop.get("score"),
                    "sources": ["echotik"],
                })

        # Add SimpTok-only
        for s_shop in simptok_grid:
            s_name = s_shop.get("name", "").lower()
            if not any(f.get("name", "").lower() == s_name for f in fused):
                fused.append({
                    "name": s_shop.get("name"),
                    "rank": s_shop.get("rank"),
                    "revenue": s_shop.get("revenue"),
                    "avg_price": s_shop.get("avg_price"),
                    "score": s_shop.get("score"),
                    "sources": ["simptok"],
                })

        fused.sort(key=lambda x: x.get("rank", 999))
        return fused

    def get_velocity_signal(self, scrapling_data: list[dict]) -> float:
        """Calculate velocity signal from Scrapling data.

        Based on trending hashtags and video growth.
        """
        if not scrapling_data:
            return 0.0

        # Simple heuristic: average "views" growth
        total_views = 0
        count = 0
        for item in scrapling_data:
            views_str = item.get("views", "0")
            # Parse views (e.g., "1.5M" -> 1500000)
            try:
                views_num = self._parse_views(views_str)
                total_views += views_num
                count += 1
            except (ValueError, TypeError):
                continue

        if count == 0:
            return 0.0

        avg_views = total_views / count
        # Normalize to 0-100 (assuming 1M views = 100)
        return min(100, avg_views / 10000)

    @staticmethod
    def _parse_views(views_str: str) -> float:
        """Parse view count string to number."""
        if not views_str:
            return 0
        views_str = str(views_str).replace(",", "").strip()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        for suffix, mult in multipliers.items():
            if suffix in views_str:
                return float(views_str.replace(suffix, "")) * mult
        return float(views_str)
