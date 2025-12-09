"""
Script pour vérifier le schéma de la table context_request
"""

import sqlite3
import os

DB_PATH = 'projects.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Base de données '{DB_PATH}' introuvable")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "="*60)
print("📋 SCHÉMA DE LA TABLE context_request")
print("="*60 + "\n")

# Récupérer les colonnes de la table
cursor.execute("PRAGMA table_info(context_request)")
columns = cursor.fetchall()

print(f"Nombre de colonnes: {len(columns)}\n")
print("ID | Nom de la colonne          | Type      | NotNull | Default")
print("-" * 70)

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"{col_id:2} | {name:25} | {col_type:9} | {not_null:7} | {default_val}")

print("\n" + "="*60)

# Vérifier si 'approved' existe
column_names = [col[1] for col in columns]
if 'approved' in column_names:
    print("✅ La colonne 'approved' EXISTE dans la base de données")
else:
    print("❌ La colonne 'approved' N'EXISTE PAS dans la base de données")
    print("\n💡 Il faut réexécuter le script de migration:")
    print("   python add_approved_column.py")

print("="*60 + "\n")

conn.close()
