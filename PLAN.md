# SIN-TikTok-Intelligence-Bundle — Plan

## Ziel
Kostenlose TikTok Shop Intelligence als Hermes Bundle. Fusioniert SimpTok (Free Tier), EchoTik (Free Tier) und Scrapling (Open Source) zu einem autonomen Trend-Monitoring System.

## Architektur

```
SIN-TikTok-Intelligence-Bundle/
|-- install.sh                          # One-Command Installer
|-- src/
|   |-- cli.py                          # CLI Eingang
|   |-- clients/
|   |   |-- simptok_client.py           # SimpTok API Client (Free Tier)
|   |   |-- echotik_client.py           # EchoTik API Client (Free Tier)
|   |   |-- scrapling_fallback.py       # Scrapling Fallback Scraper
|   |-- fusion/
|   |   |-- trend_engine.py             # Trend-Score Fusion (SimpTok + EchoTik)
|   |   |-- report_generator.py         # Weekly Report (Top 100, Creator, etc)
|   |-- utils/
|   |   |-- config_loader.py            # Config management
|   |   |-- rate_limiter.py             # Multi-Account Round-Robin
|-- skills/
|   |-- sin-tiktok-trend-finder/        # Hermes Skill: Trend-Produkte finden
|   |-- sin-tiktok-product-research/   # Hermes Skill: Produkt-Research
|   |-- sin-tiktok-competitor-monitor/  # Hermes Skill: Competitor Monitor
|-- config/
|   |-- simptok.json                    # SimpTok API Credentials
|   |-- echotik.json                    # EchoTik API Credentials
|   |-- proxies.json                    # Proxy Config (optional)
|-- docs/
    |-- setup.md
    |-- api-reference.md
    |-- free-tier-limits.md             # Honest limits documentation

## Komponenten

### 1. SimpTok Client (Free Tier)
- Endpoint: simptok.com API (light API)
- Features: Category revenue, competitor grid, top products (hourly), launch tracker
- Limits: TBD (Free tier caps)

### 2. EchoTik Client (Free Tier)
- Endpoint: echotik.live API (Data API)
- Features: Product library, influencer data, live monitor, shop analytics
- Limits: Limited daily views, basic filters only

### 3. Scrapling Fallback (Open Source)
- Tool: github.com/D4Vinci/Scrapling
- License: BSD 3-Clause
- Features: Stealth mode, Cloudflare bypass, adaptive selectors
- Use: Fallback when APIs are rate-limited or data is missing

## Fusion Engine

```
Input: SimpTok Data + EchoTik Data + Scrapling Data
    |
    v
Trend Engine (Weighted Scoring)
    - SimpTok AI Opportunity Score (weight: 0.4)
    - EchoTik Trend Rank (weight: 0.3)
    - Scrapling Velocity Signal (weight: 0.3)
    |
    v
Output: Unified Trend Score (0-100)
    |
    v
Report Generator
    - Top 100 Products (weekly)
    - Category Rankings
    - Competitor Grid
    - Influencer/Creator Matches
    - Launch Opportunities
```

## Free Tier Strategy

| Tool | Free Tier | Limitation | Workaround |
|------|-----------|------------|------------|
| SimpTok | Core metrics free | Limited exports | API + local storage |
| EchoTik | $0 plan | Limited daily views | Multi-Account rotation |
| Scrapling | 100% open source | None | Self-hosted |

## Skills

### sin-tiktok-trend-finder
Trigger: "finde tiktok trends", "top produkte tiktok", "trending tiktok shop"
Output: JSON list of top products with unified trend score

### sin-tiktok-product-research
Trigger: "recherchiere produkt", "analysiere produkt", "tiktok produkt daten"
Output: Detailed product analysis (price, sales, competitors, creators)

### sin-tiktok-competitor-monitor
Trigger: "monitor competitor", "wer ist marktfuehrer", "competitor grid"
Output: Competitor ranking, market share, pricing

## Roadmap
- [x] Plan
- [ ] Repo anlegen
- [ ] Clients bauen (SimpTok, EchoTik, Scrapling)
- [ ] Fusion Engine
- [ ] Report Generator
- [ ] 3 Hermes Skills
- [ ] Installer
- [ ] README + Docs
- [ ] Release v1.0.0
