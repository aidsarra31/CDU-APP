import oracledb

# Initialisation du client Oracle
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")

try:
    # Connexion
    connection = oracledb.connect(
        user="CDUGL1Z",
        password="cdugl1z",
        dsn="10.37.22.21:1521/L1ZGE1.world"
    )
    print("✅ Connexion réussie à Oracle")

    cur = connection.cursor()

    # 🔥 TRUNCATE pour vider la table INF
    cur.execute("TRUNCATE TABLE CDUGL1Z.INF")
    print("🗑️ Table CDUGL1Z.INF vidée avec succès.")

    # 🔍 Vérifier qu'elle est vide
    cur.execute("""
        SELECT COUNT(*)
        FROM CDUGL1Z.INF
    """)
    count = cur.fetchone()[0]

    print(f"📊 Nombre de lignes après TRUNCATE : {count}")

    # ✅ Fermeture
    cur.close()
    connection.close()
    print("\n✅ Connexion fermée.")

except oracledb.DatabaseError as e:
    error, = e.args
    print(f"❌ Erreur Oracle [{error.code}]: {error.message}")

except Exception as e:
    print("❌ Erreur générale :", e)
