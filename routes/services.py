# routes/services.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Service, db  # Импортиране на нужните модели и база данни
from decorators import roles_required  # Импортиране на декоратора за роли

services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')  # Само администратори имат достъп
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        new_service = Service(name=name, description=description, price=float(price))
        db.session.add(new_service)
        db.session.commit()
        flash('Услугата беше успешно добавена!', 'success')
        return redirect(url_for('services.list_services'))

    return render_template('add_service.html')

@services_bp.route('/list')
@login_required
def list_services():
    services = Service.query.all()
    return render_template('list_services.html', services=services)