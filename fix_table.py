import sqlite3

# Fix the context_request table schema
conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

# Drop and recreate table with correct schema
cursor.execute('DROP TABLE IF EXISTS context_request')
cursor.execute('''
    CREATE TABLE context_request (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER NOT NULL,
        requester VARCHAR(100),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (version_id) REFERENCES project_version(id) ON DELETE CASCADE
    )
''')

conn.commit()
conn.close()
print("Table context_request fixed successfully!")
