from app import app, db, Project, ProjectVersion, ContextRequest
from datetime import datetime, timedelta, date

with app.app_context():
    print("Creating seed data...")
    
    # Projet 1 avec plusieurs versions
    project1 = Project(name="Application E-Commerce", category="Web")
    db.session.add(project1)
    db.session.flush()
    
    # Version 1.0.0
    v1 = ProjectVersion(
        project_id=project1.id,
        version_number="1.0.0",
        created_at=datetime.now() - timedelta(days=150),
        phase="Production",
        status="Done",
        description="Version initiale avec catalogue produits et authentification",
        start_date=date.today() - timedelta(days=180),
        duration_days=30,
        progress=100
    )
    db.session.add(v1)
    db.session.flush()
    
    # Version 1.1.0
    v2 = ProjectVersion(
        project_id=project1.id,
        version_number="1.1.0",
        parent_id=v1.id,
        created_at=datetime.now() - timedelta(days=120),
        phase="Production",
        status="Done",
        description="Ajout du panier et système de paiement Stripe",
        start_date=date.today() - timedelta(days=150),
        duration_days=25,
        progress=100
    )
    db.session.add(v2)
    db.session.flush()
    
    # Version 1.2.0
    v3 = ProjectVersion(
        project_id=project1.id,
        version_number="1.2.0",
        parent_id=v2.id,
        created_at=datetime.now() - timedelta(days=80),
        phase="Production",
        status="Done",
        description="Gestion des stocks en temps réel avec alertes",
        start_date=date.today() - timedelta(days=120),
        duration_days=20,
        progress=100
    )
    db.session.add(v3)
    db.session.flush()
    
    # Version 2.0.0 - version actuelle en développement
    v4 = ProjectVersion(
        project_id=project1.id,
        version_number="2.0.0",
        parent_id=v3.id,
        created_at=datetime.now() - timedelta(days=30),
        phase="Development",
        status="In Progress",
        description="Refonte UI/UX avec système de recommandations et programme fidélité",
        start_date=date.today() - timedelta(days=60),
        duration_days=90,
        progress=50,
        deadline=date.today() + timedelta(days=30)
    )
    db.session.add(v4)
    db.session.flush()
    
    # Ajouter des context requests pour tester le tableau
    cr1 = ContextRequest(
        version_id=v4.id,
        requester="Marie Dubois",
        requester_role="Client",
        description="Les clients veulent une wishlist pour sauvegarder leurs produits favoris",
        user_request_type="Ajout",
        tech_request_type="",
        planned_improvement="Yes",
        improvement_type="Minor",
        difficulty_level="Easy",
        priority_level="Medium"
    )
    db.session.add(cr1)
    
    cr2 = ContextRequest(
        version_id=v4.id,
        requester="Jean Martin",
        requester_role="Manager",
        description="Optimisation des performances de la page d'accueil (temps de chargement > 3s)",
        user_request_type="",
        tech_request_type="Optimization,Refactorisation",
        planned_improvement="Yes",
        improvement_type="Patch",
        difficulty_level="Medium",
        priority_level="High"
    )
    db.session.add(cr2)
    
    cr3 = ContextRequest(
        version_id=v4.id,
        requester="Sophie Lambert",
        requester_role="Product Owner",
        description="Intégration d'un chat en temps réel pour le support client",
        user_request_type="Ajout",
        tech_request_type="Migration",
        planned_improvement="Not decided",
        improvement_type="Minor",
        difficulty_level="Hard",
        priority_level="Low"
    )
    db.session.add(cr3)
    
    cr4 = ContextRequest(
        version_id=v4.id,
        requester="Pierre Rousseau",
        requester_role="Developer",
        description="Migration de jQuery vers React pour améliorer la maintenabilité",
        user_request_type="",
        tech_request_type="Migration,Refactorisation",
        planned_improvement="Yes",
        improvement_type="Major",
        difficulty_level="Hard",
        priority_level="Medium"
    )
    db.session.add(cr4)
    
    # Projet 2
    project2 = Project(name="App Mobile Fitness", category="Mobile")
    db.session.add(project2)
    db.session.flush()
    
    v5 = ProjectVersion(
        project_id=project2.id,
        version_number="0.1.0",
        created_at=datetime.now() - timedelta(days=60),
        phase="Planning",
        status="In Progress",
        description="Prototype initial avec tracking d'activités sportives",
        start_date=date.today() - timedelta(days=90),
        duration_days=60,
        progress=30
    )
    db.session.add(v5)
    
    db.session.commit()
    
    print(f"\n✅ Seed data created!")
    print(f"   - {project1.name}: 4 versions (1.0.0 → 2.0.0)")
    print(f"   - Version 2.0.0 has 4 context requests for testing")
    print(f"   - {project2.name}: 1 version (0.1.0)")
