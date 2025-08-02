import os

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    import sqlite3

    def get_connection():
        db_path = "data/cdu.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # pour accès par nom
        return conn

else:
    import oracledb

    def get_connection():
        return oracledb.connect(
            user="CDUGL1Z",
            password="votre_mot_de_passe",
            dsn="votre_serveur:1521/votre_service"
        )