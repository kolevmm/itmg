from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Product, db
from flask_login import login_required

products_bp = Blueprint('products', __name__, url_prefix='/products')

# Маршрут за добавяне на продукт
@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']  # Получаваме стойността за quantity

        new_product = Product(name=name, description=description, price=float(price), quantity=int(quantity))
        db.session.add(new_product)
        db.session.commit()
        flash('Продуктът беше успешно добавен!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('add_product.html')


# Маршрут за списък на продуктите
@products_bp.route('/list')
@login_required
def list_products():
    products = Product.query.all()
    return render_template('list_products.html', products=products)

@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.quantity = request.form['quantity']
        db.session.commit()
        flash('Продуктът беше успешно актуализиран!', 'success')
        return redirect(url_for('products.list_products'))
    
    return render_template('edit_product.html', product=product)


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Продуктът беше успешно изтрит!', 'success')
    return redirect(url_for('products.list_products'))

