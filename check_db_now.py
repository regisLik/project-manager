import sqlite3
import os

# Check current directory
print(f"Current directory: {os.getcwd()}")
print(f"Database file exists: {os.path.exists('projects.db')}")
print(f"Database file path: {os.path.abspath('projects.db')}")

# Connect and check
conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

# Get table structure
cursor.execute("PRAGMA table_info(context_request)")
columns = cursor.fetchall()

print("\nActual table structure in projects.db:")
for col in columns:
    print(f"  {col[1]:25} {col[2]}")

# Count records
cursor.execute("SELECT COUNT(*) FROM context_request")
count = cursor.fetchone()[0]
print(f"\nNumber of records: {count}")

conn.close()
