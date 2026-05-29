#!/usr/bin/env python3
"""SIN TikTok Intelligence CLI v2.

THREE data sources:
1. Apify clockworks/tiktok-scraper (GENERAL): Videos, Hashtags, Profiles, Search
2. Apify pro100chok/tiktok-shop-scraper-usage (SHOP): Products, Prices, Sales
3. Scrapeless (SECONDARY): Cross-check, additional data

Usage:
    python3 -m src.cli --action weekly-report --keyword "skincare"
    python3 -m src.cli --action trends --hashtag "#TikTokMadeMeBuyIt" --limit 100
    python3 -m src.cli --action video-search --query "phone case review" --limit 50
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.apify_client import ApifyTikTokVideoClient, ApifyTikTokShopClient
from src.fusion.trend_engine import TrendEngine
from src.fusion.report_generator import ReportGenerator
from src.affiliate import (
    AffiliateEligibilityChecker,
    AffiliateLinkGenerator,
    CommissionEstimator,
)


def main():
    parser = argparse.ArgumentParser(description="SIN TikTok Intelligence Bundle v2")
    parser.add_argument("--action", required=True, choices=[
        "weekly-report",
        "trends",
        "video-search",
        "profiles",
        "products",
        "full-research",
        "category",
        "store",
        "creator",
        "reviews",
        "hashtags",
        "videos",
        "live",
        "affiliate-research",
        "best-deal",
    ])
    parser.add_argument("--keyword", default="", help="Search keyword")
    parser.add_argument("--hashtag", default="", help="Hashtag (with #)")
    parser.add_argument("--query", default="", help="Search query")
    parser.add_argument("--usernames", default="", help="Comma-separated usernames")
    parser.add_argument("--category", default="", help="Shop category")
    parser.add_argument("--store", default="", help="Store name")
    parser.add_argument("--creator", default="", help="Creator username")
    parser.add_argument("--url", default="", help="Product URL for reviews")
    parser.add_argument("--limit", type=int, default=50, help="Max items")
    parser.add_argument("--region", default="us")
    parser.add_argument("--format", default="summary", choices=["json", "csv", "summary"])
    parser.add_argument("--output", default=".", help="Output directory")

    args = parser.parse_args()

    video = ApifyTikTokVideoClient()
    shop = ApifyTikTokShopClient()
    engine = TrendEngine(shop, video)
    reporter = ReportGenerator(args.output)

    try:
        if args.action == "weekly-report":
            kw = args.keyword or "trending"
            print(f"=== TikTok Intelligence Weekly Report: {kw} ===\n")

            # 1. TikTok Shop products
            print("[Apify Shop] Searching products...")
            products = shop.search_products(kw, args.limit, region=args.region)
            print(f"  Found {len(products)} products")

            # 2. Hashtag trends (video data)
            hashtag = args.hashtag or f"#{kw.replace(' ', '')}"
            print(f"[Apify Video] Hashtag: {hashtag}...")
            videos = video.search_hashtags([hashtag], min(args.limit, 100))
            print(f"  Found {len(videos)} videos")

            # 3. Video search
            print(f"[Apify Video] Search: {kw}...")
            search_vids = video.search_videos([kw], args.limit)
            print(f"  Found {len(search_vids)} search results")

            # 4. Fusion
            merged = engine.merge_all(
                shop_products=products,
                hashtag_videos=videos,
                search_videos=search_vids,
            )

            # 5. Report
            report = reporter.generate_weekly_report(
                fused_products=merged,
                fused_competitors=[],
            )
            report["keyword"] = kw
            report["sources"] = {
                "shop_products": len(products),
                "hashtag_videos": len(videos),
                "search_videos": len(search_vids),
            }

            _output_report(report, args)

        elif args.action == "trends":
            hashtag = args.hashtag or "#fyp"
            print(f"Hashtag: {hashtag}")
            videos = video.search_hashtags([hashtag], args.limit)
            _output(videos, args)

        elif args.action == "video-search":
            q = args.query or args.keyword
            videos = video.search_videos([q], args.limit)
            _output(videos, args)

        elif args.action == "profiles":
            users = [u.strip() for u in args.usernames.split(",") if u.strip()]
            profiles = video.get_profiles(users, args.limit)
            _output(profiles, args)

        elif args.action == "products":
            products = shop.search_products(args.keyword, args.limit, region=args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "full-research":
            kw = args.keyword or "trending"
            print(f"Full research: {kw}...")
            print("  Step 1/2: Searching products...")
            research = shop.full_research(kw, args.limit, region=args.region)
            print(f"  Step 2/2: Getting prices, sales, stores...")
            _output_research(research, args)

        elif args.action == "category":
            products = shop.get_category(args.category, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "store":
            products = shop.get_store(args.store, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "creator":
            products = shop.get_creator(args.creator, args.limit, args.region)
            merged = engine.merge_products(products)
            _output(merged, args)

        elif args.action == "reviews":
            reviews = shop.get_reviews(args.url, args.limit, region=args.region)
            _output(reviews, args)

        elif args.action == "affiliate-research":
            kw = args.keyword or "trending"
            print(f"Affiliate Research: {kw}")
            print("  Step 1/3: Scraping products...")
            research = shop.full_research(kw, max(args.limit, 10), region=args.region)
            products = research["products"]
            print(f"  Step 2/3: Checking affiliate eligibility...")
            checker = AffiliateEligibilityChecker()
            eligible = checker.top_affiliate_picks(products, n=args.limit)
            print(f"  Step 3/3: Estimating commissions...")
            estimator = CommissionEstimator()
            for p in eligible:
                p["_commission"] = estimator.estimate(p)
            gen = AffiliateLinkGenerator()
            for p in eligible:
                p["_links"] = gen.generate(p)
            _output_affiliate(eligible, args)

        elif args.action == "best-deal":
            kw = args.keyword or "trending"
            print(f"Finding best affiliate deal: {kw}")
            research = shop.full_research(kw, max(args.limit, 20), region=args.region)
            products = research["products"]
            gen = AffiliateLinkGenerator()
            best = gen.best_deal(products)
            if best:
                estimator = CommissionEstimator()
                best["_commission"] = estimator.estimate(best)
                print(f"\n  BEST DEAL: {best.get('title', 'N/A')[:60]}")
                print(f"  Price: ${best.get('current_price')} | Sold: {best.get('sales_volume')}")
                print(f"  Shop: {best.get('seller_name')}")
                est = best["_commission"]
                print(f"  Est. Commission: {est['commission_rate']*100}% = ${est['est_earnings_per_sale']}/sale")
                print(f"  Est. Total Earnings: ${est['est_total_earnings']}")
                links = best.get("_links", {})
                print(f"  Affiliate URL: {links.get('affiliate_url', 'N/A')[:80]}")
                print(f"  Share: {links.get('share_text', '')[:100]}...")
            else:
                print("  No products found.")

        else:
            print(f"Unknown action: {args.action}")

    except RuntimeError as e:
        print(f"\nError: {e}")
        print("Did you set APIFY_API_TOKEN? Get it free from apify.com → Settings → API Token")
        sys.exit(1)


def _output(data, args):
    if args.format == "json":
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
    elif args.format == "csv":
        import pandas as pd
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        print(df.to_csv(index=False))
    else:
        if isinstance(data, list):
            print(f"\nResults: {len(data)} items")
            for i, item in enumerate(data[:args.limit or 10], 1):
                title = item.get("title", item.get("text", item.get("desc", str(item)[:60])))
                score = item.get("unified_score", "")
                price = item.get("price", "")
                plays = item.get("playCount", item.get("plays", ""))
                likes = item.get("diggCount", item.get("likes", ""))
                sales = item.get("salesCount", item.get("sales", ""))
                print(f"  {i:>2}. {str(title)[:60]}")
                if score:
                    print(f"      Score: {score}", end="")
                if price:
                    print(f" | Price: {price}", end="")
                if sales:
                    print(f" | Sales: {sales}", end="")
                if plays:
                    print(f" | Plays: {plays}", end="")
                if likes:
                    print(f" | Likes: {likes}", end="")
                print()


def _output_report(report, args):
    if args.format == "json":
        print(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    elif args.format == "csv":
        gen = ReportGenerator(args.output)
        out = gen.export_to_csv(report, "weekly_report")
        print(f"CSV: {out}")
    else:
        ReportGenerator(args.output).print_summary(report)


def _output_research(research, args):
    """Output full research results."""
    products = research.get("products", [])
    if args.format == "json":
        print(json.dumps(research, indent=2, default=str, ensure_ascii=False))
    elif args.format == "csv":
        import pandas as pd
        df = pd.DataFrame(products)
        print(df.to_csv(index=False))
    else:
        print(f"\nResearch: {research['keyword']}")
        print(f"  Products found: {research['search_count']}")
        print(f"  With full details: {research['detail_count']}")
        print()
        for i, p in enumerate(products[:10], 1):
            price = p.get('current_price', '?')
            orig = p.get('original_price', '-')
            sold = p.get('sales_volume', '?')
            last30 = p.get('sold_last_30_days', '')
            last30_str = f" | 30d: {last30}" if last30 else ""
            global_s = p.get('global_sold', '')
            global_str = f" | Global: {global_s}" if global_s else ""
            variants = p.get('variants', [])
            var_str = f" | Variants: {len(variants)}" if variants else ""

            print(f"  {i:>2}. {p.get('title', 'N/A')[:60]}")
            print(f"      Price: ${price} | Orig: ${orig} | Sold: {sold}{last30_str}{global_str}{var_str}")
            print(f"      Rating: {p.get('rating')} ★ | Reviews: {p.get('review_count')}")
            print(f"      Shop: {p.get('seller_name')} (★{p.get('shop_rating')} | {p.get('shop_total_sold')} sold | {p.get('shop_followers')} followers)")
            print(f"      URL: {p.get('product_url', '')[:80]}")
            print(f"      Shop URL: {p.get('shop_url', '')[:80]}")
            shipping = p.get('shipping')
            if shipping:
                print(f"      Shipping: {'FREE' if shipping.get('freeShipping') else 'Paid'}")
        if len(products) < 1:
            print("  ⚠️  No detail data returned. Search results may have limited info.")


def _output_affiliate(products, args):
    """Output affiliate research results."""
    if args.format == "json":
        # Clean up internal fields for JSON
        cleaned = []
        for p in products:
            c = {k: v for k, v in p.items() if not k.startswith("_")}
            c["affiliate_check"] = p.get("_affiliate_check", {})
            c["commission_estimate"] = p.get("_commission", {})
            c["links"] = p.get("_links", {})
            cleaned.append(c)
        print(json.dumps(cleaned, indent=2, default=str, ensure_ascii=False))
    else:
        gen = AffiliateLinkGenerator()
        print(f"\n{'='*70}")
        print("  AFFILIATE RESEARCH RESULTS")
        print(f"  {'='*70}")
        print(f"  Products researched: {len(products)}")
        total_est = sum(
            p.get("_commission", {}).get("est_total_earnings", 0)
            for p in products
        )
        print(f"  Est. Total Affiliate Earnings: ${total_est:,.2f}")
        print()
        for i, p in enumerate(products[:args.limit or 10], 1):
            check = p.get("_affiliate_check", {})
            comm = p.get("_commission", {})
            links = p.get("_links", {})
            score = p.get("_affiliate_score", 0)
            icon = "🟢" if check.get("eligible") else "🟡"

            print(f"  {icon} #{i} [{check.get('confidence', 0)*100:.0f}% confidence] Score: {score}")
            print(f"     {p.get('title', 'N/A')[:65]}")
            print(f"     ${p.get('current_price')} | Sold: {p.get('sales_volume')} | ★{p.get('rating')}")
            print(f"     Shop: {p.get('seller_name')} (★{p.get('shop_rating')} | {p.get('shop_total_sold')} sold)")
            print(f"     Est. Commission: {comm.get('commission_rate', 0)*100:.0f}% = ${comm.get('est_earnings_per_sale', 0):.2f}/sale")
            print(f"     Est. Total: ${comm.get('est_total_earnings', 0):,.2f}")
            aff_url = links.get("affiliate_url", "")
            print(f"     Link: {aff_url[:90]}")
            if links.get("_note"):
                print(f"     ⚠️  {links['_note']}")
            variants = p.get("variants", [])
            if variants:
                v_str = ", ".join(
                    f"{v.get('name','?')} ${v.get('price','?')}"
                    for v in variants[:3]
                )
                print(f"     Variants: {v_str}")
            print()


if __name__ == "__main__":
    main()
