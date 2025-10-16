from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, current_app
from flask_login import login_required, current_user
from extensions import db
import requests

# Import all required models
from app.models.customer import Customer
from app.models.product import Product
from app.models.invoice import Invoice
from app.forms.dashboard_forms import StockTickerForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    return render_template('landing.html')


@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        stats = {
            'total_customers': Customer.query.filter_by(owner=current_user).count(),
            'total_products': Product.query.filter_by(owner=current_user).count(),
            'total_invoices': Invoice.query.filter_by(user_id=current_user.id).count(),
            'total_revenue': 0
        }

        invoices = Invoice.query.filter_by(user_id=current_user.id).all()
        stats['total_revenue'] = sum(invoice.get_total()
                                     for invoice in invoices)

        recent_invoices = Invoice.query.filter_by(user_id=current_user.id)\
            .order_by(Invoice.date_issued.desc()).limit(5).all()
        recent_customers = Customer.query.filter_by(owner=current_user)\
            .order_by(Customer.id.desc()).limit(5).all()
    except:
        stats = {'total_customers': 0, 'total_products': 0,
                 'total_invoices': 0, 'total_revenue': 0}
        recent_invoices = []
        recent_customers = []

    return render_template('dashboard/dashboard_modern.html',
                           stats=stats,
                           recent_invoices=recent_invoices,
                           recent_customers=recent_customers)


@main_bp.route("/api/dashboard_data")
@login_required
def dashboard_data():
    customers = Customer.query.filter_by(owner=current_user).all()
    products = Product.query.filter_by(owner=current_user).all()
    invoices = Invoice.query.filter_by(owner=current_user).all()

    return jsonify({
        'customers': [{'id': c.id, 'name': c.name, 'email': c.email, 'phone': c.phone} for c in customers],
        'products': [{'id': p.id, 'name': p.name, 'description': p.description, 'price': float(p.price)} for p in products],
        'invoices': [{'id': i.id, 'invoice_number': i.invoice_number, 'customer': i.customer.name,
                     'date_issued': i.date_issued.strftime('%Y-%m-%d'), 'status': i.status,
                      'total': float(i.get_total())} for i in invoices]
    })
