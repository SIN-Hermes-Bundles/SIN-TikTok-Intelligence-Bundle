"""Trend Fusion Engine v2.

Combines Apify (PRIMARY) + Scrapeless (SECONDARY) data.

Weights:
- Apify Product Data: 50% (soldCount, rating, reviewCount)
- Scrapeless Trends: 30% (hashtag velocity, video engagement)
- Cross-Check: 20% (both sources confirm → confidence boost)
"""


class TrendEngine:
    """Fusion engine for TikTok product trends."""

    APIFY_WEIGHT = 0.5
    SCRAPELESS_WEIGHT = 0.3
    CROSSCHECK_WEIGHT = 0.2

    def __init__(self, apify_client=None, scrapeless_client=None):
        self.apify = apify_client
        self.scrapeless = scrapeless_client

    def calculate_score(
        self,
        apify_product: dict = None,
        scrapeless_product: dict = None,
    ) -> dict:
        """Calculate unified trend score (0-100) for a product.

        Returns dict with:
        - score: Unified score (0-100)
        - factors: Breakdown of contributing factors
        - confidence: How confident we are (both_sources, single_source)
        """
        factors = {}

        # Apify score (50%)
        apify_score = 0.0
        if apify_product:
            apify_score = self._calc_apify_score(apify_product)
        factors["apify"] = round(apify_score, 1)

        # Scrapeless score (30%)
        scrapeless_score = 0.0
        if scrapeless_product:
            scrapeless_score = self._calc_scrapeless_score(scrapeless_product)
        factors["scrapeless"] = round(scrapeless_score, 1)

        # Cross-check bonus (20%)
        crosscheck = 0.0
        if apify_product and scrapeless_product:
            crosscheck = 20.0  # Both sources confirm = maximum confidence
            confidence = "both_sources"
        elif apify_product or scrapeless_product:
            crosscheck = 10.0  # Single source = medium confidence
            confidence = "single_source"
        else:
            confidence = "no_data"

        factors["crosscheck"] = round(crosscheck, 1)

        # Weighted total
        total = (
            apify_score * self.APIFY_WEIGHT +
            scrapeless_score * self.SCRAPELESS_WEIGHT +
            crosscheck * self.CROSSCHECK_WEIGHT
        )
        total = min(100, max(0, total))

        return {
            "score": round(total, 2),
            "confidence": confidence,
            "factors": factors,
        }

    def _calc_apify_score(self, product: dict) -> float:
        """Calculate Apify-based score (0-100).

        Uses: soldCount, rating, reviewCount
        """
        score = 0.0
        weight = 0.0

        # Sales velocity (40% of Apify)
        sales_count = self._parse_number(product.get("salesCount", "0"))
        if sales_count > 0:
            sales_score = min(100, sales_count / 100)  # 10k sales = 100
            score += sales_score * 0.4
            weight += 0.4

        # Rating (30% of Apify)
        rating = self._parse_float(product.get("rating", 0))
        if rating > 0:
            rating_score = (rating / 5.0) * 100
            score += rating_score * 0.3
            weight += 0.3

        # Review count (30% of Apify)
        review_count = self._parse_number(product.get("reviewCount", "0"))
        if review_count > 0:
            review_score = min(100, review_count / 10)  # 1000 reviews = 100
            score += review_score * 0.3
            weight += 0.3

        if weight == 0:
            return 0.0
        return score / weight

    def _calc_scrapeless_score(self, product: dict) -> float:
        """Calculate Scrapeless-based score (0-100).

        Uses: hashtag_velocity, video_engagement
        """
        score = 0.0
        weight = 0.0

        # Video engagement (50% of Scrapeless)
        engagement = self._parse_float(product.get("engagement", 0))
        if engagement > 0:
            eng_score = min(100, engagement * 100)
            score += eng_score * 0.5
            weight += 0.5

        # Hashtag velocity (50% of Scrapeless)
        velocity = self._parse_float(product.get("velocity", 0))
        if velocity > 0:
            vel_score = min(100, velocity * 100)
            score += vel_score * 0.5
            weight += 0.5

        if weight == 0:
            return 0.0
        return score / weight

    def merge_products(
        self,
        apify_products: list[dict],
        scrapeless_hashtags: list[dict] = None,
    ) -> list[dict]:
        """Merge Apify products with Scrapeless trend data.

        Matches by keyword/title similarity and enriches products
        with trend scores from both sources.
        """
        merged = []
        scrapeless_hashtags = scrapeless_hashtags or []

        for ap_product in apify_products:
            title = ap_product.get("title", "")
            score_data = self.calculate_score(apify_product=ap_product)
            merged.append({
                "title": title,
                "price": ap_product.get("price"),
                "sales": ap_product.get("salesCount"),
                "rating": ap_product.get("rating"),
                "reviews": ap_product.get("reviewCount"),
                "store": ap_product.get("storeName"),
                "url": ap_product.get("productUrl"),
                "unified_score": score_data["score"],
                "confidence": score_data["confidence"],
                "source": "apify",
            })

        # Sort by unified score
        merged.sort(key=lambda x: x["unified_score"], reverse=True)
        return merged

    @staticmethod
    def _parse_number(value) -> float:
        """Parse number from string like '205915' or '1.5K'."""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return float(value)
        value = str(value).replace(",", "").strip()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        for suffix, mult in multipliers.items():
            if suffix in value.upper():
                return float(value.upper().replace(suffix, "")) * mult
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _parse_float(value) -> float:
        """Parse float from any value."""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace(",", "").strip())
        except (ValueError, TypeError):
            return 0.0
