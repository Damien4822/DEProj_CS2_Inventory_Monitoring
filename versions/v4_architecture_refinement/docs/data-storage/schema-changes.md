# Schema Evolution (V3 → V4)
## Overview

V4 introduces a new relational database schema that improves how market data is organized and stored.

The main goal of the redesign is to separate inventory items, marketplaces, and price data into individual tables. This makes the database easier to maintain and simplifies adding support for new marketplaces in the future.

---

# Previous Schema (V3)

## Overview

The V3 implementation stored market data using a denormalized snapshot table.

Each record represented the state of an inventory item at a specific point in time, with measurements from each marketplace stored as dedicated columns.

### Example Structure

```text
item_price_snapshots

- market_hash_name
- snapshot_time

- steam_price
- steam_median_price
- steam_volume

- buff_price
- buff_median_price
- buff_volume
```

### Example Data

| Item | Time | Steam Price | BUFF Price |
|------|------|------------:|-----------:|
| AK-47 Redline | 10:00 | 15.00 | 14.50 |
| AK-47 Redline | 11:00 | 15.20 | 14.70 |
This approach worked well when only a few marketplaces were supported.

---
# Why Change the Schema?
As the project evolved, several limitations became apparent.
## Adding New Marketplaces

Every new marketplace required adding another set of columns to the table.

For example, supporting a new marketplace would require adding columns such as:

```text
csfloat_price
csfloat_median_price
csfloat_volume
```

This meant changing both the database schema and the application code every time a new marketplace was introduced.

---

## Large Snapshot Table

Since every marketplace stored its own columns, the table became wider as more marketplaces were added.

This made the schema harder to read and maintain.

---

## Limited Flexibility

The table was designed specifically for price information.

If future versions needed to store other kinds of market data, such as demand, listings, or sales history, even more columns would have been required.


---

# New Schema (V4)

V4 separates the data into three related tables.

## Entity Relationship

```text
Inventory Item
       │
       │
Price Snapshot
       │
       │
Market Source
```

---

## Main Entities

### Inventory Item

Stores information about each monitored item.

```text
inventory_items

- item_id
- market_hash_name
```

---

### Market Source

Stores information about each supported marketplace.

```text
market_sources

- market_id
- market_name
```

Example values:

- Steam
- BUFF163

---

### Price Snapshot

Stores one price observation collected from one marketplace at a specific time.

```text
price_snapshots

- snapshot_id
- item_id
- market_id
- price
- median_price
- volume
- snapshot_time
```

### Example Data

| Item | Market | Price | Time |
|------|--------|------:|------:|
| AK-47 Redline | Steam | 15.00 | 10:00 |
| AK-47 Redline | BUFF163 | 14.50 | 10:00 |
| AK-47 Redline | Steam | 15.20 | 11:00 |
| AK-47 Redline | BUFF163 | 14.70 | 11:00 |

Each market observation is represented as an independent record associated with both an inventory item and a marketplace.

---

# Comparison

| Aspect | V3 | V4 |
|---------|----|----|
| Schema design | Denormalized | Normalized |
| Marketplace representation | Dedicated columns | Separate entity |
| Marketplace expansion | Schema modification required | Data insertion only |
| Historical observations | Supported | Supported |
| Future extensibility | Limited | Improved |

---

# Benefits

The new schema provides several improvements.

- Better organization of market data.
- Easier support for additional marketplaces.
- Less duplicated information.
- Simpler database maintenance.
- Better support for future features.

---

# Future Considerations

The current schema stores price information only.

Future versions may introduce additional tables for other types of market data, such as:

- Demand
- Active listings
- Transaction history

These tables can reuse the existing `inventory_items` and `market_sources` tables without changing the current schema.


Potential extensions include:

```text
Inventory Item
    │
    ├── Price Snapshot
    ├── Demand Snapshot
    ├── Listing Snapshot
    └── Transaction History
```

These additional observation types can be introduced as independent fact tables while continuing to reference the existing inventory and marketplace entities.

---

# Summary

The V4 redesign replaces the denormalized marketplace-specific schema used in V3 with a normalized relational model.

By separating inventory items, marketplaces, and market observations into independent entities, the new schema improves maintainability, simplifies future expansion, and provides a stronger foundation for historical analysis and continued development.