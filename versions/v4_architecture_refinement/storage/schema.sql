-- storage/schema.sql

-- =========================
-- Price snapshot table
-- =========================
CREATE TABLE IF NOT EXISTS item_price_snapshots (

    market_hash_name TEXT NOT NULL,
    snapshot_time TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Steam
    steam_price NUMERIC(12,2),
    steam_median_price NUMERIC(12,2),
    steam_volume INTEGER,

    -- Buff
    buff_price NUMERIC(12,2),
    buff_median_price NUMERIC(12,2),
    buff_volume INTEGER,

    PRIMARY KEY (market_hash_name, snapshot_time)
);


-- =========================
-- Index for fast latest queries
-- =========================
CREATE INDEX IF NOT EXISTS idx_item_snapshot_time
ON item_price_snapshots (market_hash_name, snapshot_time DESC);



-- =========================
-- Request logs (for scraping monitoring)
-- =========================
CREATE TABLE IF NOT EXISTS request_logs (

    id BIGSERIAL PRIMARY KEY,

    site TEXT,
    status INTEGER,
    latency_ms INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);