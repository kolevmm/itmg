from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from functools import wraps
import random
import os
from dotenv import load_dotenv

load_dotenv()  # Зарежда променливите от .env файла

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Използва статичния ключ от .env файла
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Задайте маршрута за вход


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Нямате права за достъп до тази страница!', 'danger')
                return redirect(url_for('dashboard'))  # Пренасочване до главната страница или панел
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
# Функция за зареждане на потребителя, базирана на ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Заменете 'User' с вашия модел на потребителя

# Задайте маршрута за логин
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модел за потребители
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50))  # Роля по подразбиране

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
# Модел за услуги
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)

# Модел за клиенти
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)  # Опционално поле за имейл
    phone = db.Column(db.String(15), nullable=True)  # Опционално поле за телефон

    visits = db.relationship('Visit', backref='client', lazy=True)  # Връзка към Visit

class Employee(db.Model):  # Модел за служители
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Свързано с клиента
    client = db.relationship('Client', backref='employees')  # Връзка с клиента

# Модел за посещения
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Външна връзка към клиента
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # Продължителност в часове
    notes = db.Column(db.String(200), nullable=True)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)  # Дата на посещението
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # Свързване с модела за служители
    
    employee = db.relationship('Employee', backref='visits')  # Релация
    service = db.relationship('Service', backref='visits')  # Връзка към Service

@app.before_first_request
def create_tables():
    db.create_all()  # Създава таблиците, ако не съществуват.

@app.route('/')
def index():
    if current_user.is_authenticated:  # Проверка дали потребителят е аутентифициран
        return redirect(url_for('dashboard'))  # Пренасочете към главния панел
    return render_template('login.html')  # В противен случай покажете логин страницата

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Проверка на потребителското име и паролата
        if user and check_password_hash(user.password, password):
            login_user(user)  # Вход на потребителя
            flash('Влязохте успешно!', 'success')
            return redirect(url_for('dashboard'))  # Пренасочете към основната страница или контролния панел
        else:
            flash('Невалидно име на потребител или парола.', 'danger')

    return render_template('login.html')  # Връщане на шаблона за логин

@app.route('/logout')
def logout():
    logout_user()  # Изход на потребителя
    flash('Изходят успешно!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  # Страница след влизане

@app.route('/add_service', methods=['GET', 'POST'])
@role_required('admin')  # Само администратори имат достъп
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        new_service = Service(name=name, description=description, price=float(price))
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('list_services'))

    return render_template('add_service.html')

@app.route('/list_services')
def list_services():
    services = Service.query.all()
    
    return render_template('list_services.html', services=services)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        client_id = request.form.get('client_id')  # Избиране на клиента за служителя
        new_employee = Employee(name=name, client_id=client_id)
        db.session.add(new_employee)
        db.session.commit()
        flash('Служителят беше добавен успешно!', 'success')
        return redirect(url_for('add_employee'))

    clients = Client.query.all()  # Вземане на всички клиенти за падащото меню
    return render_template('add_employee.html', clients=clients)

@app.route('/get_employees/<int:client_id>')
def get_employees(client_id):
    employees = Employee.query.filter_by(client_id=client_id).all()  # Получаване на служители по играещ клиент
    return jsonify([{'id': employee.id, 'name': employee.name} for employee in employees])

# Добавяне на клиент
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        new_client = Client(name=name, email=email, phone=phone)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('list_clients'))

    return render_template('add_client.html')

# Списък на клиенти
@app.route('/list_clients')
def list_clients():
    clients = Client.query.all()  # Извлича всички клиенти от базата данни
    return render_template('list_clients.html', clients=clients)

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)

    if request.method == 'POST':
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        
        db.session.commit()
        flash('Клиентът беше успешно актуализиран!', 'success')
        return redirect(url_for('list_clients'))  # Пренасочване към списъка с клиенти
    return render_template('edit_client.html', client=client)

@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    # Първо изтрийте свързаните посещения
    Visit.query.filter_by(client_id=client.id).delete()
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('list_clients'))  # Пренасочване към списъка с клиенти



@app.route('/add_visit', methods=['GET', 'POST'])
def add_visit():
    if request.method == 'POST':
        client_id = request.form['client_id']
        service_id = request.form['service_id']
        employee_id = request.form.get('employee_id')  # Получаване на ID на служителя
        duration = request.form['duration']
        notes = request.form['notes']
        visit_date = request.form['visit_date']  # Получаване на дата
        
        new_visit = Visit(client_id=client_id,
                          service_id=service_id,
                          duration=float(duration),
                          notes=notes,
                          visit_date=datetime.strptime(visit_date, '%Y-%m-%d'),
                          employee_id=employee_id
                          )
        
         # Задаване на ID на служителя
        db.session.add(new_visit)
        db.session.commit()

    clients = Client.query.all()  # Вземане на всички клиенти
    services = Service.query.all()  # Вземане на услугите за формуляра
    employees = Employee.query.all()  # Взимане на всички служители
    return render_template('add_visit.html', clients=clients, services=services, employees=employees)


@app.route('/list_visits')
def list_visits():
    visits = Visit.query.all()
    
    # Инициализация на общата сума
    total_amount = 0
    for visit in visits:
        # Отпечатване на информацията за всяко посещение
        print(f"Visit ID: {visit.id}, Client ID: {visit.client_id}, Service ID: {visit.service_id}, Duration: {visit.duration}, Service Price: {visit.service.price}")

        # Изчисляване на таксата и актуализиране на total_amount
        if visit.service.price is not None and visit.duration is not None:
            visit_total = visit.duration * visit.service.price
            total_amount += visit_total  # Събиране на таксите
            print(f"Visit Total: {visit_total}")  # Печата на индивидуалната такса

    # Отпечатка на общата сума
    print(f"Total Amount: {total_amount}")

    return render_template('list_visits.html', visits=visits, total_amount=total_amount)

@app.route('/edit_visit/<int:visit_id>', methods=['GET', 'POST'])
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)

    if request.method == 'POST':
        visit.client_name = request.form['client_name']
        visit.service_id = request.form['service_id']
        visit.duration = request.form['duration']
        visit.notes = request.form['notes']
        visit.visit_date = datetime.strptime(request.form['visit_date'], '%Y-%m-%d')

        db.session.commit()
        return redirect(url_for('list_visits'))

    services = Service.query.all()
    return render_template('edit_visit.html', visit=visit, services=services)

@app.route('/delete_visit/<int:visit_id>', methods=['POST'])
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)  # Извличане на посещение по ID
    db.session.delete(visit)  # Изтриване на записа
    db.session.commit()  # Записване на промените
    return redirect(url_for('list_visits'))  # Пренасочване към списъка с посещения

@app.route('/create_user', methods=['GET', 'POST'])
@role_required('user')
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
        return redirect(url_for('create_user'))  # Пренасочване след успешен запис

    roles = ['user', 'manager', 'admin']  # Списък с роли
    return render_template('create_user.html', roles=roles)


@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        visits = Visit.query.filter(
            Visit.client_id == client_id,
            Visit.visit_date >= start_date,
            Visit.visit_date <= end_date
        ).all()

        total_amount = sum(
            visit.duration * visit.service.price 
            for visit in visits 
            if visit.service.price is not None and visit.duration is not None
        )
        
        return render_template('report.html', visits=visits, start_date=start_date, end_date=end_date, total_amount=total_amount)

    clients = Client.query.all()
    return render_template('generate_report.html', clients=clients)

@app.route('/view_report', methods=['GET', 'POST'])
def view_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        visits = Visit.query.filter(
            Visit.client_id == client_id,
            Visit.visit_date >= start_date,
            Visit.visit_date <= end_date
        ).all()

        total_amount = sum(
            visit.duration * visit.service.price 
            for visit in visits 
            if visit.service.price is not None and visit.duration is not None
        )
        
        return render_template('report.html', visits=visits, start_date=start_date, end_date=end_date, total_amount=total_amount)

    clients = Client.query.all()
    return render_template('generate_report.html', clients=clients)

@app.route('/client/<int:client_id>/history', methods=['GET'])
@login_required  # Изисква влизане
def client_history(client_id):
    # Зареждане на данни за конкретния клиент
    client = Client.query.get_or_404(client_id)
    
    # Зареждане на всички посещения, свързани с този клиент
    visits = Visit.query.filter_by(client_id=client_id).order_by(Visit.visit_date.desc()).all()
    
    return render_template('client_history.html', client=client, visits=visits)

@app.route('/generate_pdf_report', methods=['GET', 'POST'])
def generate_pdf_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        visits = Visit.query.filter(
            Visit.client_id == client_id,
            Visit.visit_date >= start_date,
            Visit.visit_date <= end_date
        ).all()

        # Път за генерирания PDF
        pdf_file = f'report_{client_id}_{start_date}_{end_date}.pdf'

        # Създаване на PDF файл
        c = canvas.Canvas(pdf_file, pagesize=landscape(letter))
        
        # Регистрация на шрифта
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont('RobotoMono', 'RobotoMono.ttf'))
        c.setFont('RobotoMono', 10)

        # Заглавия на отчета
        c.drawString(100, 550, f"Отчет за клиента с ID: {client_id}")
        c.drawString(100, 535, f"От {start_date} до {end_date}")

        # Заглавия на таблицата
        c.drawString(30, 500, "ID")
        c.drawString(60, 500, "Име на клиента")
        c.drawString(180, 500, "Услуга")
        c.drawString(340, 500, "Време")
        c.drawString(380, 500, "Дата")
        c.drawString(450, 500, "Такса")
        c.drawString(520, 500, "Бележки")

        # Генерирането на редовете за таблицата 
        y_position = 480
        total_amount = 0

        for visit in visits:
            visit_total = visit.duration * visit.service.price if visit.service.price is not None else 0
            total_amount += visit_total
            c.drawString(30, y_position, str(visit.id))
            c.drawString(60, y_position, visit.client.name)
            c.drawString(180, y_position, visit.service.name)
            c.drawString(340, y_position, str(visit.duration))
            c.drawString(380, y_position, visit.visit_date.strftime('%d-%m-%Y'))
            c.drawString(450, y_position, str(round(visit_total, 2)) + " лв")
            c.drawString(520, y_position, visit.notes)

            y_position -= 20  # Преместване надолу за следващия ред

        # Показване на общата сума 
        c.drawString(550, y_position, f"Обща сума: {round(total_amount, 2)} лв.")
        c.save()

        return send_file(pdf_file, as_attachment=True)




@app.route('/generate_sample_data')
def generate_sample_data():
    # Първо, изчистваме текущите данни, ако е необходимо
    db.drop_all()
    db.create_all()

    # Примерни услуги
    services = [
        Service(name="IT Поддръжка", description="Поддръжка на компютри", price=50.0),
        Service(name="Настройка на мрежа", description="Конфигурация на домашна мрежа", price=70.0),
        Service(name="Изграждане на уебсайт", description="Създаване на шоурум уебсайт", price=500.0),
        Service(name="Почистване на компютър", description="Професионално почистване на хардуер", price=30.0),
        Service(name="Инсталация на софтуер", description="Инсталиране и конфигуриране на софтуер", price=40.0),
    ]

    db.session.add_all(services)
    db.session.commit()

    # Примерни клиенти
    clients = []
    for i in range(50):  # Генерираме 50 клиенти
        client = Client(name=f"Клиент {i + 1}", email=f"client{i + 1}@example.com", phone=f"0888{i:04d}")
        clients.append(client)
    db.session.add_all(clients)
    db.session.commit()

    # Примерни посещения, свързани с клиенти и услуги
    visits = []
    visit_date_start = datetime(2024, 1, 1)
    for i in range(50):  # Генерираме 50 посещения
        visit_date = visit_date_start + timedelta(days=i)  # Различни дати
        client = clients[i % len(clients)]  # Взимаме клиент по модул
        service = services[i % len(services)]  # Взимаме услуга по модул
        visit = Visit(client_id=client.id, service_id=service.id, duration=random.uniform(1, 5), 
                      notes=f"Посещение номер {i + 1} - {service.name}", visit_date=visit_date)
        visits.append(visit)

    db.session.add_all(visits)
    db.session.commit()  # Записваме промените
    return "Примерните данни бяха успешно добавени!"

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
