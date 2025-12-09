"""
Script pour nettoyer le cache Python et recréer proprement la base de données
"""

import os
import shutil
import sys

print("\n" + "="*60)
print("🧹 NETTOYAGE COMPLET DU CACHE PYTHON")
print("="*60 + "\n")

# 1. Supprimer tous les fichiers __pycache__
print("📁 Suppression des répertoires __pycache__...")
pycache_count = 0
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        shutil.rmtree(pycache_path)
        pycache_count += 1
        print(f"   ✓ Supprimé: {pycache_path}")

print(f"✅ {pycache_count} répertoire(s) __pycache__ supprimé(s)\n")

# 2. Supprimer tous les fichiers .pyc
print("📄 Suppression des fichiers .pyc...")
pyc_count = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_path = os.path.join(root, file)
            os.remove(pyc_path)
            pyc_count += 1
            print(f"   ✓ Supprimé: {pyc_path}")

print(f"✅ {pyc_count} fichier(s) .pyc supprimé(s)\n")

# 3. Supprimer la base de données
if os.path.exists('projects.db'):
    print("🗑️  Suppression de projects.db...")
    os.remove('projects.db')
    print("✅ Base de données supprimée\n")

print("="*60)
print("✅ Nettoyage terminé !")
print("="*60)
print("\n💡 Prochaines étapes:")
print("   1. python recreate_database.py")
print("   2. python generate_sample_data.py")
print("   3. python app.py\n")
