from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from extensions import db
from app.models.customer import Customer
from app.forms.crm_forms import CustomerForm

crm_bp = Blueprint('crm', __name__)


@crm_bp.route("/")
@login_required
def list_customers():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.filter_by(
        owner=current_user).paginate(page=page, per_page=10)
    return render_template('crm/customers.html', customers=customers, title='Customers')


@crm_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, email=form.email.data,
                            phone=form.phone.data, address=form.address.data, owner=current_user)
        db.session.add(customer)
        db.session.commit()
        flash('Customer has been created!', 'success')
        return redirect(url_for('crm.list_customers'))
    return render_template('crm/customer_form.html', title='New Customer', form=form, legend='New Customer')


@crm_bp.route("/<int:customer_id>")
@login_required
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.owner != current_user:
        abort(403)
    return render_template('crm/customer_detail.html', title=customer.name, customer=customer)


@crm_bp.route("/<int:customer_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.owner != current_user:
        abort(403)
    form = CustomerForm()
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        db.session.commit()
        flash('Customer has been updated!', 'success')
        return redirect(url_for('crm.list_customers'))
    elif request.method == 'GET':
        form.name.data = customer.name
        form.email.data = customer.email
        form.phone.data = customer.phone
        form.address.data = customer.address
    return render_template('crm/customer_form.html', title='Edit Customer', form=form, legend='Edit Customer')


@crm_bp.route("/<int:customer_id>/delete", methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.owner != current_user:
        abort(403)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer has been deleted!', 'success')
    return redirect(url_for('crm.list_customers'))
