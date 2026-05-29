---
description: Findet trending TikTok Shop Produkte via Apify + Scrapeless. Top 100 Produkte mit Unified Trend Score, Preisen, Sales, Ratings. KEIN Login, KEINE Cookies, KOSTENLOS.
trigger:
  - finde tiktok trends
  - top produkte tiktok
  - trending tiktok shop
  - welche produkte hot
  - weekly report tiktok
  - apify search
actions:
  - "python3 -m src.cli --action weekly-report --keyword {keyword}"
  - "python3 -m src.cli --action top-products --keyword {keyword} --limit 100"
examples:
  - query: "finde tiktok trends skincare"
    response: "Top 10 skincare products: Score, Price, Sales, Rating..."
  - query: "weekly report beauty"
    response: "Generiere Weekly Report..."
---

# sin-tiktok-trend-finder

Findet TikTok Shop Trending-Produkte via Apify Free Tier + Scrapeless.

## Quellen

| Quelle | Typ | Kosten |
|--------|-----|--------|
| Apify | PRIMARY | $5/Monat free |
| Scrapeless | SECONDARY | Free trial |

## Nutzung

```bash
# Top Produkte
python3 -m src.cli --action top-products --keyword "skincare" --limit 100

# Weekly Report
python3 -m src.cli --action weekly-report --keyword "beauty" --format summary
```

## Output

- Unified Score (0-100)
- Price, Sales, Rating, Reviews
- Store Name, Product URL
