from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, Response
from flask_login import login_required, current_user
from extensions import db
from app.models.invoice import Invoice, invoice_items
from app.models.customer import Customer
from app.models.product import Product
from app.forms.billing_forms import InvoiceForm
import weasyprint
import uuid
from sqlalchemy import text

billing_bp = Blueprint('billing', __name__)


def generate_invoice_number():
    return str(uuid.uuid4().hex[:8]).upper()


@billing_bp.route("/")
@login_required
def list_invoices():
    page = request.args.get('page', 1, type=int)
    invoices = Invoice.query.filter_by(owner=current_user).order_by(
        Invoice.date_issued.desc()).paginate(page=page, per_page=10)
    return render_template('billing/invoices.html', invoices=invoices, title='Invoices')


@billing_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_invoice():
    form = InvoiceForm()
    customers = Customer.query.filter_by(owner=current_user).all()
    products = Product.query.filter_by(owner=current_user).all()
    form.customer_id.choices = [(c.id, c.name) for c in customers]
    for item_form in form.items:
        item_form.product_id.choices = [
            (p.id, f"{p.name} - ${p.price:.2f}") for p in products]

    if form.validate_on_submit():
        # Create the main invoice (without discount/tax)
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            customer_id=form.customer_id.data,
            due_date=form.due_date.data,
            status=form.status.data,
            owner=current_user
        )
        db.session.add(invoice)
        db.session.flush()  # Flush to get the invoice ID

        # Add items to the invoice
        for item_data in form.items.data:
            product = Product.query.get(item_data['product_id'])
            if product:
                insert_stmt = invoice_items.insert().values(
                    invoice_id=invoice.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    price=product.price,
                    discount=item_data['discount'],  # <-- ADD THIS
                    tax=item_data['tax']            # <-- AND THIS
                )
                db.session.execute(insert_stmt)

        db.session.commit()
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('billing.list_invoices'))

    # Pass products data to template for JavaScript
    product_prices = {p.id: p.price for p in products}

    return render_template(
        'billing/create_invoice.html',
        title='New Invoice',
        form=form,
        legend='New Invoice',
        product_prices=product_prices
    )


@billing_bp.route("/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.owner != current_user:
        abort(403)

    # Manually fetch items with quantity and stored price
    query = text("""
        SELECT p.name, ii.quantity, ii.price
        FROM invoice_items AS ii
        JOIN product AS p ON ii.product_id = p.id
        WHERE ii.invoice_id = :invoice_id
    """)
    invoice_items_details = db.session.execute(
        query, {'invoice_id': invoice.id}).fetchall()

    return render_template('billing/view_invoice.html', title=f"Invoice {invoice.invoice_number}", invoice=invoice, items=invoice_items_details)


@billing_bp.route("/<int:invoice_id>/download")
@login_required
def download_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.owner != current_user:
        abort(403)

    query = text("""
        SELECT p.name, ii.quantity, ii.price
        FROM invoice_items AS ii
        JOIN product AS p ON ii.product_id = p.id
        WHERE ii.invoice_id = :invoice_id
    """)
    invoice_items_details = db.session.execute(
        query, {'invoice_id': invoice.id}).fetchall()

    rendered_html = render_template(
        'billing/invoice_pdf.html', invoice=invoice, items=invoice_items_details)
    pdf = weasyprint.HTML(string=rendered_html).write_pdf()

    return Response(pdf, mimetype='application/pdf', headers={
        'Content-Disposition': f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
    })
