from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv
from models import db, User  # Уверете се, че сте импортирали User тук
import os

load_dotenv()

# Инициализация на приложението и конфигурации
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация на базата данни
db.init_app(app)

# Инициализация на Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Пренасочване към правилния маршрут за логин

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистриране на Blueprints
from routes.clients import clients_bp
from routes.services import services_bp
from routes.visits import visits_bp
from routes.users import users_bp
from routes.employees import employees_bp
from routes.reports import reports_bp
from routes.auth import auth_bp

app.register_blueprint(clients_bp)
app.register_blueprint(services_bp)
app.register_blueprint(visits_bp)
app.register_blueprint(users_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(auth_bp)

@app.before_first_request
def create_tables():
    db.create_all()

# Главна страница
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Страница за контролен панел
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
