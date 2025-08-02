from flask import Blueprint, render_template, request, redirect, flash, session ,get_flashed_messages
from db import get_connection

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
    print("📥 Affichage formulaire INF lancé")

    if 'id_role' not in session:
        print("❌ id_role manquant dans session")
        return redirect('/')

    id_role = session['id_role']
    username = session.get('username')
    id_ecran = 'INF'

    if not check_rights(id_role, id_ecran, action='SELECT'):
        print("⛔ Pas de droit SELECT")
        flash("⛔ Accès refusé à l'écran INF", "error")
        return redirect('/')

    can_edit_obs = check_rights(id_role, id_ecran, 'OBSERV', 'UPDATE')

    periode = '05/2025'
    type_intervention = request.args.get('type_intervention', 'SUPPORT').upper()

    conn = get_connection()
    cur = conn.cursor()

    # 🔥 Récupérer les valeurs existantes pour pré-remplissage
    cur.execute("""
        SELECT STRUCT, VALEUR
        FROM CDUGL1Z.INF
        WHERE IDUSER = :iduser
          AND PERIODE = :periode
          AND TYPE_INTERVENTION = :type_intervention
    """, {'iduser': username, 'periode': periode, 'type_intervention': type_intervention})

    existing_values = {row[0]: row[1] for row in cur.fetchall()}

    cur.close()
    conn.close()

    return render_template('inf.html',
                           username=username,
                           can_edit_obs=can_edit_obs,
                           existing_values=existing_values,  # 🔥 Passer au template
                           selected_type_intervention=type_intervention,
                           messages=get_flashed_messages(with_categories=True))

@inf_bp.route('/submit-inf', methods=['POST'])
def submit_inf():
    if 'id_role' not in session:
        return redirect('/')
        
    if not check_rights(session['id_role'], 'INF', action='INSERT'):
        flash("⛔ Droits insuffisants pour insertion", "error")
        return redirect('/inf')

    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            flash("❌ Échec connexion base de données", "error")
            return redirect('/inf')

        type_intervention = request.form.get('type_intervention', '').strip().upper()
        iduser = request.form.get('iduser', '').strip().upper()
        observ = request.form.get('observ', '').strip()
        periode = "05/2025"

        if not type_intervention or not iduser:
            flash("❌ Champs obligatoires manquants", "error")
            return redirect('/inf')

        structures = [
            "ADM", "APP", "D", "EXP", "GPR", "RHU", "FIN", "MNT", "HSE",
            "INP", "JUR", "MOG", "PROD", "RT", "SIE", "SIG", "TEC", "TNF", "MCHE","PIPING"
        ]

        cursor = conn.cursor()
        modified_rows = 0

        for struct in structures:
            valeur = request.form.get(f'structure_{struct}', '0').strip()
            if valeur.isdigit() and int(valeur) >= 0:
                valeur_int = int(valeur)

                # Vérifier si la ligne existe
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM CDUGL1Z.INF
                    WHERE IDUSER = :iduser
                      AND STRUCT = :struct
                      AND PERIODE = :periode
                      AND TYPE_INTERVENTION = :type_intervention
                """, {
                    "iduser": iduser,
                    "struct": struct,
                    "periode": periode,
                    "type_intervention": type_intervention
                })

                exists = cursor.fetchone()[0] > 0

                if exists:
                    # 🔧 UPDATE
                    cursor.execute("""
                        UPDATE CDUGL1Z.INF
                        SET VALEUR = :valeur, OBSERV = :observ
                        WHERE IDUSER = :iduser
                          AND STRUCT = :struct
                          AND PERIODE = :periode
                          AND TYPE_INTERVENTION = :type_intervention
                    """, {
                        "valeur": valeur_int,
                        "observ": observ,
                        "iduser": iduser,
                        "struct": struct,
                        "periode": periode,
                        "type_intervention": type_intervention
                    })
                else:
                    # 🔧 INSERT si valeur > 0
                    if valeur_int > 0:
                        cursor.execute("""
                            INSERT INTO CDUGL1Z.INF (
                                IDUSER, TYPE_INTERVENTION, STRUCT, VALEUR, OBSERV, PERIODE
                            ) VALUES (
                                :iduser, :type_intervention, :struct, :valeur, :observ, :periode
                            )
                        """, {
                            "iduser": iduser,
                            "type_intervention": type_intervention,
                            "struct": struct,
                            "valeur": valeur_int,
                            "observ": observ,
                            "periode": periode
                        })
                modified_rows += 1

        conn.commit()

        if modified_rows == 0:
            flash("⚠️ Aucune modification enregistrée", "warning")
        else:
            flash(f"✅ {modified_rows} ligne(s) modifiée(s)/ajoutée(s)", "success")

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

    return redirect('/inf')

@inf_bp.route('/recap_global')
def recap_global():
    if 'id_role' not in session or 'username' not in session:
        return redirect('/')

    id_role = session['id_role']
    username = session['username']
    id_ecran = 'RECAP_GLOBAL'

    if not check_rights(id_role, id_ecran, action='SELECT'):
        flash("⛔ Accès refusé à l'écran Récapitulatif Global", "error")
        return redirect('/inf')

    selected_user = request.args.get('user', '').strip()
    selected_struct = request.args.get('struct', '').strip()
    selected_type_intervention = request.args.get('type_intervention', '').strip()
    periode = '05/2025'

    conn = get_connection()
    cur = conn.cursor()

    # 🔥 Query principale
    query = """
    SELECT STRUCT, IDUSER, TYPE_INTERVENTION, VALEUR, OBSERV, PERIODE
    FROM CDUGL1Z.INF
    WHERE PERIODE = :periode
"""
    params = {'periode': periode}

    if selected_user:
        query += " AND IDUSER = :selected_user"
        params['selected_user'] = selected_user

    if selected_struct:
        query += " AND STRUCT = :selected_struct"
        params['selected_struct'] = selected_struct

    if selected_type_intervention:
        query += " AND TYPE_INTERVENTION = :selected_type_intervention"
        params['selected_type_intervention'] = selected_type_intervention

    query += " ORDER BY STRUCT, IDUSER"

    cur.execute(query, params)
    data_all = cur.fetchall()

      # 🔥 Summary table : total par STRUCTURE
    cur.execute("""
        SELECT STRUCT, COUNT(*)
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
        GROUP BY STRUCT
        ORDER BY STRUCT
    """, {'periode': periode})
    summary_data = cur.fetchall()

    # 🔥 Calcul total INF (Support, BDD, Réseau)
    inf_query = """
        SELECT NVL(SUM(VALEUR),0)
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
          AND TYPE_INTERVENTION IN ('SUPPORT', 'BDD', 'RESEAU')
    """
    inf_params = {'periode': periode}

    if selected_user:
        inf_query += " AND IDUSER = :selected_user"
        inf_params['selected_user'] = selected_user
    else:
        inf_query += " AND IDUSER = :username"
        inf_params['username'] = username

    cur.execute(inf_query, inf_params)
    total_inf = cur.fetchone()[0]

    # 🔥 Calcul total TELECOM
    tel_query = """
        SELECT NVL(SUM(VALEUR),0)
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
          AND TYPE_INTERVENTION = 'TELECOM'
    """
    tel_params = {'periode': periode}

    if selected_user:
        tel_query += " AND IDUSER = :selected_user"
        tel_params['selected_user'] = selected_user
    else:
        tel_query += " AND IDUSER = :username"
        tel_params['username'] = username

    cur.execute(tel_query, tel_params)
    total_tel = cur.fetchone()[0]

    # 🔥 Récupérer listes pour filtres
    cur.execute("""
        SELECT DISTINCT IDUSER
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
        ORDER BY IDUSER
    """, {'periode': periode})
    users = [r[0] for r in cur.fetchall()]

    cur.execute("""
        SELECT DISTINCT STRUCT
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
        ORDER BY STRUCT
    """, {'periode': periode})
    structures = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template("recap_global.html",
                           data_all=data_all,
                           users=users,
                           summary_data=summary_data,
                           structures=structures,
                           selected_user=selected_user,
                           selected_struct=selected_struct,
                           selected_type_intervention=selected_type_intervention,
                           total_inf=total_inf,   # 🔥 Passe la variable au template
                           total_tel=total_tel,   # 🔥 Passe la variable au template
                           periode=periode)
