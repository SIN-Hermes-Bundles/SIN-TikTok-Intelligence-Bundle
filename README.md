# SIN-TikTok-Intelligence-Bundle v2

**Kostenlose TikTok Shop Intelligence. ~80% von Kalodata für $0/Monat.**

Fusioniert **Apify** (Free Tier, $5/Monat Guthaben) + **Scrapeless** (Free Trial) zu einem Hermes-native Trend-Monitoring System.

> **KEIN TikTok Login. KEINE Cookies. KEIN Account-Risiko.**

## Was es kann

| Feature | Apify | Scrapeless | Kalodata-Abdeckung |
|---------|-------|-----------|-------------------|
| Produkt-Trends | ✅ | ✅ | 100% |
| Preise & Sales | ✅ | ✅ | 90% |
| Shop Rankings | ✅ | ✅ | 100% |
| Creator Data | ✅ | ⚠️ | 85% |
| Reviews | ✅ | ✅ | 95% |
| Video Analytics | ❌ | ✅ | 50% |
| Live Stream | ❌ | ✅ | 50% |
| Hashtag Trends | ❌ | ✅ | 50% |
| Gesamt | | | **~80%** |

## Quick Start

```bash
# 1. Installieren
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-TikTok-Intelligence-Bundle/main/install.sh | bash

# 2. Apify API Token holen (30 Sekunden, kostenlos)
#    → apify.com/signup → Settings → API Token
#    → Speichern in ~/.hermes/bundles/tiktok-intelligence/config/apify.json

# 3. Trend-Report generieren
cd ~/.hermes/bundles/tiktok-intelligence
python3 -m src.cli --action top-products --keyword "skincare" --limit 50 --format summary
```

## Architektur

```
Apify (PRIMARY)           Scrapeless (SECONDARY)
$5/Monat free             Free Trial
├── Product Search        ├── Video Analytics
├── Categories            ├── Hashtag Trends
├── Stores                ├── Live Streams
├── Creators              └── Creator Profiles
└── Reviews
        │                          │
        └──────────┬───────────────┘
                   │
          Fusion Engine v2
     (Weighted: Apify 50% + Scrapeless 30% + Cross-Check 20%)
                   │
          Unified Trend Score (0-100)
                   │
          Weekly Report + CSV/JSON Export
```

## CLI

```bash
# Top 100 Produkte
python3 -m src.cli --action top-products --keyword "phone case" --limit 100

# Kategorie-Analyse
python3 -m src.cli --action category --category "beauty" --limit 100

# Store-Produkte
python3 -m src.cli --action store --store "TikTokShop"

# Creator Produkte
python3 -m src.cli --action creator --creator "influencer_name"

# Reviews
python3 -m src.cli --action reviews --url "https://shop.tiktok.com/..." --limit 50

# Weekly Report (alle Quellen)
python3 -m src.cli --action weekly-report --keyword "trending" --format summary

# Mit Scrapeless
python3 -m src.cli --action weekly-report --keyword "skincare" --use-scrapeless
```

## Hermes Skills

- **"finde tiktok trends"** → Top 100 Trending Produkte
- **"recherchiere produkt"** → Detaillierte Produkt-Analyse
- **"competitor grid"** → Shop Rankings & Competitor

## Kosten

| Quelle | Free Tier | Reicht für |
|--------|-----------|-----------|
| Apify | $5/Monat | ~2.500 Produkte/Monat |
| Scrapeless | Free Trial | Limits TBD |
| **Total** | **$0** | **Weekly Top 100** |

## Lizenz

MIT. Powered by [Apify](https://apify.com) und [Scrapeless](https://scrapeless.com).

## Disclaimer

Nicht affiliiert mit TikTok, Apify, Scrapeless, Kalodata oder SimpTok.
Free Tier Limits können sich ändern.
