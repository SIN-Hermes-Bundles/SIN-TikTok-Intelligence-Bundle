# SIN TikTok Intelligence Bundle — PLAN v2.0

## Ziel
Kostenlose TikTok Shop Intelligence fusioniert aus:
1. **Apify Free Tier** ($5/Monat Guthaben, ~2.500 Produkte)
2. **Scrapeless Free Trial** (TikTok Shop + Social Data)
3. **EchoTik/SimpTok** (Web-Dashboard Cross-Check via Browser)

→ 80% von Kalodata für $0/Monat.

## Architektur v2

```
SIN-TikTok-Intelligence-Bundle/
├── install.sh
├── requirements.txt
├── src/
│   ├── cli.py                          # CLI (7 Aktionen)
│   ├── clients/
│   │   ├── apify_client.py             # Apify TikTok Shop (PRIMARY)
│   │   ├── scrapeless_client.py        # Scrapeless TikTok (SECONDARY)
│   │   ├── echotik_web.py              # EchoTik Web Dashboard
│   │   └── simptok_web.py              # SimpTok Web Dashboard
│   ├── fusion/
│   │   ├── trend_engine.py             # Fusion Engine (Apify + Scrapeless)
│   │   └── report_generator.py         # Report Generator
│   └── __init__.py
├── skills/
│   ├── sin-tiktok-trend-finder/        # "finde tiktok trends"
│   ├── sin-tiktok-product-research/    # "recherchiere produkt"
│   └── sin-tiktok-competitor-monitor/  # "competitor grid"
└── config/
    ├── apify.json                      # APIFY_API_TOKEN
    ├── scrapeless.json                 # SCRAPELESS_API_KEY
    └── echotik.json                    # ECHOTIK_CREDENTIALS
```

## Datenquellen

### 1. Apify (PRIMARY)
- Actor: `pro100chok/tiktok-shop-scraper-usage`
- Features: Search, Categories, Stores, Creators, Reviews
- Kosten: $2/1000 records, $5 free/Monat
- Output: price, sales (soldCount), rating, reviews, store info, creator storefront

### 2. Scrapeless (SECONDARY)
- API: TikTok Scraper API
- Features: Products, Shops, Videos, Hashtags, Live streams
- Kosten: Free trial, limits TBD
- Output: product data, shop data, video analytics, hashtag trends

### 3. EchoTik/SimpTok (CROSS-CHECK)
- Web Dashboard (Browser Automation)
- Features: Category revenue, competitor grid, influencer data
- Kosten: Free (manual web access)
- Output: TBD (scraped from web)

## Fusion Engine v2

```
Weighted Scoring:
├── Apify Product Data (Gewicht: 50%)
│   ├── soldCount (Sales Velocity)
│   ├── rating (Product Quality)
│   └── reviewCount (Market Validation)
├── Scrapeless Trends (Gewicht: 30%)
│   ├── hashtag velocity
│   └── video engagement
└── Cross-Check Match (Gewicht: 20%)
    ├── EchoTik product exists? (Confidence +)
    └── SimpTok competitor data (Market validation)
```

## Free Tier Limits & Strategy

| Quelle | Free Limit | Pro Woche | Strategie |
|--------|-----------|-----------|-----------|
| Apify | $5/Monat | ~600 Produkte/Woche | 1x wöchentlich Top 100 |
| Scrapeless | Free Trial | TBD | Testen, dann entscheiden |
| EchoTik | $0/Monat | Manuell | Browser cross-check |
| SimpTok | $0/Monat | Manuell | Browser cross-check |

## Implementation Plan

Phase 1: Apify Client (HEUTE)
- [x] Apify Client mit PRO100CHOK Actor
- [x] Search, Categories, Products
- [x] JSON/CSV Export
- [x] CLI Interface

Phase 2: Scrapeless Client (HEUTE)
- [ ] Scrapeless API integration
- [ ] TikTok Shop endpoints
- [ ] Hashtag/Video data

Phase 3: Fusion Engine (HEUTE)
- [ ] Weighted Scoring
- [ ] Product Matching
- [ ] Report Generator

Phase 4: Skills (HEUTE)
- [ ] Hermes Skills updaten
- [ ] Installer updaten
- [ ] README updaten

## Kalodata Feature-Abdeckung

| Kalodata | Apify | Scrapeless | EchoTik | Abgedeckt? |
|----------|-------|-----------|---------|-----------|
| Produkt-Trends | ✅ | ✅ | ✅ | 100% |
| Preise & Sales | ✅ | ✅ | ⚠️ | 90% |
| Shop Rankings | ✅ | ✅ | ✅ | 100% |
| Creator Data | ✅ | ⚠️ | ✅ | 85% |
| Reviews | ✅ | ✅ | ❌ | 95% |
| Kategorie-Analyse | ✅ | ✅ | ✅ | 100% |
| Video Analytics | ❌ | ✅ | ❌ | 50% |
| Live Stream | ❌ | ✅ | ❌ | 50% |
| Hashtag Trends | ❌ | ✅ | ❌ | 50% |
| Dashboard UI | ❌ | ❌ | ✅ | 30% |
| Historische Daten | ❌ | ❌ | ❌ | 0% |
| **GESAMT** | | | | **~80%** |
