from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Client, db, Visit  # Импортиране на нужните модели и база данни
from decorators import roles_required  # Импортирай декоратора, ако е в отделен файл

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        vat = request.form['vat']
        address = request.form['address']
        mol = request.form['mol']
        email = request.form['email']
        phone = request.form['phone']
        new_client = Client(name=name, vat=vat, address=address, mol=mol, email=email, phone=phone)
        db.session.add(new_client)
        db.session.commit()
        flash('Клиентът беше добавен успешно!', 'success')
        return redirect(url_for('clients.list_clients'))
    return render_template('add_client.html')

@clients_bp.route('/list')
@login_required
def list_clients():
    clients = Client.query.all()  # Извлича всички клиенти от базата данни
    return render_template('list_clients.html', clients=clients)

@clients_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)

    if request.method == 'POST':
        client.name = request.form['name']
        client.vat = request.form['vat']
        client.address = request.form['address']
        client.mol = request.form['mol']
        client.email = request.form['email']
        client.phone = request.form['phone']
        
        db.session.commit()
        flash('Клиентът беше успешно актуализиран!', 'success')
        return redirect(url_for('clients.list_clients'))  # Пренасочване към списъка с клиенти

    return render_template('edit_client.html', client=client)

@clients_bp.route('/delete/<int:client_id>', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    # Първо изтрийте свързаните посещения
    Visit.query.filter_by(client_id=client.id).delete()
    db.session.delete(client)
    db.session.commit()
    flash('Клиентът беше успешно изтрит!', 'success')
    return redirect(url_for('clients.list_clients'))  # Пренасочване към списъка с клиенти

@clients_bp.route('/<int:client_id>/history', methods=['GET'])
@login_required
def client_history(client_id):
    # Зареждане на данни за конкретния клиент
    client = Client.query.get_or_404(client_id)
    
    # Зареждане на всички посещения, свързани с този клиент
    visits = Visit.query.filter_by(client_id=client_id).order_by(Visit.visit_date.desc()).all()
    
    return render_template('client_history.html', client=client, visits=visits)