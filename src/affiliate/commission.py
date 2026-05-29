"""Estimate TikTok Shop Affiliate commissions.

TikTok Shop commission structure (typical):
- Beauty & Personal Care: 15-30%
- Fashion & Apparel: 10-25%
- Electronics: 3-8%
- Home & Kitchen: 8-15%
- Food & Beverages: 5-12%
- Sports & Outdoors: 8-15%
- Pet Supplies: 8-12%
- Default: 10-15% (conservative estimate)

These rates can be scraped from:
- Affiliate Marketplace product pages
- Seller-set commission rates
- Public TikTok Shop data
"""


class CommissionEstimator:
    """Estimate affiliate commissions for products."""

    # Category → commission rate range
    CATEGORY_RATES = {
        "beauty": (0.15, 0.30),
        "skincare": (0.15, 0.30),
        "makeup": (0.15, 0.25),
        "hair": (0.10, 0.20),
        "fashion": (0.10, 0.25),
        "clothing": (0.10, 0.20),
        "shoes": (0.10, 0.20),
        "jewelry": (0.15, 0.25),
        "electronics": (0.03, 0.08),
        "phone": (0.03, 0.06),
        "gadgets": (0.05, 0.10),
        "home": (0.08, 0.15),
        "kitchen": (0.08, 0.15),
        "food": (0.05, 0.12),
        "beverages": (0.05, 0.10),
        "sports": (0.08, 0.15),
        "outdoors": (0.08, 0.15),
        "fitness": (0.08, 0.15),
        "pet": (0.08, 0.12),
        "toys": (0.08, 0.15),
        "office": (0.05, 0.10),
        "automotive": (0.05, 0.10),
    }

    DEFAULT_RATE = 0.12  # Conservative default

    def estimate(self, product: dict) -> dict:
        """Estimate commission for a single product.

        Returns dict with:
        - commission_rate: float (e.g. 0.15 for 15%)
        - commission_min: minimum commission estimate
        - commission_max: maximum commission estimate
        - est_earnings_per_sale: estimated $ per sale
        - est_total_earnings: estimated total if all sold volume was affiliate
        """
        category = self._extract_category(product)
        price = float(product.get("current_price") or 0)
        sales = int(product.get("sales_volume") or 0)

        # Get rate range
        min_rate, max_rate = self.CATEGORY_RATES.get(category, (self.DEFAULT_RATE - 0.03, self.DEFAULT_RATE + 0.03))
        mid_rate = (min_rate + max_rate) / 2

        # If product has explicit commission data, use it
        if product.get("commissionRate"):
            mid_rate = float(product["commissionRate"])
            min_rate = mid_rate * 0.8
            max_rate = mid_rate * 1.2

        return {
            "category": category,
            "commission_rate": round(mid_rate, 3),
            "commission_range": (round(min_rate, 3), round(max_rate, 3)),
            "est_earnings_per_sale": round(price * mid_rate, 2),
            "est_total_earnings": round(sales * price * mid_rate, 2),
            "sales_volume": sales,
            "price": price,
        }

    def top_earners(self, products: list[dict], n: int = 10) -> list[dict]:
        """Find products with highest estimated affiliate earnings.

        Returns products enriched with `_commission` field, sorted by earnings.
        """
        scored = []
        for p in products:
            p["_commission"] = self.estimate(p)
            p["_est_earnings"] = p["_commission"]["est_total_earnings"]
            scored.append(p)

        scored.sort(key=lambda p: -(p.get("_est_earnings", 0)))
        return scored[:n]

    def batch_estimate(self, products: list[dict]) -> list[dict]:
        """Add commission estimates to all products."""
        results = []
        total_est_earnings = 0
        for p in products:
            p["_commission"] = self.estimate(p)
            total_est_earnings += p["_commission"]["est_total_earnings"]
            results.append(p)

        return results

    @staticmethod
    def _extract_category(product: dict) -> str:
        """Extract category from product data."""
        category = (
            product.get("category")
            or product.get("categoryName")
            or product.get("productCategory")
            or ""
        ).lower()

        # Match against known categories
        for key in CommissionEstimator.CATEGORY_RATES:
            if key in category:
                return key

        # Try title
        title = (product.get("title") or "").lower()
        for key in CommissionEstimator.CATEGORY_RATES:
            if key in title:
                return key

        return "other"
