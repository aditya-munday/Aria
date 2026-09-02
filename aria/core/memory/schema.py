"""SQLite database schema and migrations with explicit eviction bounds."""

SCHEMA_SQL = """
-- Conversations & Turn History (Bounded to rolling 5,000 interactions / 90 days)
CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conv_created_at ON conversation_history(created_at);
CREATE INDEX IF NOT EXISTS idx_conv_session_id ON conversation_history(session_id);

-- User Facts & Extracted Memory (Bounded to 1,000 items with LRU access tracking)
CREATE TABLE IF NOT EXISTS user_facts (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    confidence REAL DEFAULT 1.0,
    access_count INTEGER DEFAULT 1,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facts_last_accessed ON user_facts(last_accessed_at);

-- User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Intent Audit Log
CREATE TABLE IF NOT EXISTS intent_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id TEXT NOT NULL,
    intent_type TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    confirmed_by_user INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_intent_created ON intent_audit_log(created_at);
"""
