from app import app, db, ProjectVersion, ContextRequest

def migrate():
    with app.app_context():
        # Create the new table
        db.create_all()
        print("Created context_request table")
        
        # Migrate existing data
        versions = ProjectVersion.query.filter(
            (ProjectVersion.requester.isnot(None)) | 
            (ProjectVersion.request_description.isnot(None))
        ).all()
        
        migrated = 0
        for version in versions:
            if version.requester or version.request_description:
                # Check if already migrated
                existing = ContextRequest.query.filter_by(version_id=version.id).first()
                if not existing:
                    request = ContextRequest(
                        version_id=version.id,
                        requester=version.requester or '',
                        description=version.request_description or ''
                    )
                    db.session.add(request)
                    migrated += 1
        
        db.session.commit()
        print(f"Migrated {migrated} existing context requests")
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()

