from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Offer, OfferProduct, OfferService, Client, Product, Service
from flask_login import login_required

offers_bp = Blueprint('offers', __name__, url_prefix='/offers')

# Route за добавяне на оферта
@offers_bp.route('/add', methods=['GET', 'POST'])
def add_offer():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        status = request.form.get('status')  # Получаваме статуса от формата

        # Изчисляваме общата сума на базата на продуктите и услугите
        total_price = 0
        products = request.form.getlist('products[]')
        product_quantities = request.form.getlist('product_quantities[]')
        for product_id, quantity in zip(products, product_quantities):
            product = Product.query.get(int(product_id))
            if product:
                total_price += product.price * int(quantity)

        services = request.form.getlist('services[]')
        service_ids = [int(service_id) for service_id in services if service_id]  # Пропусни празните стойности
        service_hours = request.form.getlist('service_hours[]')
        for service_id, hours in zip(services, service_hours):
            service = Service.query.get(int(service_id))
            if service:
                total_price += service.price * int(hours)

        # Създаваме новата оферта с правилния статус и обща сума
        new_offer = Offer(
            client_id=client_id,
            validity_days=30,  # Можеш да го вземеш от настройките, ако е дефинирано
            status=status,
            total_price=total_price
        )
        
        db.session.add(new_offer)
        db.session.commit()

        # Добавяне на свързаните продукти и услуги към офертата
        for product_id, quantity in zip(products, product_quantities):
            offer_product = OfferProduct(offer_id=new_offer.id, product_id=int(product_id), quantity=int(quantity))
            db.session.add(offer_product)

        for service_id, hours in zip(services, service_hours):
            offer_service = OfferService(offer_id=new_offer.id, service_id=int(service_id), quantity=int(hours))
            db.session.add(offer_service)

        db.session.commit()
        flash('Офертата е успешно добавена!', 'success')
        return redirect(url_for('offers.list_offers'))

    clients = Client.query.all()
    products = Product.query.all()
    services = Service.query.all()
    return render_template('add_offer.html', clients=clients, products=products, services=services)



@offers_bp.route('/list', methods=['GET'])
def list_offers():
    # Извличане на всички оферти от базата данни
    offers = Offer.query.all()
    
    # Рендиране на шаблона и предаване на офертите към него
    return render_template('list_offers.html', offers=offers)

@offers_bp.route('/view/<int:offer_id>', methods=['GET'])
@login_required
def view_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    return render_template('view_offer.html', offer=offer)

@offers_bp.route('/delete/<int:offer_id>', methods=['GET', 'POST'])
@login_required
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)

    try:
        # Изтрий свързаните записи в offer_services
        OfferService.query.filter_by(offer_id=offer.id).delete()

        # Изтрий свързаните записи в offer_products, ако също съществуват
        OfferProduct.query.filter_by(offer_id=offer.id).delete()

        # Изтрий самата оферта
        db.session.delete(offer)
        db.session.commit()

        flash('Офертата беше успешно изтрита!', 'success')

    except Exception as e:
        db.session.rollback()  # Връщане назад на транзакцията при грешка
        flash(f'Грешка при изтриването на офертата: {str(e)}', 'danger')

    return redirect(url_for('offers.list_offers'))



