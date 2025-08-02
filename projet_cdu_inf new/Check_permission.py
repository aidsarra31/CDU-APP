from functools import wraps
from flask import request, redirect, flash, session
from db import get_connection

# Middleware pour vérifier les permissions
def check_permission(id_ecran, action):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            id_role = session.get('id_role')  # Assurez-vous que le rôle est stocké dans la session après login

            if not id_role:
                flash("🔒 Vous n'êtes pas connecté.", "error")
                return redirect('/login')

            conn = get_connection()
            if not conn:
                flash("❌ Connexion à la base impossible.", "error")
                return redirect('/')

            try:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT CAN_SELECT, CAN_INSERT, CAN_UPDATE, CAN_DELETE
                    FROM MGUSER
                    WHERE ID_ROLE = :id_role AND ID_ECRAN = :id_ecran
                """, {"id_role": id_role, "id_ecran": id_ecran})

                row = cursor.fetchone()
                if not row:
                    flash("❌ Accès refusé à cet écran.", "error")
                    return redirect('/')

                # Vérifie le droit spécifique demandé
                permission_map = {
                    'select': row[0],
                    'insert': row[1],
                    'update': row[2],
                    'delete': row[3],
                }

                if permission_map.get(action, 'N') != 'Y':
                    flash(f"❌ Permission {action.upper()} refusée pour cet écran.", "error")
                    return redirect('/')

            except Exception as e:
                flash(f"❌ Erreur de vérification des droits : {str(e)}", "error")
                return redirect('/')
            finally:
                conn.close()

            return view_func(*args, **kwargs)
        return wrapper
    return decorator
