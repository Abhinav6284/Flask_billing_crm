from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from extensions import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.invoice import Invoice

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    return render_template('landing.html')


@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        # CORRECTED QUERY: Use user_id for invoices and owner_id for others
        user_invoices = Invoice.query.filter_by(user_id=current_user.id).all()

        stats = {
            'total_customers': Customer.query.filter_by(owner_id=current_user.id).count(),
            'total_products': Product.query.filter_by(owner_id=current_user.id).count(),
            'total_invoices': len(user_invoices),
            'total_revenue': sum(invoice.get_total() for invoice in user_invoices)
        }

        recent_invoices = Invoice.query.filter_by(user_id=current_user.id)\
            .order_by(Invoice.date_issued.desc()).limit(5).all()
        recent_customers = Customer.query.filter_by(owner_id=current_user.id)\
            .order_by(Customer.id.desc()).limit(5).all()
    except Exception as e:
        print(f"Error calculating dashboard stats: {e}")  # For debugging
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
    customers = Customer.query.filter_by(owner_id=current_user.id).all()
    products = Product.query.filter_by(owner_id=current_user.id).all()
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        'customers': [{
            'id': c.id, 'name': c.name, 'email': c.email, 'phone': c.phone,
            'customer_type': c.customer_type, 'status': c.status
        } for c in customers],
        'products': [{
            'id': p.id, 'name': p.name, 'category': p.category, 'price': float(p.price),
            'stock_quantity': p.stock_quantity, 'sku': p.sku, 'status': p.status
        } for p in products],
        'invoices': [{
            'id': i.id, 'invoice_number': i.invoice_number, 'customer': i.customer.name,
            'date_issued': i.date_issued.strftime('%Y-%m-%d'),
            'due_date': i.due_date.strftime('%Y-%m-%d') if i.due_date else 'N/A',
            'status': i.status, 'total': float(i.get_total())
        } for i in invoices]
    })
