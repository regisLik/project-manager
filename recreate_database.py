"""
Script pour recréer complètement la base de données avec le nouveau schéma
ATTENTION: Ce script supprime toutes les données existantes !
"""

from app import app, db
import os

DB_PATH = 'projects.db'

with app.app_context():
    print("\n" + "="*60)
    print("🔄 RECRÉATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("="*60)
    
    response = input("\n⚠️  ATTENTION: Toutes les données seront supprimées ! Continuer ? (o/N): ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Opération annulée")
        exit(0)
    
    # Supprimer l'ancien fichier
    if os.path.exists(DB_PATH):
        print(f"\n🗑️  Suppression de {DB_PATH}...")
        os.remove(DB_PATH)
        print("✅ Ancien fichier supprimé")
    
    # Recréer les tables
    print("\n📝 Création des tables avec le nouveau schéma...")
    db.create_all()
    print("✅ Tables créées avec succès")
    
    print("\n" + "="*60)
    print("✅ Base de données recréée !")
    print("="*60)
    print("\n💡 Prochaine étape:")
    print("   Générer des données de test:")
    print("   python generate_sample_data.py")
    print("\n   Puis redémarrer Flask:")
    print("   python app.py\n")
