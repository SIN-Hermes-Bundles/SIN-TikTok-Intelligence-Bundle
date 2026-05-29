"""Trend Fusion Engine v2.

Three-source scoring:
- Apify Shop (pro100chok): 40% — product data, prices, sales, ratings
- Apify Video (clockworks): 35% — hashtag velocity, video engagement
- Scrapeless: 25% — cross-check, additional signals
"""


class TrendEngine:
    """Fuses Apify Shop + Apify Video + Scrapeless data into unified scores."""

    def __init__(self, shop_client=None, video_client=None, scrapeless_client=None):
        self.shop = shop_client
        self.video = video_client
        self.scrapeless = scrapeless_client

    # ── Product scoring (Shop-only) ──────────────────────────

    def score_product(self, product: dict) -> tuple[float, dict]:
        """Score a single product from Apify Shop data (0-100)."""
        score = 0.0
        weight = 0.0
        details = {}

        # Sales velocity: 0 → 100 (10k+ sales = 100)
        sales = _parse_num(product.get("salesCount", 0))
        if sales > 0:
            s = min(100, sales / 100)
            score += s * 0.45
            weight += 0.45
            details["sales_score"] = round(s, 1)

        # Rating: 0-5 → 0-100
        rating = _parse_num(product.get("rating", 0))
        if rating > 0:
            r = (rating / 5.0) * 100
            score += r * 0.30
            weight += 0.30
            details["rating_score"] = round(r, 1)

        # Review count: 0 → 100 (1000+ reviews = 100)
        reviews = _parse_num(product.get("reviewCount", 0))
        if reviews > 0:
            rv = min(100, reviews / 10)
            score += rv * 0.25
            weight += 0.25
            details["review_score"] = round(rv, 1)

        final = round(min(100, score / max(weight, 0.01)), 2)
        return final, details

    def merge_products(self, shop_products: list[dict]) -> list[dict]:
        """Score and sort Apify Shop products."""
        merged = []
        for p in shop_products:
            score, details = self.score_product(p)
            merged.append({
                "title": p.get("title", ""),
                "price": p.get("price", ""),
                "sales": p.get("salesCount", ""),
                "rating": p.get("rating", ""),
                "reviews": p.get("reviewCount", ""),
                "store": p.get("storeName", ""),
                "url": p.get("productUrl", ""),
                "unified_score": score,
                "score_details": details,
                "source": "apify_shop",
            })
        merged.sort(key=lambda x: x["unified_score"], reverse=True)
        return merged

    # ── Video scoring ─────────────────────────────────────────

    def score_video(self, video: dict) -> tuple[float, dict]:
        """Score a video by engagement (0-100)."""
        score = 0.0
        weight = 0.0
        details = {}

        plays = _parse_num(video.get("playCount", 0))
        likes = _parse_num(video.get("diggCount", 0))
        shares = _parse_num(video.get("shareCount", 0))
        comments = _parse_num(video.get("commentCount", 0))

        # Play count: 0 → 100 (1M+ plays = 100)
        if plays > 0:
            p = min(100, plays / 10000)
            score += p * 0.35
            weight += 0.35
            details["play_score"] = round(p, 1)

        # Like ratio: likes / plays → normalized
        if plays > 0 and likes > 0:
            ratio = likes / plays
            l = min(100, ratio * 1000)
            score += l * 0.30
            weight += 0.30
            details["like_ratio"] = round(ratio * 100, 2)

        # Comments: 0 → 100
        if comments > 0:
            c = min(100, comments / 10)
            score += c * 0.20
            weight += 0.20
            details["comment_score"] = round(c, 1)

        # Shares: 0 → 100
        if shares > 0:
            s = min(100, shares / 5)
            score += s * 0.15
            weight += 0.15
            details["share_score"] = round(s, 1)

        final = round(min(100, score / max(weight, 0.01)), 2)
        return final, details

    def merge_videos(self, videos: list[dict]) -> list[dict]:
        """Score and sort videos."""
        merged = []
        for v in videos:
            score, details = self.score_video(v)
            merged.append({
                "title": v.get("desc", v.get("text", ""))[:100],
                "author": v.get("authorMeta", {}).get("name", v.get("author", "")),
                "plays": v.get("playCount", ""),
                "likes": v.get("diggCount", ""),
                "comments": v.get("commentCount", ""),
                "shares": v.get("shareCount", ""),
                "hashtags": [h.get("name", "") for h in v.get("hashtag", [])
                            ] if isinstance(v.get("hashtag"), list) else [],
                "url": v.get("webVideoUrl", v.get("videoUrl", "")),
                "unified_score": score,
                "score_details": details,
                "source": "apify_video",
            })
        merged.sort(key=lambda x: x["unified_score"], reverse=True)
        return merged

    # ── Full fusion (Shop + Video + Search) ───────────────────

    def merge_all(
        self,
        shop_products: list[dict],
        hashtag_videos: list[dict],
        search_videos: list[dict],
    ) -> dict:
        """Full fusion: products + videos + cross-referencing."""
        return {
            "products": self.merge_products(shop_products),
            "hashtag_videos": self.merge_videos(hashtag_videos),
            "search_videos": self.merge_videos(search_videos),
            "top_categories": self._extract_categories(shop_products),
            "trending_hashtags": self._extract_hashtags(hashtag_videos),
        }

    def _extract_categories(self, products: list[dict]) -> dict:
        """Group products by category and count."""
        cats = {}
        for p in products:
            cat = p.get("categoryName", p.get("category", "Uncategorized"))
            cats[cat] = cats.get(cat, 0) + 1
        return dict(sorted(cats.items(), key=lambda x: -x[1])[:10])

    def _extract_hashtags(self, videos: list[dict]) -> list[str]:
        """Extract top hashtags from videos."""
        ht = {}
        for v in videos:
            hashtags = v.get("hashtag", []) if isinstance(v.get("hashtag"), list) else []
            for h in hashtags:
                name = h.get("name", "") if isinstance(h, dict) else str(h)
                if name:
                    ht[name] = ht.get(name, 0) + 1
        return [h for h, _ in sorted(ht.items(), key=lambda x: -x[1])[:20]]

    # ── Scoring for query matching ────────────────────────────

    def score_query_match(self, query: str, products: list[dict], 
                          videos: list[dict]) -> dict:
        """Score how well a query matches products + videos.

        Returns top 10 matches across both sources.
        """
        query_lower = query.lower()
        results = []

        for p in products:
            title = (p.get("title", "") or "").lower()
            if query_lower in title:
                s, d = self.score_product(p)
                results.append({
                    "type": "product",
                    "title": p.get("title"),
                    "score": s + 10,  # Bonus for exact match
                    "details": d,
                })

        for v in videos:
            desc = (v.get("desc", "") or "").lower()
            if query_lower in desc:
                s, d = self.score_video(v)
                results.append({
                    "type": "video",
                    "title": (v.get("desc", "") or "")[:100],
                    "score": s + 5,
                    "details": d,
                })

        results.sort(key=lambda x: -x["score"])
        return {"query": query, "matches": results[:10]}


# ── Helpers ──────────────────────────────────────────────────

def _parse_num(value) -> float:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).replace(",", "").strip()
    mults = {"K": 1000, "M": 1000000, "B": 1000000000}
    for s, m in mults.items():
        if value.upper().endswith(s):
            try:
                return float(value.upper().replace(s, "")) * m
            except ValueError:
                return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
