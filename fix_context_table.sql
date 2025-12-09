-- Fix context_request table schema
-- Drop existing table and recreate with correct schema

DROP TABLE IF EXISTS context_request;

CREATE TABLE context_request (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    requester VARCHAR(100),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES project_version(id) ON DELETE CASCADE
);
