from sqlalchemy import create_engine, text
import os

# Absolute path to the database
DB_PATH = os.path.join(os.getcwd(), 'instance', 'projects.db')
print(f"Database path: {DB_PATH}")

def add_column():
    engine = create_engine(f'sqlite:///{DB_PATH}')
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(context_request)"))
            columns = [row.name for row in result]
            
            if 'created_at' not in columns:
                print("Adding created_at column...")
                conn.execute(text("ALTER TABLE context_request ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                print("Column added successfully!")
            else:
                print("Column created_at already exists.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
