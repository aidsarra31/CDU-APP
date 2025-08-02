from flask import Blueprint, request, redirect, render_template, flash, url_for,session
from ldap3 import Server, Connection, NTLM
from db import get_connection
import oracledb

login_bp = Blueprint('login', __name__)
dsn = '10.37.22.21:1521/L1ZGE1.world'
serveur_ad = '10.114.106.13'
domaine = 'corp.sonatrach.dz'

try:
    oracledb.init_oracle_client(lib_dir=r"C:\instatntCl\instantclient_19_26")
except:
    pass

def verifier_ad(username, password):
    try:
        server = Server(serveur_ad)
        conn = Connection(server, user=f'{domaine}\\{username}', password=password, authentication=NTLM, auto_bind=True)
        conn.unbind()
        return True
    except:
        return False

def verifier_oracle(username, password):
    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        conn.close()
        return True
    except:
        return False

@login_bp.route('/', methods=['GET'])
def index():
    return render_template("index.html")
# Modifier la route de login pour stocker l'ID_ROLE dans la session
@login_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"🟡 Tentative login avec utilisateur : {username}")

    # 1️⃣ Vérification Active Directory
    if not verifier_ad(username, password):
        print("❌ Échec authentification AD")
        flash("❌ Échec authentification AD", "error")
        return redirect('/')

    print("✅ Authentification AD réussie")

    # 2️⃣ Vérification connexion Oracle avec user Oracle
    if not verifier_oracle(username, password):
        print("❌ Échec authentification Oracle")
        flash("❌ Échec authentification Oracle", "error")
        return redirect('/')

    print("✅ Authentification Oracle réussie")

    # 3️⃣ Récupération des rôles Oracle attribués et lien avec MGUSER
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("🔍 Requête Oracle pour récupérer le rôle applicatif...")

        cursor.execute("""
            SELECT r.ID_ROLE 
            FROM DBA_ROLE_PRIVS d
            JOIN CDUGL1Z.MGUSER r ON d.GRANTED_ROLE = r.ID_ROLE
            WHERE d.GRANTEE = :username
            AND r.ID_ECRAN = 'INF'
            AND ROWNUM = 1
        """, {"username": username.upper()})

        result = cursor.fetchone()

        if result:
            print(f"✅ Rôle Oracle trouvé : {result[0]}")
            session['username'] = username
            session['id_role'] = result[0]
            session['id_ecran'] = 'INF'
            print("➡️ Redirection vers le formulaire INF...")
            return redirect(url_for('inf.show_form'))
        else:
            print("⚠️ Aucun rôle applicatif trouvé dans MGUSER")
            flash("⚠️ Aucun accès applicatif trouvé", "error")
            return redirect('/')

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Erreur Oracle : {error.message}")
        flash(f"❌ Erreur Oracle: {error.message}", "error")
        return redirect('/')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

  