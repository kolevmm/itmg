from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import Client, Employee, Assets, AssetType, Service, db  # Импортиране на нужните модели и база данни
from decorators import roles_required  # Импортирай декоратора, ако е в отделен файл
from datetime import datetime

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

@assets_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        employee_id = request.form.get('employee_id')
        type_id = request.form.get('type_id')
        name = request.form['name']
        net_name = request.form['net_name']
        serial_number = request.form['serial_number']
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        warranty_expiration = datetime.strptime(request.form['warranty_expiration'], '%Y-%m-%d')
        notes = request.form['notes']

        new_asset = Assets(name=name,client_id=client_id, 
                           employee_id=employee_id, type_id=type_id, 
                           net_name=net_name,serial_number=serial_number, 
                           purchase_date=purchase_date, 
                           warranty_expiration=warranty_expiration, notes=notes)
        db.session.add(new_asset)
        db.session.commit()
        flash('Актива беше добавен успешно!', 'success')
        return redirect(url_for('assets.add_asset'))
    clients = Client.query.all()
    employees = Employee.query.all()
    types = AssetType.query.all()
        
    return render_template('add_asset.html', clients=clients, employees=employees, types=types)

@assets_bp.route('/get_employees/<int:client_id>', methods=['GET'])
@login_required
def get_employees(client_id):
    employees = Employee.query.filter_by(client_id=client_id).all()
    return jsonify([{'id': employee.id, 'name': employee.name} for employee in employees])

@assets_bp.route('/add_type', methods=['GET', 'POST'])
def add_asset_type():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        monthly_price = float(request.form.get('monthly_price', 0))
        selected_services = request.form.getlist('services')
 # Проверка дали съществува такъв тип актив
        existing_asset_type = AssetType.query.filter_by(name=name).first()
        if existing_asset_type:
            flash('Тип актив с това име вече съществува!', 'danger')
            return redirect(url_for('assets.add_asset_type'))

        # Създаване на нов тип актив
        new_asset_type = AssetType(name=name, description=description, monthly_maintenance_price=monthly_price)

        # Добавяне на избраните услуги
        if selected_services:
            for service_id in selected_services:
                service = Service.query.get(int(service_id))
                if service:
                    new_asset_type.services.append(service)

        db.session.add(new_asset_type)
        db.session.commit()

        flash('Типът актив е успешно добавен!', 'success')
        return redirect(url_for('assets.add_asset_type'))

    # Зареждане на всички услуги за избор
    services = Service.query.all()
    return render_template('add_asset_type.html', services=services)