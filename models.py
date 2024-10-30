from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

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