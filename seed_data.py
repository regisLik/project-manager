from app import app, db, Project, ProjectVersion
from datetime import datetime, timedelta
import random

def seed_projects():
    with app.app_context():
        print("Seeding database with 10 virtual projects...")
        
        # Clear existing data (optional, comment out if you want to append)
        # db.drop_all()
        # db.create_all()
        
        categories = ['Web', 'Mobile', 'Data Science', 'Infrastructure', 'Security', 'Backend', 'Frontend', 'DevOps']
        phases = ['Intake', 'Planning', 'Development', 'Testing', 'Review', 'Deployment', 'Done']
        statuses = ['Not started', 'In progress', 'En cours', 'Review', 'Done', 'Stopped', 'Gel']
        
        projects_list = [
            ("E-commerce Platform Revamp", "Web", "Refonte complète de la plateforme e-commerce."),
            ("Customer Loyalty App", "Mobile", "Application mobile pour la fidélisation client."),
            ("AI Recommendation Engine", "Data Science", "Moteur de recommandation produit basé sur l'IA."),
            ("Cloud Migration Phase 2", "Infrastructure", "Migration des bases de données vers le cloud."),
            ("Security Audit 2025", "Security", "Audit complet et mise en conformité."),
            ("Internal HR Portal", "Web", "Portail RH pour la gestion des congés et notes de frais."),
            ("API Gateway Implementation", "Backend", "Mise en place d'une API Gateway centralisée."),
            ("Design System V2", "Frontend", "Mise à jour du Design System pour uniformiser les UI."),
            ("CI/CD Pipeline Optimization", "DevOps", "Optimisation des pipelines de déploiement."),
            ("Legacy System Decommissioning", "Infrastructure", "Arrêt et archivage des anciens systèmes.")
        ]

        for i, (name, category, desc) in enumerate(projects_list):
            # Create Project
            project = Project(name=name, category=category)
            db.session.add(project)
            db.session.commit()
            
            # Randomize status and progress
            status = random.choice(statuses)
            phase = random.choice(phases)
            progress = random.randint(0, 100)
            
            if status == 'Done':
                progress = 100
                phase = 'Done'
            elif status == 'Not started':
                progress = 0
                phase = 'Intake'
            
            # Calculate dates
            now = datetime.now().date()
            start_offset = random.randint(-100, -10)
            duration = random.randint(30, 180)
            
            start_date = now + timedelta(days=start_offset)
            deadline = start_date + timedelta(days=duration)
            
            # Create Version
            version = ProjectVersion(
                project_id=project.id,
                version_number=f"V{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(0,9)}",
                phase=phase,
                status=status,
                app_status="Working",
                integration_level="Dev",
                hosting="Cloud",
                accessibility="Online",
                description=desc,
                progress=progress,
                deadline=deadline,
                start_date=start_date,
                duration_days=duration,
                cost=random.randint(5000, 50000),
                cost_type="One-time",
                team_members="Alice, Bob, Charlie, David"
            )
            db.session.add(version)
        
        db.session.commit()
        print("Successfully added 10 virtual projects.")

if __name__ == "__main__":
    seed_projects()
