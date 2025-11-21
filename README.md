# Project Manager

Application de gestion de projets avec tableau de bord, statistiques et diagramme de Gantt.

## Fonctionnalités

*   **Dashboard** : Vue d'ensemble des projets, KPIs, et prochaines livraisons.
*   **Projets** : Gestion complète des projets (création, édition, versioning).
*   **Statistiques** : Analyse visuelle des données (budget, statuts, types de projets).
*   **Gantt** : Visualisation temporelle des projets.

## Installation

1.  Cloner le dépôt :
    ```bash
    git clone <votre-repo-url>
    cd project-manager
    ```

2.  Créer un environnement virtuel (recommandé) :
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4.  Initialiser la base de données et ajouter des données de test :
    ```bash
    python seed_data.py
    ```

5.  Lancer l'application :
    ```bash
    python app.py
    ```

6.  Accéder à l'application sur `http://127.0.0.1:5000`.

## Déploiement sur GitHub

Pour mettre ce projet sur GitHub, suivez ces étapes :

1.  Initialiser Git :
    ```bash
    git init
    ```

2.  Ajouter les fichiers :
    ```bash
    git add .
    ```

3.  Faire le premier commit :
    ```bash
    git commit -m "Initial commit: Project Manager App"
    ```

4.  Créer un nouveau repository sur GitHub (sans README/gitignore par défaut).

5.  Lier le dépôt local au dépôt distant (remplacez l'URL) :
    ```bash
    git remote add origin https://github.com/votre-username/project-manager.git
    ```

6.  Pousser le code :
    ```bash
    git branch -M main
    git push -u origin main
    ```

## Structure du Projet

*   `app.py` : Application Flask principale.
*   `templates/` : Fichiers HTML (Jinja2).
*   `static/` : Fichiers statiques (CSS, JS, Images).
*   `seed_data.py` : Script pour peupler la base de données.
*   `requirements.txt` : Liste des dépendances Python.
