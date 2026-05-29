#!/usr/bin/env python3
"""SIN TikTok Intelligence CLI.

Usage:
    python3 -m src.cli --action weekly-report --category "beauty"
    python3 -m src.cli --action top-products --limit 50
    python3 -m src.cli --action competitor-grid --category "electronics"
    python3 -m src.cli --action influencer-report --category "fashion"
"""

import argparse
import json
import sys

from src.clients.simptok_client import SimpTokClient
from src.clients.echotik_client import EchoTikClient
from src.clients.scrapling_fallback import ScraplingFallback
from src.fusion.trend_engine import TrendEngine
from src.fusion.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="SIN TikTok Intelligence Bundle")
    parser.add_argument("--action", required=True, choices=[
        "weekly-report", "top-products", "competitor-grid", "influencer-report",
        "trending-categories", "launches", "product-detail",
    ])
    parser.add_argument("--category", default="", help="Product category")
    parser.add_argument("--limit", type=int, default=100, help="Limit results")
    parser.add_argument("--product-id", help="Product ID for detail")
    parser.add_argument("--region", default="US", help="Region (US, UK, DE, etc)")
    parser.add_argument("--format", default="json", choices=["json", "csv", "summary"])
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--use-scrapling", action="store_true", help="Include Scrapling fallback")

    args = parser.parse_args()

    # Initialize clients
    simptok = SimpTokClient()
    echotik = EchoTikClient()
    scrapling = ScraplingFallback() if args.use_scrapling else None
    engine = TrendEngine(simptok, echotik, scrapling)
    reporter = ReportGenerator(args.output)

    try:
        if args.action == "weekly-report":
            # Fetch data from all sources
            simptok_products = simptok.get_top_products(args.category, args.region, args.limit)
            echotik_products = echotik.get_products("top_sold", args.category, args.limit)
            simptok_competitors = simptok.get_competitor_grid(args.category, args.region)
            echotik_shops = echotik.get_shops("best_seller", args.region, args.limit)

            # Fusion
            fused_products = engine.fuse_products(simptok_products, echotik_products)
            fused_competitors = engine.fuse_competitors(simptok_competitors, echotik_shops)

            # Report
            report = reporter.generate_weekly_report(fused_products, fused_competitors)
            _output_report(report, args)

        elif args.action == "top-products":
            simptok_products = simptok.get_top_products(args.category, args.region, args.limit)
            echotik_products = echotik.get_products("top_sold", args.category, args.limit)
            fused = engine.fuse_products(simptok_products, echotik_products)
            _output_json(fused[:args.limit], args)

        elif args.action == "competitor-grid":
            simptok_competitors = simptok.get_competitor_grid(args.category, args.region)
            echotik_shops = echotik.get_shops("best_seller", args.region, args.limit)
            fused = engine.fuse_competitors(simptok_competitors, echotik_shops)
            _output_json(fused, args)

        elif args.action == "influencer-report":
            echotik_influencers = echotik.get_influencers("sales_champion", args.category, args.limit)
            echotik_products = echotik.get_products("top_sold", args.category, 50)
            report = reporter.generate_influencer_report(echotik_influencers, echotik_products)
            _output_report(report, args)

        elif args.action == "trending-categories":
            categories = simptok.get_trending_categories(args.region)
            _output_json(categories, args)

        elif args.action == "launches":
            launches = simptok.get_launches(7, args.region)
            _output_json(launches, args)

        elif args.action == "product-detail":
            if not args.product_id:
                print("Error: --product-id required")
                sys.exit(1)
            detail = echotik.get_product_detail(args.product_id)
            _output_json(detail, args)

    finally:
        simptok.close()
        echotik.close()
        if scrapling:
            scrapling.close()


def _output_json(data, args):
    if args.format == "json":
        print(json.dumps(data, indent=2, default=str))
    elif args.format == "csv":
        import pandas as pd
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        print(df.to_csv(index=False))
    elif args.format == "summary":
        print(f"Results: {len(data) if isinstance(data, list) else 1}")
        if isinstance(data, list) and data:
            print(f"First: {data[0].get('title', data[0])}")


def _output_report(report, args):
    if args.format == "json":
        print(json.dumps(report, indent=2, default=str))
    elif args.format == "csv":
        out_dir = ReportGenerator(args.output).export_to_csv(report, "report")
        print(f"CSV exported to: {out_dir}")
    elif args.format == "summary":
        ReportGenerator(args.output).print_summary(report)


if __name__ == "__main__":
    main()
