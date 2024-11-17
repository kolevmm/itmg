from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, MaintenanceOffer, MaintenanceOfferAsset, Client, AssetType, MaintenanceOfferCustomField, CompanyInfo, Service
from flask_login import login_required
from datetime import timedelta
from sqlalchemy.orm import joinedload

maintenance_offers_bp = Blueprint('maintenance_offers', __name__, url_prefix='/maintenance_offers')

# Route for adding a maintenance offer
@maintenance_offers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_maintenance_offer():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        status = request.form.get('status', 'draft')

        # Initialize total price
        total_price = 0

        # Process assets and services
        assets = request.form.getlist('assets[]')
        asset_quantities = request.form.getlist('asset_quantities[]')
        asset_services = request.form.getlist('asset_services[]')  # Selected services for each asset

        # Create the maintenance offer
        new_offer = MaintenanceOffer(client_id=client_id, status=status, validity_days=30)
        db.session.add(new_offer)
        db.session.commit()  # Commit to get the new offer ID

        for asset_type_id, quantity, service_id in zip(assets, asset_quantities, asset_services):
            asset_type = AssetType.query.get(int(asset_type_id))
            service = Service.query.get(int(service_id)) if service_id else None  # Get selected service
            if asset_type:
                quantity = int(quantity)
                total_price += asset_type.monthly_maintenance_price * quantity

                # Add the asset with selected service to the offer
                offer_asset = MaintenanceOfferAsset(
                    maintenance_offer_id=new_offer.id,
                    asset_type_id=asset_type.id,
                    quantity=quantity,
                    service_id=service.id if service else None
                )
                db.session.add(offer_asset)

        # Process custom fields
        custom_names = request.form.getlist('custom_names[]')
        custom_quantities = request.form.getlist('custom_quantities[]')
        custom_prices = request.form.getlist('custom_prices[]')

        for name, quantity, price in zip(custom_names, custom_quantities, custom_prices):
            if name.strip() and quantity and price:
                total = float(quantity) * float(price)
                total_price += total
                db.session.add(MaintenanceOfferCustomField(
                    maintenance_offer_id=new_offer.id,
                    name=name.strip(),
                    quantity=int(quantity),
                    price=float(price),
                    total=total
                ))

        # Update total price for the offer
        new_offer.total_price = total_price
        db.session.commit()

        flash('Офертата за поддръжка е успешно добавена!', 'success')
        return redirect(url_for('maintenance_offers.add_maintenance_offer'))

    # Load asset types with their services for the form
    asset_types = AssetType.query.options(joinedload(AssetType.services)).all()
    serialized_asset_types = []
    for asset_type in asset_types:
        serialized_asset_types.append({
            "id": asset_type.id,
            "name": asset_type.name,
            "monthly_maintenance_price": asset_type.monthly_maintenance_price,
            "services": [{"id": service.id, "name": service.name} for service in asset_type.services]
        })

    # Load clients for the form
    clients = Client.query.all()
    return render_template('add_maintenance_offer.html', clients=clients, asset_types=serialized_asset_types)




@maintenance_offers_bp.route('/template/<int:offer_id>', methods=['GET'])
@login_required
def template(offer_id):
    # Намери офертата за поддръжка
    maintenance_offer = MaintenanceOffer.query.get_or_404(offer_id)
    company_info = CompanyInfo.query.first()  # Вземаме информацията за фирмата
    validity_date = maintenance_offer.created_at + timedelta(days=maintenance_offer.validity_days)
   # Изчисления за общо, ДДС и крайна сума
    total = maintenance_offer.total_price or 0  # Общата сума
    vat_rate = 0.20  # Процент на ДДС (20%)
    vat_amount = round(total * vat_rate, 2)
    total_with_vat = round(total + vat_amount, 2)

    return render_template(
        'maintenance_offer_template.html',
        offer=maintenance_offer,
        validity_date=validity_date,
        total=total,
        vat_amount=vat_amount,
        total_with_vat=total_with_vat,
        company=company_info
    )


@maintenance_offers_bp.route('/edit/<int:offer_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance_offer(offer_id):
    offer = MaintenanceOffer.query.get_or_404(offer_id)

    if request.method == 'POST':
        # Обновяване на статус
        offer.status = request.form.get('status', offer.status)

        # Обновяване на активи
        db.session.query(MaintenanceOfferAsset).filter_by(maintenance_offer_id=offer.id).delete()
        assets = request.form.getlist('assets[]')
        asset_quantities = request.form.getlist('asset_quantities[]')
        for asset_id, quantity in zip(assets, asset_quantities):
            asset_type = AssetType.query.get(int(asset_id))
            if asset_type:
                offer_asset = MaintenanceOfferAsset(
                    maintenance_offer_id=offer.id,
                    asset_type_id=asset_type.id,
                    quantity=int(quantity)
                )
                db.session.add(offer_asset)

        # Обновяване на къстъм полета
        db.session.query(MaintenanceOfferCustomField).filter_by(maintenance_offer_id=offer.id).delete()
        custom_names = request.form.getlist('custom_names[]')
        custom_quantities = request.form.getlist('custom_quantities[]')
        custom_prices = request.form.getlist('custom_prices[]')
        for name, quantity, price in zip(custom_names, custom_quantities, custom_prices):
            quantity = int(quantity)
            price = float(price)
            total = quantity * price
            custom_field = MaintenanceOfferCustomField(
                maintenance_offer_id=offer.id,
                name=name,
                quantity=quantity,
                price=price,
                total=total
            )
            db.session.add(custom_field)

        # Обновяване на общата цена
        total_price = sum(
            asset.quantity * asset.asset_type.monthly_maintenance_price
            for asset in offer.assets
        )
        total_price += sum(
            field.total for field in offer.custom_fields
        )
        offer.total_price = total_price

        db.session.commit()
        flash('Офертата за поддръжка е успешно редактирана!', 'success')
        return redirect(url_for('offers.list_offers'))

    # Зареждане на данните за офертата
    assets = MaintenanceOfferAsset.query.filter_by(maintenance_offer_id=offer.id).all()
    custom_fields = MaintenanceOfferCustomField.query.filter_by(maintenance_offer_id=offer.id).all()
    asset_types = AssetType.query.all()
    return render_template(
        'edit_maintenance_offer.html',
        offer=offer,
        assets=assets,
        custom_fields=custom_fields,
        asset_types=asset_types
    )
