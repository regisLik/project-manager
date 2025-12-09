import sqlite3

# Remove created_at column by recreating the table
conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

print("Recreating context_request table without created_at column...")

# Get existing data
cursor.execute("SELECT id, version_id, requester, description, requester_role, user_request_type, tech_request_type, planned_improvement, improvement_type, difficulty_level, priority_level FROM context_request")
existing_data = cursor.fetchall()
print(f"Found {len(existing_data)} existing records")

# Drop old table
cursor.execute("DROP TABLE context_request")
print("Dropped old table")

# Create new table without created_at
cursor.execute('''
    CREATE TABLE context_request (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER NOT NULL,
        requester VARCHAR(100),
        description TEXT,
        requester_role VARCHAR(50),
        user_request_type VARCHAR(200),
        tech_request_type VARCHAR(200),
        planned_improvement VARCHAR(20) DEFAULT 'Not decided',
        improvement_type VARCHAR(20) DEFAULT 'Not decided',
        difficulty_level VARCHAR(20) DEFAULT 'Not decided',
        priority_level VARCHAR(20) DEFAULT 'Medium',
        FOREIGN KEY (version_id) REFERENCES project_version(id) ON DELETE CASCADE
    )
''')
print("Created new table")

# Restore data
for row in existing_data:
    cursor.execute('''
        INSERT INTO context_request 
        (id, version_id, requester, description, requester_role, user_request_type, tech_request_type, planned_improvement, improvement_type, difficulty_level, priority_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)

print(f"Restored {len(existing_data)} records")

conn.commit()

# Verify
cursor.execute("PRAGMA table_info(context_request)")
columns = cursor.fetchall()
print("\nFinal table structure:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\n✅ Table recreated successfully!")
