-- One row per MCP tool call. No IP addresses, user agents or request contents.
CREATE TABLE IF NOT EXISTS usage_events (
	id INTEGER PRIMARY KEY,
	ts TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
	tool TEXT NOT NULL,
	skill TEXT
);
CREATE INDEX IF NOT EXISTS usage_events_ts ON usage_events (ts);
