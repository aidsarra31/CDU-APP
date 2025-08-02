import sqlite3
import os

db_path = "data/cdu.db"
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Table INF
cur.execute("""
CREATE TABLE IF NOT EXISTS INF (
    IDUSER TEXT,
    TYPE_INTERVENTION TEXT,
    STRUCT TEXT,
    VALEUR INTEGER,
    OBSERV TEXT,
    PERIODE TEXT
)
""")

# Table MGUSER (droits d’accès)
cur.execute("""
CREATE TABLE IF NOT EXISTS MGUSER (
    ID_ROLE TEXT,
    ID_ECRAN TEXT,
    ID_OBJET TEXT,
    TYPE_OBJET TEXT,
    CAN_SELECT INTEGER,
    CAN_INSERT INTEGER,
    CAN_UPDATE INTEGER,
    CAN_DELETE INTEGER
)
""")

# Données de test
cur.execute("DELETE FROM INF")
cur.execute("DELETE FROM MGUSER")

cur.executemany("""
INSERT INTO INF (IDUSER, TYPE_INTERVENTION, STRUCT, VALEUR, OBSERV, PERIODE)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    ("USR01", "Support", "APP", 10, "RAS", "05/2025"),
    ("USR02", "Telecom", "MNT", 8, "OK", "05/2025"),
    ("USR03", "BDD", "PROD", 15, "Test", "05/2025")
])

cur.execute("""
INSERT INTO MGUSER (ID_ROLE, ID_ECRAN, ID_OBJET, TYPE_OBJET, CAN_SELECT, CAN_INSERT, CAN_UPDATE, CAN_DELETE)
VALUES ('INF_BDD', 'INF', NULL, NULL, 1, 1, 1, 0)
""")

conn.commit()
conn.close()
print("✅ Base SQLite initialisée.")