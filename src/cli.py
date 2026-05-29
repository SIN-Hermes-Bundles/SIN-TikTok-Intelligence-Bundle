#!/usr/bin/env python3
"""SIN TikTok Intelligence CLI v2.

Primary: Apify TikTok Shop Scraper (PRO100CHOK actor)
Secondary: Scrapeless TikTok API

Usage:
    python3 -m src.cli --action weekly-report --keyword "skincare"
    python3 -m src.cli --action top-products --keyword "phone case" --limit 50
    python3 -m src.cli --action category --category "beauty"
    python3 -m src.cli --action store --store "TikTokShop"
    python3 -m src.cli --action reviews --url "https://..."
    python3 -m src.cli --action hashtags --query "#makeup"
"""

import argparse
import json
import sys

from src.clients.apify_client import ApifyTikTokClient
from src.clients.scrapeless_client import ScrapelessClient
from src.fusion.trend_engine import TrendEngine
from src.fusion.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="SIN TikTok Intelligence Bundle v2")
    parser.add_argument("--action", required=True, choices=[
        "weekly-report", "top-products", "category", "store",
        "creator", "reviews", "hashtags", "videos", "live",
    ])
    parser.add_argument("--keyword", default="", help="Search keyword")
    parser.add_argument("--category", default="", help="Category name")
    parser.add_argument("--store", default="", help="Store name")
    parser.add_argument("--creator", default="", help="Creator username")
    parser.add_argument("--url", default="", help="Product URL for reviews")
    parser.add_argument("--limit", type=int, default=50, help="Max items")
    parser.add_argument("--region", default="us", help="Region (us, uk, de)")
    parser.add_argument("--format", default="summary", choices=["json", "csv", "summary"])
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--use-scrapeless", action="store_true", help="Also use Scrapeless")

    args = parser.parse_args()

    apify = ApifyTikTokClient()
    scrapeless = ScrapelessClient() if args.use_scrapeless else None
    engine = TrendEngine(apify, scrapeless)
    reporter = ReportGenerator(args.output)

    try:
        if args.action == "weekly-report":
            _weekly_report(args, apify, scrapeless, engine, reporter)

        elif args.action == "top-products":
            if not args.keyword:
                print("Error: --keyword required")
                sys.exit(1)
            products = apify.search_products(args.keyword, args.limit, region=args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "category":
            if not args.category:
                print("Error: --category required")
                sys.exit(1)
            products = apify.get_category_products(args.category, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "store":
            if not args.store:
                print("Error: --store required")
                sys.exit(1)
            products = apify.get_store_products(args.store, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "creator":
            if not args.creator:
                print("Error: --creator required")
                sys.exit(1)
            products = apify.get_creator_products(args.creator, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "reviews":
            if not args.url:
                print("Error: --url required")
                sys.exit(1)
            reviews = apify.get_product_reviews(args.url, args.limit, region=args.region)
            _output(reviews, args)

        elif args.action == "hashtags":
            query = args.keyword or "#trending"
            hashtags = [] if not scrapeless else scrapeless.get_hashtag_trends(query)
            _output(hashtags, args)

        elif args.action == "videos":
            keyword = args.keyword or ""
            videos = [] if not scrapeless else scrapeless.get_top_videos(keyword, args.limit)
            _output(videos, args)

        elif args.action == "live":
            lives = [] if not scrapeless else scrapeless.get_live_streams(args.limit)
            _output(lives, args)

    finally:
        if scrapeless:
            scrapeless.close()


def _weekly_report(args, apify, scrapeless, engine, reporter):
    """Generate weekly intelligence report."""
    keyword = args.keyword or "trending"
    print(f"Generating weekly report for: {keyword}...")
    print()

    # Fetch from Apify
    print(f"[Apify] Searching '{keyword}'...")
    apify_products = apify.search_products(keyword, args.limit, region=args.region)
    print(f"[Apify] Found {len(apify_products)} products")

    # Optionally fetch Scrapeless
    scrapeless_hashtags = []
    if scrapeless:
        print(f"[Scrapeless] Fetching hashtag trends...")
        scrapeless_hashtags = scrapeless.get_hashtag_trends(keyword.replace("#", ""))
        print(f"[Scrapeless] Found {len(scrapeless_hashtags)} hashtags")

    # Fusion
    merged = engine.merge_products(apify_products, scrapeless_hashtags)

    # Report
    report = reporter.generate_weekly_report(
        fused_products=merged,
        fused_competitors=[],  # TBD: store-based competitors
    )

    # Add metadata
    report["keyword"] = keyword
    report["region"] = args.region
    report["apify_count"] = len(apify_products)
    report["scrapeless_count"] = len(scrapeless_hashtags)

    _output_report(report, args)


def _output(data, args):
    """Output data in requested format."""
    if args.format == "json":
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
    elif args.format == "csv":
        import pandas as pd
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        print(df.to_csv(index=False))
    elif args.format == "summary":
        if isinstance(data, list):
            print(f"\nResults: {len(data)}")
            for i, item in enumerate(data[:10], 1):
                title = item.get("title", item.get("name", str(item)[:50]))
                score = item.get("unified_score", item.get("score", ""))
                price = item.get("price", "")
                sales = item.get("sales", item.get("salesCount", ""))
                print(f"  {i:>2}. {title[:60]}")
                if score:
                    print(f"      Score: {score} | Price: {price} | Sales: {sales}")
        else:
            print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def _output_report(report, args):
    """Output report in requested format."""
    if args.format == "json":
        print(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    elif args.format == "csv":
        out_dir = ReportGenerator(args.output).export_to_csv(report, "weekly_report")
        print(f"CSV exported to: {out_dir}")
    elif args.format == "summary":
        ReportGenerator(args.output).print_summary(report)


if __name__ == "__main__":
    main()
