---
description: Findet trending Produkte auf TikTok Shop via SimpTok + EchoTik + Scrapling Fusion. Gibt Top 100 Produkte mit Unified Trend Score zurueck.
trigger:
  - finde tiktok trends
  - top produkte tiktok
  - trending tiktok shop
  - welche produkte sind gerade hot
  - suche tiktok trends
  - weekly report tiktok
  - trend finder
  - tiktok intelligence
actions:
  - "Fuehrt `python3 -m src.cli --action weekly-report --category {category} --format summary` aus"
  - "Alternativ: `--action top-products --limit 100`"
  - "Gibt Top 100 Produkte mit Unified Score (0-100)"
  - "Kombiniert SimpTok + EchoTik + Scrapling Daten"
examples:
  - query: "finde tiktok trends beauty"
    response: "Top 10: 1. Lipgloss X (Score: 92) | 2. Face Serum Y (Score: 88)..."
  - query: "weekly report"
    response: "Generiere Weekly Report... Top 100 Produkte, Competitor Grid, Launch Opportunities"
  - query: "welche produkte sind gerade hot"
    response: "Hole aktuelle Trend-Daten..."
---

# sin-tiktok-trend-finder

Findet Trend-Produkte auf TikTok Shop durch Fusion mehrerer Datenquellen.

## Funktionsweise

1. **SimpTok** (Free Tier): Category revenue, top products, competitor grid
2. **EchoTik** (Free Tier): Product library, shop rankings, influencer data
3. **Scrapling** (Open Source): Fallback für TikTok Creative Center / Hashtag Trends

## Fusion Engine

- **SimpTok AI Opportunity Score** (Gewicht: 40%)
- **EchoTik Trend Rank** (Gewicht: 30%)
- **Scrapling Velocity Signal** (Gewicht: 30%)

**Output:** Unified Trend Score (0-100) pro Produkt

## Nutzung

```bash
# Weekly Report
python3 -m src.cli --action weekly-report --category "beauty" --format summary

# Top 100
python3 -m src.cli --action top-products --limit 100 --format json

# Mit Scrapling Fallback
python3 -m src.cli --action weekly-report --use-scrapling
```

## Free Tier Limits

| Tool | Free Tier | Limit | Workaround |
|------|-----------|-------|------------|
| SimpTok | Core metrics | Limited exports | API + local storage |
| EchoTik | $0 plan | 100 views/day | Multi-Account rotation |
| Scrapling | 100% open source | None | Self-hosted |
