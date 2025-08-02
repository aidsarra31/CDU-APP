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
    id_ecran = 'INF'

    if not check_rights(id_role, id_ecran, action='SELECT'):
        print("⛔ Pas de droit SELECT")
        flash("⛔ Accès refusé à l'écran INF", "error")
        return redirect('/')

    can_edit_obs = check_rights(id_role, id_ecran, 'OBSERV', 'UPDATE')

    # 🔢 Charger totaux par structure
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT STRUCT, SUM(VALEUR) AS TOTAL
        FROM CDUGL1Z.INF
        WHERE PERIODE = '05/2025'
        GROUP BY STRUCT
        ORDER BY STRUCT
    """)
    data_totaux = cur.fetchall()
    cur.close()
    conn.close()

    print(f"✅ Affichage du formulaire INF avec can_edit_obs = {can_edit_obs}")
    return render_template('inf.html',
                           username=session.get('username'),
                           can_edit_obs=can_edit_obs,
                           data_totaux=data_totaux,
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

        type_intervention = request.form.get('type_intervention', '').strip()
        iduser = request.form.get('iduser', '').strip().upper()
        observ = request.form.get('observ', '').strip()
        periode = "05/2025"  # Valeur fixe en VARCHAR

        if not type_intervention or not iduser:
            flash("❌ Champs obligatoires manquants", "error")
            return redirect('/inf')

        structures = [
            "ADM", "APP", "D", "EXP", "GPR", "RHU", "FIN", "MNT", "HSE",
            "INP", "JUR", "MOG", "PROD", "RT", "SIE", "SIG", "TEC", "TNF", "MCHE","PIPING"
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

    return redirect('/inf')

@inf_bp.route('/recap_global')
def recap_global():
    if 'id_role' not in session:
        return redirect('/')

    id_role = session['id_role']
    id_ecran = 'RECAP_GLOBAL'

    # Vérifier droit SELECT
    if not check_rights(id_role, id_ecran, action='SELECT'):
        flash("⛔ Accès refusé à l'écran Récapitulatif Global", "error")
        return redirect('/inf')

    # 🔥 Récupérer les filtres depuis l'URL (GET)
    selected_user = request.args.get('user', '').strip()
    selected_struct = request.args.get('struct', '').strip()
    selected_type_intervention = request.args.get('type_intervention', '').strip()
    periode = '05/2025'  # Pour l'instant valeur fixe, adapte plus tard

    conn = get_connection()
    cur = conn.cursor()

    # 🔎 Debug filters
    print(f"🔎 Filtre - User: {selected_user}, Struct: {selected_struct}, Type Intervention: {selected_type_intervention}, Periode: {periode}")

    # 🔥 Requête principale avec filtres
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

    # 🔧 Debug final query
    print(f"🔧 Query finale : {query}")
    print(f"🔧 Params : {params}")

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

    # 🔥 Récupérer la liste des utilisateurs distincts pour le filtre
    cur.execute("""
        SELECT DISTINCT IDUSER
        FROM CDUGL1Z.INF
        WHERE PERIODE = :periode
        ORDER BY IDUSER
    """, {'periode': periode})
    users = [r[0] for r in cur.fetchall()]

    # 🔥 Récupérer la liste des structures distinctes pour le filtre
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
                           summary_data=summary_data,
                           users=users,
                           structures=structures,
                           selected_user=selected_user,
                           selected_struct=selected_struct,
                           selected_type_intervention=selected_type_intervention,
                           periode=periode)
