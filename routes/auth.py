# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Проверка на потребителското име и паролата
        if user and check_password_hash(user.password, password):
            login_user(user)  # Вход на потребителя
            flash('Влязохте успешно!', 'success')
            return redirect(url_for('dashboard'))  # Пренасочване към контролния панел
        else:
            flash('Невалидно име на потребител или парола.', 'danger')

    return render_template('login.html')  # Връщане на шаблона за логин

@auth_bp.route('/logout')
def logout():
    logout_user()  # Изход на потребителя
    flash('Излязохте успешно!', 'success')
    return redirect(url_for('auth.login'))
