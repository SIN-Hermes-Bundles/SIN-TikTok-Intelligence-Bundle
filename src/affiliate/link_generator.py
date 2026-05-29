"""Generate TikTok Shop Affiliate tracking links.

Two modes:
1. WITH affiliate account: Proper tracking links + analytics
2. WITHOUT account: Direct product links with notes for registration

Link formats:
- Product: https://shop.tiktok.com/view/product/{product_id}?region=US
- Affiliate: https://www.tiktok.com/@seller/video/{video_id} (video-based)
- Marketplace: https://affiliate.tiktok.com/product/{product_id}
"""

import os
from typing import Optional


class AffiliateLinkGenerator:
    """Generate affiliate-tracking URLs for TikTok Shop products."""

    def __init__(self, affiliate_id: Optional[str] = None):
        self.affiliate_id = affiliate_id or os.getenv(
            "TIKTOK_AFFILIATE_ID", ""
        )

    def generate(self, product: dict) -> dict:
        """Generate all link types for a product.

        Returns dict with:
        - product_url: Original product URL
        - affiliate_url: Affiliate tracking URL (if account connected)
        - marketplace_url: Affiliate Marketplace URL
        - deep_link: App deep link (tiktokshop://)
        - share_text: Ready-to-share text with link
        """
        product_id = self._extract_id(product)
        product_url = product.get("product_url", "")

        links = {
            "product_url": product_url,
            "product_id": product_id,
            "title": product.get("title", ""),
            "price": product.get("current_price", ""),
            "shop": product.get("seller_name", ""),
        }

        # Affiliate Marketplace URL (always available)
        if product_id:
            links["marketplace_url"] = (
                f"https://affiliate.tiktok.com/product/{product_id}?region=US"
            )

        # Affiliate tracking URL (requires affiliate_id)
        if self.affiliate_id and product_id:
            links["affiliate_url"] = (
                f"https://shop.tiktok.com/view/product/{product_id}"
                f"?region=US&locale=en"
                f"&affiliate_id={self.affiliate_id}"
                f"&source=affiliate_marketplace"
            )
        elif product_url:
            links["affiliate_url"] = product_url  # Fallback
            links["_note"] = "Set TIKTOK_AFFILIATE_ID for tracking links"

        # App deep link
        if product_id:
            links["deep_link"] = f"tiktokshop://product/{product_id}"

        # Share text
        title = product.get("title", "Check this out")
        price = product.get("current_price", "")
        price_str = f" — ${price}" if price else ""
        url = links.get("affiliate_url") or links.get("marketplace_url") or product_url

        links["share_text"] = f"🔥 {title}{price_str} on TikTok Shop!\n{url}"

        return links

    def bulk_generate(self, products: list[dict], max_products: int = 50) -> list[dict]:
        """Generate affiliate links for multiple products.

        Returns products enriched with `_links` field.
        """
        results = []
        for p in products[:max_products]:
            p["_links"] = self.generate(p)
            results.append(p)
        return results

    def best_deal(self, products: list[dict]) -> dict:
        """Find the product with highest earning potential.

        Scores: sales × price × (1 - competition proxy)
        Competition proxy: lower review count = less saturated
        """
        best = None
        best_score = 0

        for p in products:
            sales = int(p.get("sales_volume") or 0)
            price = float(p.get("current_price") or 0)
            reviews = int(p.get("review_count") or 1)

            # Lower reviews = less competition, higher = more proven
            competition_penalty = 1 / (1 + reviews / 100)

            score = sales * float(price) * competition_penalty

            if score > best_score:
                best_score = score
                best = p

        if best:
            best["_affiliate_opportunity_score"] = round(best_score, 2)
            best["_links"] = self.generate(best)

        return best or {}

    @staticmethod
    def _extract_id(product: dict) -> str:
        """Extract product ID from product dict or URL."""
        # Direct ID field
        if product.get("productId"):
            return str(product["productId"])

        # From URL: .../product-name/{id}
        url = product.get("productUrl") or product.get("product_url", "")
        if url:
            parts = url.rstrip("/").split("/")
            if parts:
                last = parts[-1]
                if last.isdigit():
                    return last

        return ""
