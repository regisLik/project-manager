import sqlite3

# Check and fix context_request table
conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

# Get current table structure
cursor.execute("PRAGMA table_info(context_request)")
columns = cursor.fetchall()

print("Current columns in context_request table:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Check if we need to add columns
existing_columns = [col[1] for col in columns]
needed_columns = {
    'requester_role': 'VARCHAR(50)',
    'user_request_type': 'VARCHAR(200)',
    'tech_request_type': 'VARCHAR(200)',
    'planned_improvement': 'VARCHAR(20) DEFAULT "Not decided"',
    'improvement_type': 'VARCHAR(20) DEFAULT "Not decided"',
    'difficulty_level': 'VARCHAR(20) DEFAULT "Not decided"',
    'priority_level': 'VARCHAR(20) DEFAULT "Medium"'
}

print("\nAdding missing columns...")
for col_name, col_type in needed_columns.items():
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE context_request ADD COLUMN {col_name} {col_type}')
            print(f"✓ Added {col_name}")
        except sqlite3.OperationalError as e:
            print(f"✗ {col_name}: {e}")
    else:
        print(f"- {col_name} already exists")

conn.commit()

# Verify final structure
cursor.execute("PRAGMA table_info(context_request)")
final_columns = cursor.fetchall()
print("\nFinal table structure:")
for col in final_columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\n✅ Migration verification complete!")
