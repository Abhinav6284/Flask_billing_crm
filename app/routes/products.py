from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from extensions import db
from app.models.product import Product
from app.forms.product_forms import ProductForm

products_bp = Blueprint('products', __name__)


@products_bp.route("/")
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(
        owner=current_user).paginate(page=page, per_page=10)
    return render_template('products/products.html', products=products, title='Products & Services')


@products_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data,
                          price=form.price.data, owner=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Your product/service has been created!', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/product_form.html', title='New Product', form=form, legend='New Product/Service')


@products_bp.route("/<int:product_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner != current_user:
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
    if product.owner != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product/service has been deleted!', 'success')
    return redirect(url_for('products.list_products'))
