"""Check if TikTok Shop products are eligible for affiliate promotion.

Two approaches:
1. API field: Some products return `affiliateEligible` or similar
2. Open Affiliate Marketplace: Products anyone can promote
3. Commission data: If commission rate > 0, product is affiliate-eligible

Without a TikTok Shop Affiliate Account, we can only check product data
and filter by signals of affiliate eligibility.
"""

from typing import Optional


class AffiliateEligibilityChecker:
    """Check product affiliate eligibility."""

    # Known signals that a product likely has open affiliate
    AFFILIATE_SIGNALS = [
        "affiliateEligible",
        "openAffiliate",
        "collaborationType",
        "commissionRate",
        "affiliateCommission",
    ]

    def check_product(self, product: dict) -> dict:
        """Check a single product for affiliate eligibility.

        Returns dict with:
        - eligible: bool
        - confidence: float (0.0-1.0)
        - signals: list[str] (found signals)
        - method: str (how we determined eligibility)
        """
        signals_found = []
        confidence = 0.0
        eligible = False
        method = "none"

        # Direct API field
        if product.get("affiliateEligible") or product.get("openAffiliate"):
            eligible = True
            confidence = 1.0
            method = "api_field"
            signals_found.append("affiliateEligible")

        # Commission rate available
        if product.get("commissionRate") or product.get("commission_rate"):
            eligible = True
            confidence = 0.9
            method = "commission_data"
            signals_found.append("commissionRate")

        # High seller volume = likely has affiliate program
        shop_followers = self._parse_number(product.get("shop_followers", 0))
        shop_total_sold = self._parse_number(product.get("shop_total_sold", 0))

        if shop_total_sold > 10000:
            confidence = max(confidence, 0.7)
            signals_found.append("high_shop_volume")
            method = method or "heuristic"

        if shop_followers > 5000:
            confidence = max(confidence, 0.6)
            signals_found.append("high_followers")
            method = method or "heuristic"

        # High review count = established product = likely affiliate
        reviews = product.get("review_count", 0) or 0
        if reviews > 100:
            confidence = max(confidence, 0.5)
            signals_found.append("high_reviews")
            method = method or "heuristic"

        # High rating = quality product sellers want to promote
        rating = product.get("rating") or product.get("shop_rating") or 0
        if isinstance(rating, (int, float)) and rating >= 4.5:
            confidence = max(confidence, 0.4)
            signals_found.append("high_rating")
            method = method or "heuristic"

        # Final determination
        if confidence >= 0.5 and not eligible:
            eligible = True

        return {
            "eligible": eligible,
            "confidence": round(confidence, 2),
            "signals": signals_found,
            "method": method,
        }

    def filter_eligible(self, products: list[dict], min_confidence: float = 0.4) -> list[dict]:
        """Filter products by affiliate eligibility.

        Returns products sorted by: eligible (yes first) → confidence (high first) → sales volume.
        """
        scored = []
        for p in products:
            check = self.check_product(p)
            p["_affiliate_check"] = check
            scored.append(p)

        # Sort: eligible first, then by confidence, then by sales
        scored.sort(
            key=lambda p: (
                not p["_affiliate_check"]["eligible"],
                -p["_affiliate_check"]["confidence"],
                -(p.get("sales_volume") or 0),
            )
        )

        return [
            p for p in scored
            if p["_affiliate_check"]["confidence"] >= min_confidence
        ]

    def top_affiliate_picks(self, products: list[dict], n: int = 10) -> list[dict]:
        """Best affiliate candidates from product list.

        Scores by: affiliate confidence × sales potential × commission estimate.
        """
        eligible = self.filter_eligible(products)

        # Score each product
        for p in eligible:
            sales = p.get("sales_volume") or 0
            price = p.get("current_price") or 0
            confidence = p["_affiliate_check"]["confidence"]

            # Estimated commission (default 15% for TikTok Shop)
            est_commission_rate = p.get("commission_rate", 0.15)
            est_revenue = sales * float(price) * est_commission_rate

            p["_affiliate_score"] = round(confidence * est_revenue * 100, 2)

        # Sort by affiliate score
        eligible.sort(key=lambda p: -(p.get("_affiliate_score", 0)))

        return eligible[:n]

    @staticmethod
    def _parse_number(val) -> int:
        """Parse number from string or int (handles '20+', '105', etc.)."""
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            val = val.replace("+", "").replace(",", "").strip()
            try:
                return int(float(val))
            except ValueError:
                return 0
        return 0
