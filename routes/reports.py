# routes/reports.py

from flask import Blueprint, render_template, request
from models import Visit, Client
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/generate', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Преобразуване на дати от формуляра
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

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

@reports_bp.route('/view', methods=['GET', 'POST'])
def view_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Преобразуване на дати от формуляра
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

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


@reports_bp.route('/generate_pdf', methods=['GET', 'POST'])
def generate_pdf_report():
    if request.method == 'POST':
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Преобразуване на дати от формуляра
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

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
        pdfmetrics.registerFont(TTFont('RobotoMono', 'RobotoMono.ttf'))
        c.setFont('RobotoMono', 10)

        # Заглавия на отчета
        c.drawString(100, 550, f"Отчет за клиента с ID: {client_id}")
        c.drawString(100, 535, f"От {start_date.date()} до {end_date.date()}")

        # Заглавия на таблицата
        c.drawString(30, 500, "ID")
        c.drawString(60, 500, "Име на клиента")
        c.drawString(180, 500, "Услуга")
        c.drawString(340, 500, "Време")
        c.drawString(380, 500, "Дата")
        c.drawString(450, 500, "Такса")
        c.drawString(520, 500, "Бележки")

        # Генериране на редовете за таблицата 
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
            c.drawString(450, y_position, f"{round(visit_total, 2)} лв")
            c.drawString(520, y_position, visit.notes)

            y_position -= 20  # Преместване надолу за следващия ред

        # Показване на общата сума 
        c.drawString(550, y_position, f"Обща сума: {round(total_amount, 2)} лв.")
        c.save()

        return send_file(pdf_file, as_attachment=True)

    # Получаване на всички клиенти за формуляра
    clients = Client.query.all()
    return render_template('generate_report.html', clients=clients)
