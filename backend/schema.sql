-- Suraksha Setu v4 — SQLite schema.
-- PRIVACY: is DB me user ka paste kiya hua text KABHI store nahi hota.
-- Sirf (a) anonymous daily counters, (b) public RSS headlines ka cache,
-- (c) public domains ke RDAP results ka cache rakha jata hai.

CREATE TABLE IF NOT EXISTS daily_counters (
  date         TEXT PRIMARY KEY,          -- IST date, YYYY-MM-DD
  total_scans  INTEGER NOT NULL DEFAULT 0,
  danger_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS alerts_cache (
  source       TEXT NOT NULL,
  title        TEXT NOT NULL,
  link         TEXT NOT NULL,
  published_at TEXT,
  fetched_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feed_status (
  source     TEXT PRIMARY KEY,
  ok         INTEGER NOT NULL DEFAULT 0,
  item_count INTEGER NOT NULL DEFAULT 0,
  fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS rdap_cache (
  domain        TEXT PRIMARY KEY,
  found         INTEGER NOT NULL DEFAULT 0,
  registered_on TEXT,
  fetched_at    TEXT NOT NULL
);
