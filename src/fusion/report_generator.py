"""Report Generator for TikTok Intelligence Bundle.

Output: console summary, JSON, CSV.
"""

import csv
import json
import os
from datetime import datetime
from typing import Optional


class ReportGenerator:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_weekly_report(
        self,
        fused_products: list[dict],
        fused_competitors: list[dict] = None,
    ) -> dict:
        return {
            "generated_at": datetime.now().isoformat(),
            "total_products": len(fused_products),
            "top_10": fused_products[:10],
            "competitors": (fused_competitors or [])[:5],
            "top_categories": self._group_by_category(fused_products),
            "top_stores": self._group_by_store(fused_products),
        }

    def _group_by_category(self, products: list[dict]) -> dict:
        cats = {}
        for p in products:
            cat = p.get("category", p.get("store", "Other"))
            cats[cat] = cats.get(cat, 0) + 1
        return dict(sorted(cats.items(), key=lambda x: -x[1])[:10])

    def _group_by_store(self, products: list[dict]) -> dict:
        stores = {}
        for p in products:
            s = p.get("store", p.get("storeName", "Unknown"))
            stores[s] = stores.get(s, 0) + 1
        return dict(sorted(stores.items(), key=lambda x: -x[1])[:10])

    def print_summary(self, report: dict):
        """Console output — human readable."""
        print("\n" + "=" * 60)
        print("  SIN TikTok Intelligence — Weekly Report")
        print("=" * 60)
        print(f"  Generated: {report['generated_at'][:19]}")
        print(f"  Products: {report['total_products']}")

        print("\n── Top 10 Products ──")
        for i, p in enumerate(report.get("top_10", [])[:10], 1):
            title = p.get("title", "N/A")[:50]
            score = p.get("unified_score", "—")
            price = p.get("price", "—")
            sales = p.get("sales", "—")
            print(f"  {i:>2}. {title}")
            print(f"      Score: {score} | Price: {price} | Sales: {sales}")

        print("\n── Top Categories ──")
        for cat, count in report.get("top_categories", {}).items():
            print(f"  {cat}: {count} products")

        print("\n── Top Stores ──")
        for store, count in report.get("top_stores", {}).items():
            print(f"  {store}: {count} products")

        print("\n" + "=" * 60)

    def export_to_csv(self, report: dict, name: str = "report") -> str:
        path = os.path.join(self.output_dir, f"{name}_{datetime.now():%Y%m%d_%H%M}.csv")
        products = report.get("top_10", report.get("products", []))
        if not products:
            return path
        fields = ["title", "price", "sales", "rating", "reviews", "store", "unified_score", "url"]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(products)
        return path

    def export_to_json(self, report: dict, name: str = "report") -> str:
        path = os.path.join(self.output_dir, f"{name}_{datetime.now():%Y%m%d_%H%M}.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        return path
