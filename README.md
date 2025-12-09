# ProjTrack - Project Management System

Application de gestion de projets avec système de versioning et gestion des demandes de modification.

## 🚀 Démarrage Rapide

### Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd project-manager
```

2. **Créer et activer l'environnement virtuel**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Générer des données de test (optionnel mais recommandé)**
```bash
python generate_sample_data.py
```
Ce script génère automatiquement des projets, versions et demandes pour tester l'application.

5. **Lancer l'application**
```bash
python app.py
```

6. **Ouvrir dans le navigateur**
```
http://localhost:5000
```

## 📊 Fonctionnalités

### Gestion de Projets
- Création et gestion de projets multi-catégories (Web, Mobile, Desktop, API, Data)
- Système de versioning avec héritage parent-enfant
- Suivi de progression et deadlines
- Gestion d'équipes et budgets

### Gestion des Demandes
- Page dédiée pour visualiser toutes les requêtes
- Filtrage par projet
- Statistiques en temps réel (priorité, difficulté, approbation)
- Édition via panneau latéral
- Création de nouvelles demandes

### Future Upgrade Section
- Statistiques visuelles des demandes par projet
- Cartes interactives avec métriques clés
- Lien direct vers la vue globale des requêtes

### Interface
- Navigation collapsible avec sous-menus
- Mode sombre/clair
- Design moderne avec Tailwind CSS
- Interactions fluides avec Alpine.js

## 🗂️ Structure du Projet

```
project-manager/
├── app.py                      # Application Flask principale
├── generate_sample_data.py     # Générateur de données synthétiques
├── seed_data.py               # Script de seed basique
├── projects.db                # Base de données SQLite
├── templates/
│   ├── base.html              # Template de base
│   ├── dashboard.html         # Page d'accueil
│   ├── projects.html          # Liste des projets
│   ├── project_detail.html    # Détails d'un projet
│   ├── requests.html          # Gestion globale des requêtes
│   └── ...
├── static/
│   └── ...
└── uploads/                   # Documents téléchargés
```

## 🛠️ Technologies Utilisées

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Tailwind CSS, Alpine.js
- **Base de données**: SQLite
- **Génération de données**: Faker

## 📝 Modèles de Données

### Project
- Nom, catégorie
- Relation avec versions

### ProjectVersion
- Numéro de version, phase, statut
- Dates, budget, équipe
- Objectifs, fonctionnalités
- Relation parent-enfant pour versioning

### ContextRequest
- Demandeur, rôle, description
- Types de demande (user/tech)
- Niveau de priorité, difficulté
- Amélioration prévue

## 🔄 Workflow de Développement

1. **Cloner le projet**
2. **Générer des données de test** avec `generate_sample_data.py`
3. **Développer vos fonctionnalités**
4. **Tester avec les données synthétiques**
5. **Commit et push**

## 📦 Requirements

Voir `requirements.txt` pour la liste complète des dépendances.

Principales dépendances:
- Flask
- Flask-SQLAlchemy
- Faker (pour génération de données)

## 🎨 Personnalisation

### Générer plus de données
Modifier les constantes dans `generate_sample_data.py`:
```python
NUM_PROJECTS = 8              # Nombre de projets
MAX_VERSIONS_PER_PROJECT = 5  # Versions max par projet
MAX_REQUESTS_PER_VERSION = 6  # Requêtes max par version
```

### Thème
L'application supporte le mode sombre automatiquement via Tailwind CSS.

## 📄 License

Ce projet est sous license MIT.
