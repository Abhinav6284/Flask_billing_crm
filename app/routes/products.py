from flask import Blueprint, jsonify, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from extensions import db
from app.models.product import Product
from app.forms.product_forms import ProductForm
import io
import csv
from flask import Response

products_bp = Blueprint('products', __name__)


@products_bp.route("/")
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(
        owner_id=current_user.id).paginate(page=page, per_page=10)
    return render_template('products/products.html', products=products, title='Products & Services')


@products_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data,
                          price=form.price.data, owner_id=current_user.id)
        db.session.add(product)
        db.session.commit()
        flash('Your product/service has been created!', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/product_form.html', title='New Product', form=form, legend='New Product/Service')


@products_bp.route("/<int:product_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner_id != current_user.id:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        db.session.commit()
        flash('Your product/service has been updated!', 'success')
        return redirect(url_for('products.list_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
    return render_template('products/product_form.html', title='Edit Product', form=form, legend='Edit Product/Service')


@products_bp.route("/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner_id != current_user.id:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product/service has been deleted!', 'success')
    return redirect(url_for('products.list_products'))


@products_bp.route("/api/products")
@login_required
def api_products():
    products = Product.query.filter_by(owner_id=current_user.id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': float(p.price),
        'category': getattr(p, 'category', 'General')
    } for p in products])


@products_bp.route("/api/new", methods=['POST'])
@login_required
def api_new_product():
    data = request.get_json()
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        owner_id=current_user.id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Product created successfully!'})


@products_bp.route("/export/csv")
@login_required
def export_products_csv():
    products = Product.query.filter_by(owner_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['ID', 'Name', 'Description', 'Price',
                    'Category', 'Stock', 'Status'])

    # Write data
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.description,
            product.price,
            product.category,
            product.stock_quantity,
            product.status
        ])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=products.csv"}
    )
