"""
Script de migration pour ajouter la colonne 'approved' à la table context_request
"""

import sqlite3
import os

DB_PATH = 'instance/projects.db'

def add_approved_column():
    """Ajoute la colonne approved à la table context_request"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données '{DB_PATH}' introuvable")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(context_request)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'approved' in columns:
            print("✅ La colonne 'approved' existe déjà")
            return
        
        # Ajouter la colonne
        print("📝 Ajout de la colonne 'approved'...")
        cursor.execute("""
            ALTER TABLE context_request 
            ADD COLUMN approved TEXT DEFAULT 'En attente'
        """)
        
        conn.commit()
        print("✅ Colonne 'approved' ajoutée avec succès")
        print("   Valeur par défaut: 'En attente'")
        print("   Valeurs possibles: En attente, Approuvé, Rejeté")
        
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔄 MIGRATION: Ajout de la colonne 'approved'")
    print("="*60 + "\n")
    
    add_approved_column()
    
    print("\n" + "="*60)
    print("✅ Migration terminée")
    print("="*60)
    print("\n💡 Redémarrez l'application Flask pour appliquer les changements\n")
