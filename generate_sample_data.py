"""
Script de génération de données synthétiques pour ProjTrack
Utilise Faker pour créer des données réalistes
"""

from app import app, db, Project, ProjectVersion, ContextRequest
from datetime import datetime, timedelta, date
import random

try:
    from faker import Faker
    fake = Faker('fr_FR')  # Français
except ImportError:
    print("⚠️  Installation de Faker requise...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'faker'])
    from faker import Faker
    fake = Faker('fr_FR')

# Configuration
NUM_PROJECTS = 8
MAX_VERSIONS_PER_PROJECT = 5
MAX_REQUESTS_PER_VERSION = 6

# Listes pour génération réaliste
CATEGORIES = ['Web', 'Mobile', 'Desktop', 'API', 'Data']
PHASES = ['Intake', 'Qualification', 'Planning', 'Build', 'Test & QA', 'Staging', 'Release']
STATUSES = ['Not started', 'In progress', 'Review', 'Done', 'Gel', 'Stopped']
APP_STATUSES = ['Working', 'Partially Working', 'Not Working', 'Under Maintenance']
HOSTING = ['Cloud','Services']
ACCESSIBILITY = ['Online', 'Offline']

ROLES = ['Client', 'Manager', 'Developer', 'Product Owner', 'Designer', 'Tester']
USER_REQUEST_TYPES = ['Ajout', 'Modification', 'Suppression']
TECH_REQUEST_TYPES = ['Refactorisation', 'Migration', 'Optimization']
PLANNED_IMPROVEMENTS = ['Yes', 'No', 'Not decided']
IMPROVEMENT_TYPES = ['Patch', 'Minor', 'Major', 'Not decided']
DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard', 'Not decided']
PRIORITY_LEVELS = ['Low', 'Medium', 'High', 'Urgent']

def generate_version_number(version_count, improvement_type='Minor'):
    """Génère un numéro de version réaliste"""
    if version_count == 0:
        return "1.0.0"
    
    # Parse previous version or start fresh
    versions = [
        "1.0.0", "1.1.0", "1.2.0", "2.0.0", "2.1.0",
        "2.2.0", "3.0.0", "3.1.0", "3.2.0", "3.3.0"
    ]
    
    if version_count < len(versions):
        return versions[version_count]
    
    return f"{version_count // 3}.{version_count % 3}.0"

def generate_project_description(category):
    """Génère une description de projet basée sur la catégorie"""
    descriptions = {
        'Web': [
            "Plateforme de gestion collaborative pour équipes distribuées",
            "Marketplace e-commerce avec paiement intégré",
            "Système de réservation en ligne multi-services",
            "Dashboard analytics en temps réel",
            "Portail client self-service"
        ],
        'Mobile': [
            "Application de suivi de fitness et nutrition",
            "App de livraison à la demande",
            "Réseau social professionnel mobile",
            "Application de gestion de tâches avec synchronisation cloud",
            "App de scanner de documents avec OCR"
        ],
        'Desktop': [
            "Logiciel de comptabilité pour PME",
            "Outil de design graphique avancé",
            "IDE pour développement spécialisé",
            "Suite bureautique collaborative",
            "Application de montage vidéo professionnelle"
        ],
        'API': [
            "API REST pour intégration de paiements",
            "Service d'authentification OAuth2",
            "API de géolocalisation et cartographie",
            "Service de notification multi-canal",
            "API de traduction automatique"
        ],
        'Data': [
            "Pipeline ETL pour data warehouse",
            "Système de recommandation basé ML",
            "Plateforme d'analyse prédictive",
            "Dashboard BI avec connexions multiples",
            "Outil d'extraction et visualisation de données"
        ]
    }
    
    return random.choice(descriptions.get(category, ["Projet innovant"]))

def generate_version_description(phase, version_number):
    """Génère une description de version"""
    descriptions = [
        f"Version {version_number} - Amélioration de l'interface utilisateur et corrections de bugs",
        f"Version {version_number} - Optimisation des performances et nouvelles fonctionnalités",
        f"Version {version_number} - Refonte du système d'authentification",
        f"Version {version_number} - Ajout de fonctionnalités demandées par les utilisateurs",
        f"Version {version_number} - Migration vers nouvelle architecture",
        f"Version {version_number} - Améliorations de sécurité et stabilité",
    ]
    return random.choice(descriptions)

def generate_request_description():
    """Génère une description de demande réaliste"""
    descriptions = [
        "Les utilisateurs demandent une fonctionnalité de recherche avancée avec filtres multiples",
        "Besoin d'export des données en format Excel et PDF",
        "Amélioration de l'ergonomie du formulaire de saisie (trop de clics)",
        "Intégration avec services tiers (Slack, Teams, etc.)",
        "Optimisation du temps de chargement des pages (actuellement > 3s)",
        "Ajout d'un système de notifications push en temps réel",
        "Support du mode sombre pour réduire la fatigue visuelle",
        "Traduction de l'interface en plusieurs langues (EN, ES, DE)",
        "Amélioration du système de recherche (résultats non pertinents)",
        "Ajout de graphiques et statistiques dans le dashboard",
        "Correction du bug d'affichage sur mobile (responsiveness)",
        "Mise en place d'un système de cache pour améliorer les performances",
        "Refactorisation du code legacy pour faciliter la maintenance",
        "Migration de la base de données vers PostgreSQL",
        "Implémentation d'un système de logs structurés",
        "Ajout de tests automatisés (unitaires et e2e)",
    ]
    return random.choice(descriptions)

def clear_database():
    """Vide la base de données et recrée les tables"""
    print("🗑️  Suppression des données existantes...")
    db.drop_all()
    db.create_all()
    print("✅ Base de données vidée et tables recréées")

def generate_synthetic_data():
    """Génère toutes les données synthétiques"""
    
    print(f"\n📊 Génération de {NUM_PROJECTS} projets avec versions et demandes...\n")
    
    projects_created = 0
    versions_created = 0
    requests_created = 0
    
    for i in range(NUM_PROJECTS):
        # Créer un projet
        category = random.choice(CATEGORIES)
        project = Project(
            name=f"{fake.company()} - {category}",
            category=category
        )
        db.session.add(project)
        db.session.flush()
        projects_created += 1
        
        print(f"✓ Projet {i+1}/{NUM_PROJECTS}: {project.name}")
        
        # Créer plusieurs versions
        num_versions = random.randint(2, MAX_VERSIONS_PER_PROJECT)
        parent_version = None
        
        for v in range(num_versions):
            # Dates progressives
            days_ago = (num_versions - v) * 60  # Espacement de ~2 mois
            version_date = datetime.now() - timedelta(days=days_ago)
            start_date = date.today() - timedelta(days=days_ago + 30)
            
            # Progression du statut
            if v < num_versions - 2:
                status = 'Done'
                phase = 'Production'
                progress = 100
            elif v == num_versions - 2:
                status = random.choice(['Done', 'In Progress'])
                phase = random.choice(['Testing', 'Production'])
                progress = random.randint(70, 100)
            else:  # Dernière version
                status = 'In Progress'
                phase = random.choice(['Planning', 'Development', 'Testing'])
                progress = random.randint(20, 70)
            
            version_number = generate_version_number(v)
            
            version = ProjectVersion(
                project_id=project.id,
                version_number=version_number,
                parent_id=parent_version.id if parent_version else None,
                created_at=version_date,
                phase=phase,
                status=status,
                app_status=random.choice(APP_STATUSES) if status == 'Done' else 'Under Maintenance',
                integration_level=random.choice(['Local', 'Incoming', 'Prod']),
                hosting=random.choice(HOSTING),
                accessibility=random.choice(ACCESSIBILITY),
                cost=round(random.uniform(100, 5000), 2),
                cost_type=random.choice(['Monthly', 'Annual']),
                objective=generate_project_description(category),
                target_audience=fake.sentence(nb_words=10),
                features="; ".join([fake.sentence(nb_words=6) for _ in range(3)]),
                whats_new=f"Nouvelle fonctionnalité: {fake.sentence(nb_words=8)}",
                start_date=start_date,
                duration_days=random.randint(20, 90),
                progress=progress,
                deadline=start_date + timedelta(days=random.randint(30, 120)) if status != 'Done' else None,
                team_members=", ".join([fake.name() for _ in range(random.randint(2, 5))]),
                description=generate_version_description(phase, version_number)
            )
            db.session.add(version)
            db.session.flush()
            parent_version = version
            versions_created += 1
            
            print(f"  └─ Version {version_number} ({phase} - {status})")
            
            # Créer des demandes surtout pour les versions récentes
            if v >= num_versions - 2:  # Seulement pour les 2 dernières versions
                num_requests = random.randint(2, MAX_REQUESTS_PER_VERSION)
                
                for r in range(num_requests):
                    # Types de demande
                    is_user_request = random.choice([True, False])
                    is_tech_request = random.choice([True, False])
                    
                    user_types = random.sample(USER_REQUEST_TYPES, random.randint(0, 2)) if is_user_request else []
                    tech_types = random.sample(TECH_REQUEST_TYPES, random.randint(0, 2)) if is_tech_request else []
                    
                    request_date = version_date + timedelta(days=random.randint(1, 45))
                    
                    request = ContextRequest(
                        version_id=version.id,
                        created_at=request_date,
                        requester=fake.name(),
                        requester_role=random.choice(ROLES),
                        description=generate_request_description(),
                        user_request_type=",".join(user_types),
                        tech_request_type=",".join(tech_types),
                        planned_improvement=random.choice(PLANNED_IMPROVEMENTS),
                        improvement_type=random.choice(IMPROVEMENT_TYPES),
                        difficulty_level=random.choice(DIFFICULTY_LEVELS),
                        priority_level=random.choice(PRIORITY_LEVELS),
                        approved=random.choice(['En attente', 'Approuvé', 'Rejeté'])
                    )
                    db.session.add(request)
                    requests_created += 1
                
                if num_requests > 0:
                    print(f"     └─ {num_requests} demandes créées")
    
    db.session.commit()
    
    print(f"\n" + "="*60)
    print(f"✅ Génération terminée avec succès !")
    print(f"="*60)
    print(f"📁 Projets créés:          {projects_created}")
    print(f"📦 Versions créées:        {versions_created}")
    print(f"📝 Demandes créées:        {requests_created}")
    print(f"="*60)
    print(f"\n💡 Vous pouvez maintenant:")
    print(f"   1. Démarrer l'application: py app.py")
    print(f"   2. Ouvrir http://localhost:5000")
    print(f"   3. Explorer les projets et tester les fonctionnalités\n")

if __name__ == '__main__':
    with app.app_context():
        print("\n" + "="*60)
        print("🎲 GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES - ProjTrack")
        print("="*60)
        
        # Auto-confirmed
        clear_database()
        generate_synthetic_data()
