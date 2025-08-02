from flask import Blueprint, request, redirect, render_template, flash, url_for, session
from ldap3 import Server, Connection, NTLM
from db import get_connection
import oracledb

login_bp = Blueprint('login', __name__)

# Paramètres de connexion
dsn = '10.37.22.21:1521/L1ZGE1.world'
serveur_ad = '10.114.106.13'
domaine = 'corp.sonatrach.dz'

# Initialisation du client Oracle
try:
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
    print("✅ Oracle Instant Client initialisé.")
except Exception as e:
    print(f"⚠️ Impossible d'initialiser Oracle Instant Client : {e}")

# Fonction de vérification Active Directory
def verifier_ad(username, password):
    try:
        server = Server(f'ldap://{serveur_ad}')
        print(f"🟡 Connexion à l'AD sur : ldap://{serveur_ad}")

        conn = Connection(
            server,
            user=f'{domaine}\\{username}',
            password=password,
            authentication=NTLM
        )

        if not conn.bind():
            print("❌ Échec authentification AD")
            print(f"📃 Détail LDAP : {conn.result}")
            return False

        print("✅ Authentification AD réussie")
        conn.unbind()
        return True

    except Exception as e:
        print(f"❌ Erreur de connexion à l'AD : {e}")
        return False

# Fonction de vérification Oracle
def verifier_oracle(username, password):
    try:
        print(f"🟡 Tentative connexion Oracle avec user : {username}")
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        conn.close()
        print("✅ Connexion Oracle réussie")
        return True

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Erreur Oracle : {error.message}")
        return False

# Route index
@login_bp.route('/', methods=['GET'])
def index():
    return render_template("index.html")

# Route de login
@login_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"🟡 Tentative login avec utilisateur : {username}")

    # 1️⃣ Vérification Active Directory
    if not verifier_ad(username, password):
        flash("❌ Échec authentification Active Directory", "error")
        return redirect('/')

    # 2️⃣ Vérification Oracle
    if not verifier_oracle(username, password):
        flash("❌ Échec authentification Oracle", "error")
        return redirect('/')

    # 3️⃣ Récupération du rôle applicatif Oracle
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("🔍 Requête Oracle pour récupérer le rôle applicatif...")

        cursor.execute("""
            SELECT r.ID_ROLE 
            FROM DBA_ROLE_PRIVS d
            JOIN CDUGL1Z.MGUSER r ON d.GRANTED_ROLE = r.ID_ROLE
            WHERE d.GRANTEE = :username
            AND ROWNUM = 1
        """, {"username": username.upper()})

        result = cursor.fetchone()

        if result:
            id_role = result[0]
            print(f"✅ Rôle Oracle trouvé : {id_role}")

            session['username'] = username
            session['id_role'] = id_role

            # Redirection selon le rôle
            if id_role == 'INF_MANAGER':
                session['id_ecran'] = 'RECAP_GLOBAL'
                print("➡️ Redirection vers recap_global")
                return redirect(url_for('inf.recap_global'))

            elif id_role == 'INF_BDD':
                session['id_ecran'] = 'INF'
                print("➡️ Redirection vers formulaire INF")
                return redirect(url_for('inf.show_form'))

            else:
                print("⚠️ Rôle non autorisé pour cette application")
                flash("⚠️ Vous n'avez pas accès à cette application", "error")
                return redirect('/')

        else:
            print("⚠️ Aucun rôle applicatif trouvé dans MGUSER")
            flash("⚠️ Aucun accès applicatif trouvé", "error")
            return redirect('/')

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Erreur Oracle lors de la récupération du rôle : {error.message}")
        flash(f"❌ Erreur Oracle : {error.message}", "error")
        return redirect('/')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
