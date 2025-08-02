import oracledb

def afficher_table(cursor, table_name):
    # Afficher la structure de la table
    print(f"\n🔍 Structure de la table {table_name}:")
    cursor.execute(f"""
        SELECT column_name, data_type, data_length, nullable
        FROM user_tab_columns
        WHERE table_name = '{table_name.upper()}'
        ORDER BY column_id
    """)
    colonnes = cursor.fetchall()
    
    print("Colonne".ljust(25) + "Type".ljust(20) + "Taille".ljust(10) + "Nullable")
    print("-" * 70)
    for col in colonnes:
        print(f"{col[0].ljust(25)}{col[1].ljust(20)}{str(col[2]).ljust(10)}{'NULL' if col[3] == 'Y' else 'NOT NULL'}")

    # Afficher le contenu de la table
    print(f"\n📊 Contenu de la table {table_name}:")
    cursor.execute(f"SELECT * FROM {table_name}  ")
    
    # Récupérer les résultats
    noms_colonnes = [desc[0] for desc in cursor.description]
    lignes = cursor.fetchall()
    
    if not lignes:
        print(f"La table {table_name} est vide.")
        return
    
    # Calculer les largeurs de colonnes
    largeurs = [len(nom) for nom in noms_colonnes]
    for ligne in lignes:
        for i, valeur in enumerate(ligne):
            largeur_valeur = len(str(valeur)) if valeur is not None else 4
            largeurs[i] = max(largeurs[i], largeur_valeur)
    
    # Afficher l'en-tête
    en_tete = " | ".join(nom.ljust(largeurs[i]) for i, nom in enumerate(noms_colonnes))
    print(en_tete)
    print("-" * len(en_tete))
    
    # Afficher les données
    for ligne in lignes:
        ligne_formatee = " | ".join(
            str(valeur).ljust(largeurs[i]) if valeur is not None else "NULL".ljust(largeurs[i])
            for i, valeur in enumerate(ligne)
        )
        print(ligne_formatee)

def main():
    # Configuration de la connexion
    config = {
        "user": "CDUGL1Z",
        "password": "cdugl1z",
        "dsn": "10.37.22.21:1521/L1ZGE1.world",
        "lib_dir": r"C:\oracle\instantclient_23_8"
    }

    try:
        # Initialisation du client Oracle
        oracledb.init_oracle_client(lib_dir=config["lib_dir"])
        
        # Connexion à la base de données
        with oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"]
        ) as connection:
            print("✅ Connexion réussie à Oracle")
            
            with connection.cursor() as cursor:
                # Afficher le contenu de la table PROD
                afficher_table(cursor, "PROD")
                
    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Erreur Oracle [{error.code}]: {error.message}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
    finally:
        print("\n✅ Opération terminée")

if __name__ == "__main__":
    main()