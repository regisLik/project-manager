from app import app, db

# Recreate database with correct schema
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables with new schema...")
    db.create_all()
    
    print("\n✅ Database recreated successfully!")
    print("All tables now have the correct schema including new ContextRequest fields.")
