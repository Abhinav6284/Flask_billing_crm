from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
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


@main_bp.route("/api/reports", methods=['POST'])
@login_required
def get_reports():
    """
    Generate report data based on user filters.
    """
    data = request.get_json()
    report_type = data.get('report_type')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(
            end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except (ValueError, TypeError):
        # Default to today if dates are invalid
        today = datetime.utcnow()
        start_date = today.replace(hour=0, minute=0, second=0)
        end_date = today.replace(hour=23, minute=59, second=59)

    response_data = {}

    if report_type == 'sales':
        # --- Sales Performance & Revenue Trends Data ---
        invoices = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            Invoice.date_issued.between(start_date, end_date)
        ).order_by(Invoice.date_issued).all()

        daily_totals = {}
        for inv in invoices:
            date_key = inv.date_issued.strftime('%Y-%m-%d')
            daily_totals[date_key] = daily_totals.get(
                date_key, 0) + inv.get_total()

        response_data['sales_performance'] = {
            'labels': list(daily_totals.keys()),
            'data': list(daily_totals.values())
        }
        response_data['revenue_trends'] = response_data['sales_performance']

        # --- Customer Growth Data ---
        customers = Customer.query.filter(
            Customer.owner_id == current_user.id,
            Customer.created_at.between(start_date, end_date)
        ).order_by(Customer.created_at).all()

        daily_new_customers = {}
        for cust in customers:
            date_key = cust.created_at.strftime('%Y-%m-%d')
            daily_new_customers[date_key] = daily_new_customers.get(
                date_key, 0) + 1

        # Ensure all dates from sales have a corresponding customer entry (even if zero)
        for date_key in daily_totals.keys():
            if date_key not in daily_new_customers:
                daily_new_customers[date_key] = 0

        # Sort by date
        sorted_dates = sorted(daily_new_customers.keys())

        response_data['customer_growth'] = {
            'labels': sorted_dates,
            'data': [daily_new_customers[d] for d in sorted_dates]
        }

    return jsonify(response_data)
