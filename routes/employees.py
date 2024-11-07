# routes/employees.py

from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_required
from models import Employee, Client, db  # Импортиране на нужните модели и база данни
from decorators import roles_required  # Импортиране на декоратора за роли, ако е необходимо

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')  # Само администратори могат да добавят служители (може да се махне, ако не е нужно)
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        client_id = request.form.get('client_id')  # Избиране на клиент за служителя
        new_employee = Employee(name=name, client_id=client_id)
        db.session.add(new_employee)
        db.session.commit()
        flash('Служителят беше добавен успешно!', 'success')
       # return redirect(url_for('employees.list_employees'))   Пренасочване към списък на служители

    clients = Client.query.all()  # Вземане на всички клиенти за падащото меню
    return render_template('add_employee.html', clients=clients)

@employees_bp.route('/get/<int:client_id>')
def get_employees(client_id):
    employees = Employee.query.filter_by(client_id=client_id).all()  # Получаване на служители по ID на клиент
    return jsonify([{'id': employee.id, 'name': employee.name} for employee in employees])

@employees_bp.route('/delete/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)  # Изтриване на записа
    db.session.commit()  # Записване на промените
    flash('Посещението беше успешно изтрито!', 'success')
    return redirect(url_for('visits.list_visits'))  # Пренасочване към списъка с посещения