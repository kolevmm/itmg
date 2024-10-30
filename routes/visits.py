# routes/visits.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Visit, Client, Service, Employee, db
from datetime import datetime

visits_bp = Blueprint('visits', __name__, url_prefix='/visits')

@visits_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_visit():
    if request.method == 'POST':
        client_id = request.form['client_id']
        service_id = request.form['service_id']
        employee_id = request.form.get('employee_id')
        duration = request.form['duration']
        notes = request.form['notes']
        visit_date = request.form['visit_date']
        
        new_visit = Visit(
            client_id=client_id,
            service_id=service_id,
            duration=float(duration),
            notes=notes,
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d'),
            employee_id=employee_id
        )
        
        db.session.add(new_visit)
        db.session.commit()
        flash('Посещението беше успешно добавено!', 'success')
        return redirect(url_for('visits.list_visits'))  # Пренасочване към списъка с посещения

    clients = Client.query.all()
    services = Service.query.all()
    employees = Employee.query.all()
    return render_template('add_visit.html', clients=clients, services=services, employees=employees)

@visits_bp.route('/list')
@login_required
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

@visits_bp.route('/edit/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)

    if request.method == 'POST':
        visit.client_id = request.form['client_id']
        visit.service_id = request.form['service_id']
        visit.duration = request.form['duration']
        visit.notes = request.form['notes']
        visit.visit_date = datetime.strptime(request.form['visit_date'], '%Y-%m-%d')

        db.session.commit()
        flash('Посещението беше успешно актуализирано!', 'success')
        return redirect(url_for('visits.list_visits'))

    services = Service.query.all()
    return render_template('edit_visit.html', visit=visit, services=services)

@visits_bp.route('/delete/<int:visit_id>', methods=['POST'])
@login_required
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)  # Извличане на посещение по ID
    db.session.delete(visit)  # Изтриване на записа
    db.session.commit()  # Записване на промените
    flash('Посещението беше успешно изтрито!', 'success')
    return redirect(url_for('visits.list_visits'))  # Пренасочване към списъка с посещения