# SIN-TikTok-Intelligence-Bundle

**Free TikTok Shop Intelligence Bundle for Hermes Agent.**

Fuses **SimpTok** (Free Tier) + **EchoTik** (Free Tier) + **Scrapling** (Open Source) into a unified trend monitoring system.

## What It Does

1. **Finds trending products** on TikTok Shop (Top 100 weekly)
2. **Tracks competitors** (rank, revenue, pricing)
3. **Identifies influencers** matched to products
4. **Monitors launches** (new products, velocity signals)
5. **Generates reports** (JSON, CSV, human-readable summary)

## Why This Bundle

| Problem | Solution |
|---------|----------|
| Kalodata costs $$$/month | **This bundle is FREE** |
| No single free API covers everything | **Fuses 3 sources** |
| Free tiers have limits | **Round-robin + fallback** |
| TikTok Shop not publicly scrapable | **Uses official APIs + Scrapling fallback** |

## Architecture

```
SimpTok (Free)      EchoTik (Free)      Scrapling (Open Source)
    |                    |                      |
    | Category Revenue   | Product Library      | Hashtag Trends
    | Competitor Grid    | Shop Rankings        | Video Search
    | Top Products       | Influencer Data      | Affiliate Fallback
    | Launch Tracker     | Live Streams         |
    |                    |                      |
    +--------------------+----------------------+
                         |
                         v
              Fusion Engine (Weighted)
                         |
              Unified Trend Score (0-100)
                         |
                         v
              Report Generator
                         |
         +---------------+---------------+
         |               |               |
    Weekly Report   Top 100      Competitor Grid
    JSON/CSV        Products     Influencer Match
```

## Quick Start

```bash
# One-command install
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-TikTok-Intelligence-Bundle/main/install.sh | bash

# Add your API keys (free, no credit card)
~/.hermes/bundles/tiktok-intelligence/config/simptok.json
~/.hermes/bundles/tiktok-intelligence/config/echotik.json

# Generate weekly report
cd ~/.hermes/bundles/tiktok-intelligence && python3 -m src.cli --action weekly-report --format summary

# Or use Hermes skills:
# "finde tiktok trends"
# "recherchiere produkt"
# "competitor grid"
```

## API Keys (Free)

### SimpTok
- Website: https://simptok.com
- Plan: Free tier (no credit card)
- Limits: Limited exports, 90-day history
- Get key: Sign up with email

### EchoTik
- Website: https://echotik.live
- Plan: Free ($0/month)
- Limits: 100 daily views, basic filters
- Get key: Sign up with email

### Scrapling
- Repo: https://github.com/D4Vinci/Scrapling
- License: BSD 3-Clause (Open Source)
- Cost: **FREE** — self-hosted
- Limits: None

## CLI Usage

```bash
# Weekly report (all sources)
python3 -m src.cli --action weekly-report --category "beauty" --format summary

# Top 100 products
python3 -m src.cli --action top-products --limit 100 --format json

# Competitor grid
python3 -m src.cli --action competitor-grid --category "electronics" --format csv

# Influencer report
python3 -m src.cli --action influencer-report --category "fashion" --format json

# With Scrapling fallback
python3 -m src.cli --action weekly-report --use-scrapling

# Export to CSV
python3 -m src.cli --action weekly-report --format csv --output ./reports
```

## Fusion Engine

| Source | Weight | Data |
|--------|--------|------|
| SimpTok AI Opportunity Score | 40% | Category revenue, growth, saturation |
| EchoTik Trend Rank | 30% | Product rank, sales velocity |
| Scrapling Velocity | 30% | Hashtag trends, video views |

**Output:** Unified Trend Score (0-100) per product

## Free Tier Strategy

| Tool | Free Tier | Limit | Workaround |
|------|-----------|-------|------------|
| SimpTok | Core metrics | Limited exports | API + local storage |
| EchoTik | $0 plan | 100 views/day | Multi-account rotation |
| Scrapling | 100% open source | None | Self-hosted |

## Hermes Skills

### sin-tiktok-trend-finder
**Trigger:** "finde tiktok trends", "top produkte tiktok", "weekly report"

Finds top 100 trending products with unified score.

### sin-tiktok-product-research
**Trigger:** "recherchiere produkt", "analysiere produkt", "produkt detail"

Deep product analysis: price, revenue, growth, competitors, creators.

### sin-tiktok-competitor-monitor
**Trigger:** "competitor grid", "wer ist marktfuehrer", "monitor competitor"

Competitor rankings, market share, pricing intelligence.

## Directory Structure

```
SIN-TikTok-Intelligence-Bundle/
|-- install.sh
|-- requirements.txt
|-- src/
|   |-- cli.py
|   |-- clients/
|   |   |-- simptok_client.py
|   |   |-- echotik_client.py
|   |   |-- scrapling_fallback.py
|   |-- fusion/
|   |   |-- trend_engine.py
|   |   |-- report_generator.py
|-- skills/
|   |-- sin-tiktok-trend-finder/
|   |-- sin-tiktok-product-research/
|   |-- sin-tiktok-competitor-monitor/
|-- config/
|   |-- simptok.json
|   |-- echotik.json
|-- docs/
    |-- setup.md
    |-- api-reference.md
    |-- free-tier-limits.md
```

## Roadmap

- [x] SimpTok client (Free Tier)
- [x] EchoTik client (Free Tier)
- [x] Scrapling fallback (Open Source)
- [x] Fusion engine (weighted scoring)
- [x] Report generator (JSON/CSV/summary)
- [x] 3 Hermes skills
- [x] CLI interface
- [x] One-command installer
- [ ] Auto-API key rotation (multi-account)
- [ ] Cronjob: Weekly auto-report
- [ ] Email/Slack report delivery
- [ ] Historical trend database
- [ ] Product recommendation engine

## License

MIT License. Scrapling component: BSD 3-Clause (D4Vinci).

## Disclaimer

This bundle uses **free tiers** of third-party services. Limits apply. For production scale, consider upgrading to paid plans or building direct TikTok Shop Partner API integration.

**Not affiliated with** TikTok, SimpTok, EchoTik, or Kalodata.
