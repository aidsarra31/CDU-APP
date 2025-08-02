from flask import Blueprint, request, redirect, flash, render_template, url_for
from db import get_connection

prod_bp = Blueprint('prod', __name__)

@prod_bp.route('/prod', methods=['GET', 'POST'])
def prod():
    if request.method == 'POST':
        conn = get_connection()
        cur = conn.cursor()

        for i in range(1, 7):  # 1 à 6 pour T100 à T600
            train = request.form.get(f'train_{i}')
            situation = request.form.get(f'situation_{i}')
            jours_arret = request.form.get(f'jours_arret_{i}')
            tp = request.form.get(f'tp_{i}')
            ac = request.form.get(f'ac_{i}')
            observation = request.form.get(f'observation_{i}')

            # Vérifie si la ligne a été remplie (par exemple on exige au moins le train + situation + une valeur saisie)
            if train and situation and (jours_arret or tp or ac or observation):
                # Cast vers les bons types
                try:
                    jours_arret = int(jours_arret) if jours_arret else None
                    tp = float(tp) if tp else None
                    ac = float(ac) if ac else None
                except ValueError:
                    flash(f"Erreur de saisie dans la ligne {train}", 'danger')
                    continue

                # Exécuter l'insertion
                
                cur.execute("""
                    INSERT INTO PROD (TRAIN, SITUATION, JOURS_ARRET, TP, AC, OBSERVATION)
                    VALUES (:1, :2, :3, :4, :5, :6)
                """, (train, situation, jours_arret, tp, ac, observation))
                
                conn.commit()
        cur.close()
        conn.close()


        flash("Insertion réussie.", "success")
        return redirect(url_for('prod.prod'))

    # GET
    return render_template('prod.html', periode_ouverte="07/2025")
