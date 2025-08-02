from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_home():
    # Only allow access if user is admin
    if 'id_role' not in session or session['id_role'] != 'ADMIN':
        return redirect('/')

    return render_template('admin_home.html')
