"""Report Generator for TikTok Intelligence.

Generates weekly reports from fused data:
- Top 100 Products
- Category Rankings
- Competitor Grid
- Influencer Matches
- Launch Opportunities
"""

import json
from datetime import datetime
from typing import Optional

import pandas as pd


class ReportGenerator:
    """Generate reports from fused TikTok data."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or "."

    def generate_weekly_report(self, fused_products: list[dict], fused_competitors: list[dict]) -> dict:
        """Generate comprehensive weekly report.

        Returns:
            dict with:
            - top_100_products: List of top 100 products
            - category_rankings: Category overview
            - competitor_grid: Top competitors
            - launch_opportunities: Recent launches
            - generated_at: Timestamp
        """
        report = {
            "top_100_products": self._get_top_products(fused_products, 100),
            "category_rankings": self._get_category_rankings(fused_products),
            "competitor_grid": self._get_competitor_grid(fused_competitors),
            "launch_opportunities": self._get_launch_opportunities(fused_products),
            "generated_at": datetime.now().isoformat(),
            "source_count": {
                "simptok": sum(1 for p in fused_products if "simptok" in p.get("sources", [])),
                "echotik": sum(1 for p in fused_products if "echotik" in p.get("sources", [])),
                "scrapling": sum(1 for p in fused_products if "scrapling" in p.get("sources", [])),
            },
        }
        return report

    def generate_influencer_report(self, influencers: list[dict], products: list[dict]) -> dict:
        """Generate influencer matching report.

        Matches influencers to trending products based on category alignment.
        """
        report = {
            "influencers": influencers[:50],
            "product_matches": self._match_influencers_to_products(influencers, products),
            "generated_at": datetime.now().isoformat(),
        }
        return report

    def export_to_csv(self, report: dict, filename: str) -> str:
        """Export report to CSV files.

        Returns:
            Path to output directory
        """
        import os

        out_dir = os.path.join(self.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        # Top products
        if report.get("top_100_products"):
            df = pd.DataFrame(report["top_100_products"])
            df.to_csv(os.path.join(out_dir, "top_100_products.csv"), index=False)

        # Competitors
        if report.get("competitor_grid"):
            df = pd.DataFrame(report["competitor_grid"])
            df.to_csv(os.path.join(out_dir, "competitor_grid.csv"), index=False)

        # Category rankings
        if report.get("category_rankings"):
            df = pd.DataFrame(report["category_rankings"])
            df.to_csv(os.path.join(out_dir, "category_rankings.csv"), index=False)

        # Full JSON
        with open(os.path.join(out_dir, "full_report.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)

        return out_dir

    def _get_top_products(self, products: list[dict], limit: int = 100) -> list[dict]:
        """Get top N products by unified score."""
        sorted_products = sorted(products, key=lambda x: x.get("unified_score", 0), reverse=True)
        return sorted_products[:limit]

    def _get_category_rankings(self, products: list[dict]) -> list[dict]:
        """Aggregate products by category."""
        categories = {}
        for product in products:
            cat = product.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = {
                    "category": cat,
                    "product_count": 0,
                    "total_revenue": 0,
                    "avg_score": 0,
                    "top_product": None,
                }
            categories[cat]["product_count"] += 1
            categories[cat]["total_revenue"] += product.get("revenue", 0) or 0
            categories[cat]["avg_score"] += product.get("unified_score", 0)

            if categories[cat]["top_product"] is None or product.get("unified_score", 0) > categories[cat]["top_product"].get("unified_score", 0):
                categories[cat]["top_product"] = product

        # Calculate averages
        for cat in categories.values():
            if cat["product_count"] > 0:
                cat["avg_score"] = round(cat["avg_score"] / cat["product_count"], 2)

        # Sort by avg score
        return sorted(categories.values(), key=lambda x: x["avg_score"], reverse=True)

    def _get_competitor_grid(self, competitors: list[dict]) -> list[dict]:
        """Get top competitors."""
        return sorted(competitors, key=lambda x: x.get("rank", 999))[:50]

    def _get_launch_opportunities(self, products: list[dict]) -> list[dict]:
        """Identify launch opportunities (high growth, low saturation)."""
        opportunities = []
        for product in products:
            score = product.get("unified_score", 0)
            growth = product.get("growth", 0)
            if score > 70 and growth > 0.2:
                opportunities.append({
                    "title": product.get("title"),
                    "score": score,
                    "growth": growth,
                    "price": product.get("price"),
                    "category": product.get("category"),
                    "reason": "High score + strong growth",
                })
        return sorted(opportunities, key=lambda x: x["score"], reverse=True)[:20]

    def _match_influencers_to_products(self, influencers: list[dict], products: list[dict]) -> list[dict]:
        """Match influencers to products by category."""
        matches = []
        for product in products[:20]:
            product_category = product.get("category", "")
            matched_influencers = [
                inf for inf in influencers
                if product_category.lower() in (inf.get("category", "") or "").lower()
            ]
            if matched_influencers:
                matches.append({
                    "product": product.get("title"),
                    "category": product_category,
                    "influencers": [
                        {
                            "name": inf.get("name"),
                            "followers": inf.get("followers"),
                            "sales_score": inf.get("sales_score"),
                        }
                        for inf in matched_influencers[:5]
                    ],
                })
        return matches

    def print_summary(self, report: dict):
        """Print human-readable summary to console."""
        print("\n" + "=" * 60)
        print("  SIN TIKTOK INTELLIGENCE WEEKLY REPORT")
        print("=" * 60)
        print(f"\nGenerated: {report.get('generated_at', 'N/A')}")
        print(f"Sources: {report.get('source_count', {})}")

        print("\n  TOP 10 PRODUCTS")
        print("-" * 60)
        for i, product in enumerate(report.get("top_100_products", [])[:10], 1):
            print(f"  {i}. {product.get('title', 'N/A')[:50]}")
            print(f"     Score: {product.get('unified_score', 0)} | Revenue: {product.get('revenue', 0)} | Growth: {product.get('growth', 0)}")

        print("\n  TOP 5 CATEGORIES")
        print("-" * 60)
        for i, cat in enumerate(report.get("category_rankings", [])[:5], 1):
            print(f"  {i}. {cat.get('category', 'N/A')}")
            print(f"     Products: {cat.get('product_count', 0)} | Avg Score: {cat.get('avg_score', 0)}")

        print("\n  TOP 5 COMPETITORS")
        print("-" * 60)
        for i, comp in enumerate(report.get("competitor_grid", [])[:5], 1):
            print(f"  {i}. {comp.get('name', 'N/A')}")
            print(f"     Rank: {comp.get('rank', 'N/A')} | Revenue: {comp.get('revenue', 0)}")

        print("\n  LAUNCH OPPORTUNITIES")
        print("-" * 60)
        for i, opp in enumerate(report.get("launch_opportunities", [])[:5], 1):
            print(f"  {i}. {opp.get('title', 'N/A')[:50]}")
            print(f"     Score: {opp.get('score', 0)} | Growth: {opp.get('growth', 0)}")

        print("\n" + "=" * 60)
