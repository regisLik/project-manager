from app import app, db
from sqlalchemy import text

def migrate():
    print("Starting migration...")
    with app.app_context():
        # Create new tables (Document)
        db.create_all()
        print("Created new tables (if any).")

        # Update existing tables
        with db.engine.connect() as conn:
            # Check/Add request_description
            try:
                conn.execute(text("ALTER TABLE project_version ADD COLUMN request_description TEXT"))
                print("Added column: request_description")
            except Exception as e:
                print(f"Skipped request_description (might exist): {e}")

            # Check/Add requester
            try:
                conn.execute(text("ALTER TABLE project_version ADD COLUMN requester VARCHAR(100)"))
                print("Added column: requester")
            except Exception as e:
                print(f"Skipped requester (might exist): {e}")
                
            conn.commit()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
