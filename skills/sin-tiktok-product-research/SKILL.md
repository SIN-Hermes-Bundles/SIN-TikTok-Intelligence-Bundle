---
description: Recherchiert detaillierte Produkt-Daten auf TikTok Shop. Preis, Revenue, Wachstum, Competitor, Creator. Nutzt EchoTik + SimpTok.
trigger:
  - recherchiere produkt
  - analysiere produkt
  - tiktok produkt daten
  - produkt detail
  - welche preise
  - wie verkauft sich
  - competitor check
actions:
  - "Fuehrt `python3 -m src.cli --action product-detail --product-id {id}` aus"
  - "Oder: `--action competitor-grid --category {category}`"
  - "Gibt Preis, Revenue, Wachstum, Top Competitor"
examples:
  - query: "recherchiere Produkt XYZ"
    response: "Produkt: XYZ | Preis: $12.99 | Revenue: $45k | Wachstum: +23%..."
  - query: "competitor check beauty"
    response: "Top 5 Competitor: 1. Brand A ($120k) | 2. Brand B ($98k)..."
  - query: "analysiere tiktok produkt"
    response: "Hole detaillierte Produkt-Analyse..."
---

# sin-tiktok-product-research

Detaillierte Produkt-Recherche auf TikTok Shop.

## Datenquellen

- **EchoTik**: Produkt-Detail, Preis, Sales, Rank
- **SimpTok**: Revenue, Growth, AI Opportunity Score
- **Scrapling**: Hashtag-Trends, Video-Daten (Fallback)

## Nutzung

```bash
# Produkt Detail
python3 -m src.cli --action product-detail --product-id "12345" --format json

# Competitor Grid
python3 -m src.cli --action competitor-grid --category "beauty" --format summary

# Kombiniert
python3 -m src.cli --action weekly-report --category "beauty" --format json
```

## Output

```json
{
  "title": "Product Name",
  "price": 12.99,
  "revenue": 45000,
  "growth": 0.23,
  "competitor_rank": 3,
  "creator_matches": [...],
  "unified_score": 87
}
```
