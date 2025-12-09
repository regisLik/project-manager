"""
Script simple pour créer la DB et ajouter des données de test minimales
"""

from app import app, db, Project, ProjectVersion, ContextRequest
from datetime import datetime, date, timedelta

with app.app_context():
    print("\n🔄 Création de la base de données...")
    db.create_all()
    print("✅ Tables créées\n")
    
    print("📝 Ajout de données de test...")
    
    # Créer un projet
    project = Project(name="Projet Test", category="Web")
    db.session.add(project)
    db.session.flush()
    
    # Créer une version
    version = ProjectVersion(
        project_id=project.id,
        version_number="1.0.0",
        phase="Development",
        status="In Progress",
        start_date=date.today(),
        duration_days=30,
        progress=50,
        description="Version de test"
    )
    db.session.add(version)
    db.session.flush()
    
    # Créer des demandes AVEC le champ approved
    requests = [
        ContextRequest(
            version_id=version.id,
            requester="Alice Martin",
            requester_role="Client",
            description="Ajouter une fonctionnalité de recherche",
            user_request_type="Ajout",
            difficulty_level="Medium",
            priority_level="High",
            approved="Approuvé"  # ← Champ approved
        ),
        ContextRequest(
            version_id=version.id,
            requester="Bob Durand",
            requester_role="Manager",
            description="Correction du bug d'affichage",
            user_request_type="Modification",
            difficulty_level="Easy",
            priority_level="Urgent",
            approved="En attente"  # ← Champ approved
        ),
        ContextRequest(
            version_id=version.id,
            requester="Claire Dubois",
            requester_role="Developer",
            description="Refactorisation du code backend",
            tech_request_type="Refactorisation",
            difficulty_level="Hard",
            priority_level="Low",
            approved="Rejeté"  # ← Champ approved
        )
    ]
    
    for req in requests:
        db.session.add(req)
    
    db.session.commit()
    
    print("✅ Données de test ajoutées !")
    print(f"\n📊 Résumé:")
    print(f"   - 1 projet créé")
    print(f"   - 1 version créée")
    print(f"   - 3 demandes créées (dont 1 approuvée, 1 en attente, 1 rejetée)")
    print("\n💡 Lancez maintenant: python app.py\n")
