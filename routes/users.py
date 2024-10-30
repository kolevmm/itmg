# routes/users.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import User, db
from werkzeug.security import generate_password_hash
from decorators import roles_required  # Импортиране на декоратора за роли

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Избор на роля от падащото меню
        
        # Създаване на нов потребител в базата данни
        new_user = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Потребителят е успешно добавен!', 'success')
        return redirect(url_for('users.create_user'))  # Пренасочване към същата страница

    roles = ['user', 'manager', 'admin']  # Списък с роли
    return render_template('create_user.html', roles=roles)
