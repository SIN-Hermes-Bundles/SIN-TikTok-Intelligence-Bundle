---
description: Monitored den Competitor Markt auf TikTok Shop. Wer fuehrt? Wer waechst? Welche Preise? Top Shops, Marktanteile, Pricing.
trigger:
  - monitor competitor
  - wer ist marktfuehrer
  - competitor grid
  - top shops
  - marktanteile
  - wer verkauft am meisten
  - competitor ranking
actions:
  - "Fuehrt `python3 -m src.cli --action competitor-grid --category {category}` aus"
  - "Gibt Top 50 Shops mit Rank, Revenue, Avg Price"
  - "Mit EchoTik + SimpTok Fusion"
examples:
  - query: "wer ist marktfuehrer beauty"
    response: "Top 3: 1. Brand A ($500k) | 2. Brand B ($320k) | 3. Brand C ($210k)"
  - query: "competitor grid"
    response: "Generiere Competitor Grid..."
  - query: "monitor top shops"
    response: "Hole aktuelle Shop-Rankings..."
---

# sin-tiktok-competitor-monitor

Monitored den Competitor-Markt auf TikTok Shop.

## Datenquellen

- **SimpTok**: Competitor grid, shop rank, revenue, avg price
- **EchoTik**: Shop library, best sellers, cross-border sellers
- **Fusion**: Unified ranking, market share estimates

## Nutzung

```bash
# Competitor Grid
python3 -m src.cli --action competitor-grid --category "beauty" --format summary

# JSON Export
python3 -m src.cli --action competitor-grid --format json --output ./reports

# CSV Export
python3 -m src.cli --action competitor-grid --format csv --output ./reports
```

## Output

```json
[
  {
    "name": "Brand A",
    "rank": 1,
    "revenue": 500000,
    "avg_price": 15.99,
    "score": 95,
    "sources": ["echotik", "simptok"]
  }
]
```

## Free Tier Limits

- SimpTok: Competitor grid free (limited exports)
- EchoTik: Shop library free (limited views)
- Kombiniert: Reichweitend genug fuer weekly monitoring
