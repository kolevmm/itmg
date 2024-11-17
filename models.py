from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id', name='fk_service_category'), nullable=False)
    category = db.relationship('ServiceCategory', back_populates='services')

ServiceCategory = db.relationship('Service', back_populates='category')

# Мождел за категории на услуги
class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Модел за клиенти
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vat = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(100), nullable=True)
    mol = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)  # Опционално поле за имейл
    phone = db.Column(db.String(15), nullable=True)  # Опционално поле за телефон

    visits = db.relationship('Visit', backref='client', lazy=True)  # Връзка към Visit

class Employee(db.Model):  # Модел за служители
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)  # Свързано с клиента
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

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Product {self.name} - {self.price} BGN>'


# Модел Settings - за глобални параметри
class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    offer_validity = db.Column(db.Integer, nullable=False, default=30)
    tax_rate = db.Column(db.Float, nullable=False, default=20.0)
    payment_terms = db.Column(db.String(255), nullable=False, default="Стандартни условия")

# Модел CompanyInfo - за информацията за фирмата
class CompanyInfo(db.Model):
    __tablename__ = 'company_info'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    tax_number = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    # Свързване на CompanyInfo с BankAccount - една фирма може да има много банкови сметки
    bank_accounts = db.relationship('BankAccount', backref='company', lazy=True)

# Модел BankAccount - за банковите сметки
class BankAccount(db.Model):
    __tablename__ = 'bank_account'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    iban = db.Column(db.String(34), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company_info.id'), nullable=False)

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validity_days = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(50), nullable=False, default="draft")
    total_price = db.Column(db.Float, nullable=True)

    client = db.relationship("Client", backref="offers")
    products = db.relationship("OfferProduct", back_populates="offer")
    services = db.relationship("OfferService", back_populates="offer")

    def formatted_id(self):
        return str(self.id).zfill(5)
class OfferProduct(db.Model):
    __tablename__ = 'offer_products'
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    offer = db.relationship("Offer", back_populates="products")
    product = db.relationship("Product")

class OfferService(db.Model):
    __tablename__ = 'offer_services'
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    offer = db.relationship("Offer", back_populates="services")
    service = db.relationship("Service")

class AssetType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Име на вида (напр. Лаптоп, Принтер)
    description = db.Column(db.Text, nullable=True)
    monthly_maintenance_price = db.Column(db.Float, nullable=False)
    services = db.relationship('Service', secondary='asset_type_services', backref='asset_types')

    asset_type_services = db.Table(
    'asset_type_services',
    db.Column('asset_type_id', db.Integer, db.ForeignKey('asset_type.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)
class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Клиент, към когото е свързан активът
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # Назначен служител
    type_id = db.Column(db.Integer, db.ForeignKey('asset_type.id'), nullable=False)  # Вид на актива (напр. Лаптоп)
    
    name = db.Column(db.String(100), nullable=False)  # Име на актива
    net_name = db.Column(db.String(50), nullable=True) # Име на актива в мрежата
    serial_number = db.Column(db.String(50), nullable=True)  # Сериен номер
    purchase_date = db.Column(db.Date, nullable=True)  # Дата на закупуване
    warranty_expiration = db.Column(db.Date, nullable=True)  # Изтичане на гаранцията
    notes = db.Column(db.String(255), nullable=True)  # Бележки
    
    client = db.relationship('Client', backref='assets')
    employee = db.relationship('Employee', backref='assigned_assets')  # Връзка със служителя
    type = db.relationship('AssetType', backref='assets')  # Връзка с вида на актива

class MaintenanceOffer(db.Model):
    __tablename__ = 'maintenance_offers'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validity_days = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(50), nullable=False, default="draft")
    total_price = db.Column(db.Float, nullable=True)

    client = db.relationship("Client", backref="maintenance_offers")
    assets = db.relationship("MaintenanceOfferAsset", back_populates="maintenance_offer")
    custom_fields = db.relationship("MaintenanceOfferCustomField", back_populates="maintenance_offer")
    def formatted_id(self):
        return str(self.id).zfill(5)

class MaintenanceOfferAsset(db.Model):
    __tablename__ = 'maintenance_offer_assets'
    id = db.Column(db.Integer, primary_key=True)
    maintenance_offer_id = db.Column(db.Integer, db.ForeignKey('maintenance_offers.id'), nullable=False)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_type.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
  # Свързана услуга

    maintenance_offer = db.relationship("MaintenanceOffer", back_populates="assets")
    asset_type = db.relationship("AssetType")
    service = db.relationship("Service")  # Връзка с услугата

    def calculate_total_price(self):
        # This calculates the maintenance cost for this asset type in the offer
        return self.quantity * self.asset_type.monthly_maintenance_price

class MaintenanceOfferCustomField(db.Model):
    __tablename__ = 'maintenance_offer_custom_fields'
    id = db.Column(db.Integer, primary_key=True)
    maintenance_offer_id = db.Column(db.Integer, db.ForeignKey('maintenance_offers.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)

    maintenance_offer = db.relationship("MaintenanceOffer", back_populates="custom_fields")