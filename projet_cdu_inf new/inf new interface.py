from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from projet_cdu_inf.projet_cdu_inf.db_connection_sqlite import get_connection
from datetime import datetime
import oracledb

inf_bp = Blueprint('inf', __name__, template_folder='templates')

def check_rights(id_role, id_ecran, id_objet=None, action='SELECT'):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if id_objet is None:
            query = f"""
                SELECT CAN_{action}
                FROM CDUGL1Z.MGUSER
                WHERE ID_ROLE = :id_role
                  AND ID_ECRAN = :id_ecran
                  AND ID_OBJET IS NULL
                  AND ROWNUM = 1
            """
            params = {'id_role': id_role, 'id_ecran': id_ecran}
        else:
            query = f"""
                SELECT CAN_{action}
                FROM CDUGL1Z.MGUSER
                WHERE ID_ROLE = :id_role
                  AND ID_ECRAN = :id_ecran
                  AND ID_OBJET = :id_objet
                  AND ROWNUM = 1
            """
            params = {'id_role': id_role, 'id_ecran': id_ecran, 'id_objet': id_objet}

        cursor.execute(query, params)
        result = cursor.fetchone()
        return result and result[0] == 1

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"❌ Erreur Oracle dans check_rights(): {error.message}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@inf_bp.route('/')
def show_form():
    if 'id_role' not in session:
        return redirect('/')

    id_role = session['id_role']
    id_ecran = 'INF'

    if not check_rights(id_role, id_ecran, action='SELECT'):
        flash("⛔ Accès refusé à l'écran INF", "error")
        return redirect('/')

    can_edit_obs = check_rights(id_role, id_ecran, 'OBSERV', 'UPDATE')

    username = session.get('username', '').upper()
    periode = datetime.now().strftime("%m/%Y")  # Ex: "06/2025"

    structures = [
        "ADM", "APP", "D", "EXP", "GPR", "RHU", "FIN", "MNT", "HSE",
        "INP", "JUR", "MOG", "PROD", "RT", "SIE", "SIG", "TEC", "TNF", "MCHE"
    ]

    conn = get_connection()
    cursor = conn.cursor()

    # 🔍 Récupérer données existantes
    cursor.execute("""
        SELECT STRUCT, VALEUR, OBSERV 
        FROM CDUGL1Z.INF 
        WHERE IDUSER = :iduser AND PERIODE = :periode
    """, {"iduser": username, "periode": periode})

    data = cursor.fetchall()

    # 🎯 Préparer un dictionnaire avec 0 par défaut
    valeurs = {struct: 0 for struct in structures}
    observation = ""

    for row in data:
        struct, valeur, observ = row
        valeurs[struct] = valeur
        observation = observ or observation  # garder la première non vide

    cursor.close()
    conn.close()

    return render_template("inf.html",
                           username=username,
                           valeurs=valeurs,
                           can_edit_obs=can_edit_obs,
                           observation=observation)

@inf_bp.route('/submit-inf', methods=['POST'])
def submit_inf():
    if 'id_role' not in session:
        return redirect('/')

    if not check_rights(session['id_role'], 'INF', action='INSERT'):
        flash("⛔ Droits insuffisants pour insertion", "error")
        return redirect(url_for('inf.show_form'))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            flash("❌ Échec connexion base de données", "error")
            return redirect(url_for('inf.show_form'))

        type_intervention = request.form.get('type_intervention', '').strip()
        iduser = request.form.get('iduser', '').strip().upper()
        observ = request.form.get('observ', '').strip()
        periode = "05/2025"

        if not type_intervention or not iduser:
            flash("❌ Champs obligatoires manquants", "error")
            return redirect(url_for('inf.show_form'))

        structures = [
            "ADM", "APP", "D", "EXP", "GPR", "RHU", "FIN", "MNT", "HSE",
            "INP", "JUR", "MOG", "PROD", "RT", "SIE", "SIG", "TEC", "TNF", "MCHE"
        ]

        cursor = conn.cursor()
        inserted_rows = 0

        query = """
            INSERT INTO CDUGL1Z.INF (
                IDUSER, TYPE_INTERVENTION, STRUCT, VALEUR, OBSERV, PERIODE
            ) VALUES (
                :iduser, :type_intervention, :struct, :valeur, :observ, :periode
            )
        """

        for struct in structures:
            valeur = request.form.get(f'structure_{struct}', '0').strip()
            if valeur.isdigit() and int(valeur) > 0:
                cursor.execute(query, {
                    "iduser": iduser,
                    "type_intervention": type_intervention,
                    "struct": struct,
                    "valeur": int(valeur),
                    "observ": observ,
                    "periode": periode
                })
                inserted_rows += 1

        if inserted_rows == 0:
            flash("⚠️ Aucune intervention enregistrée", "warning")
        else:
            conn.commit()
            flash(f"✅ {inserted_rows} intervention(s) enregistrée(s)", "success")

    except oracledb.DatabaseError as e:
        error, = e.args
        flash(f"❌ Erreur Oracle [{error.code}]: {error.message}", "error")
    except Exception as e:
        flash(f"❌ Erreur système: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('inf.show_form'))
