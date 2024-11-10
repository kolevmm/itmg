from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, MaintenanceOffer, MaintenanceOfferAsset, Client, AssetType
from flask_login import login_required

maintenance_offers_bp = Blueprint('maintenance_offers', __name__, url_prefix='/maintenance_offers')

# Route for adding a maintenance offer
@maintenance_offers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_maintenance_offer():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        status = request.form.get('status', 'draft')

        # Start calculating the total maintenance cost
        total_price = 0
        assets = request.form.getlist('assets[]')
        asset_quantities = request.form.getlist('asset_quantities[]')

        # Create the new maintenance offer
        new_offer = MaintenanceOffer(client_id=client_id, status=status, validity_days=30)

        db.session.add(new_offer)
        db.session.commit()  # Commit here to get the offer ID for associated assets

        # Add selected assets to the offer
        for asset_type_id, quantity in zip(assets, asset_quantities):
            asset_type = AssetType.query.get(int(asset_type_id))
            if asset_type:
                quantity = int(quantity)
                total_price += asset_type.monthly_maintenance_price * quantity

                offer_asset = MaintenanceOfferAsset(
                    maintenance_offer_id=new_offer.id,
                    asset_type_id=asset_type.id,
                    quantity=quantity
                )
                db.session.add(offer_asset)

        # Update total price and save the maintenance offer
        new_offer.total_price = total_price
        db.session.commit()
        
        flash('Офертата за поддръжка е успешно добавена!', 'success')
        return redirect(url_for('maintenance_offers.add_maintenance_offer'))

    # Load clients and asset types for the form
    clients = Client.query.all()
    asset_types = AssetType.query.all()
    return render_template('add_maintenance_offer.html', clients=clients, asset_types=asset_types)

@maintenance_offers_bp.route('/view_maintenance_offer/<int:offer_id>', methods=['GET'])
@login_required
def view_maintenance_offer(offer_id):
    # Логика за преглед на оферта за поддръжка
    maintenance_offer = MaintenanceOffer.query.get_or_404(offer_id)
    return render_template('view_maintenance_offer.html', offer=maintenance_offer)
