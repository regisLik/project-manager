from app import app, db, Project, ProjectVersion
from datetime import datetime, timedelta
import random

def seed_projects():
    with app.app_context():
        print("Seeding database with virtual projects...")
        
        # Define some virtual projects
        projects_data = [
            {
                "name": "Refonte Site Web Corporate",
                "category": "Web",
                "version": "V2.0.0",
                "phase": "Validation",
                "status": "Review",
                "progress": 90,
                "deadline_offset": 7, # 7 days from now
                "description": "Refonte complète du site institutionnel avec nouvelle charte graphique.",
                "cost": 15000,
                "start_offset": -30
            },
            {
                "name": "Application Mobile Client",
                "category": "Mobile",
                "version": "V1.0.0",
                "phase": "Development",
                "status": "En cours",
                "progress": 45,
                "deadline_offset": 60,
                "description": "Développement de l'application mobile iOS et Android pour les clients fidèles.",
                "cost": 25000,
                "start_offset": -15
            },
            {
                "name": "Migration Cloud Azure",
                "category": "Infrastructure",
                "version": "V1.1.0",
                "phase": "Testing",
                "status": "Review",
                "progress": 95,
                "deadline_offset": 2,
                "description": "Migration des serveurs on-premise vers Azure.",
                "cost": 5000,
                "start_offset": -45
            },
            {
                "name": "API Gateway Integration",
                "category": "Backend",
                "version": "V1.0.2",
                "phase": "Deployment",
                "status": "Done",
                "progress": 100,
                "deadline_offset": -10, # Past deadline
                "description": "Mise en place d'une passerelle API pour sécuriser les échanges.",
                "cost": 8000,
                "start_offset": -60
            },
            {
                "name": "Dashboard Analytics IA",
                "category": "Data Science",
                "version": "V0.5.0",
                "phase": "Intake",
                "status": "Intake",
                "progress": 10,
                "deadline_offset": 90,
                "description": "Création d'un tableau de bord prédictif basé sur l'IA.",
                "cost": 12000,
                "start_offset": -5
            },
            {
                "name": "Audit Sécurité Q4",
                "category": "Security",
                "version": "V1.0.0",
                "phase": "Audit",
                "status": "Review",
                "progress": 80,
                "deadline_offset": 3,
                "description": "Audit de sécurité trimestriel des infrastructures critiques.",
                "cost": 3000,
                "start_offset": -10
            }
        ]

        for p_data in projects_data:
            # Create Project
            project = Project(name=p_data["name"], category=p_data["category"])
            db.session.add(project)
            db.session.commit()
            
            # Calculate dates
            now = datetime.now().date()
            deadline = now + timedelta(days=p_data["deadline_offset"])
            start_date = now + timedelta(days=p_data["start_offset"])
            
            # Create Version
            version = ProjectVersion(
                project_id=project.id,
                version_number=p_data["version"],
                phase=p_data["phase"],
                status=p_data["status"],
                app_status="Working",
                integration_level="Dev",
                hosting="Cloud",
                accessibility="Online",
                description=p_data["description"],
                progress=p_data["progress"],
                deadline=deadline,
                start_date=start_date,
                duration_days=abs(p_data["deadline_offset"] - p_data["start_offset"]),
                cost=p_data["cost"],
                cost_type="One-time",
                team_members="Alice, Bob, Charlie"
            )
            db.session.add(version)
        
        db.session.commit()
        print("Successfully added 6 virtual projects.")

if __name__ == "__main__":
    seed_projects()
