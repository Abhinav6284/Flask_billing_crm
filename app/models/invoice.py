from extensions import db
from datetime import datetime

# Association table for many-to-many relationship between Invoice and Product
invoice_items = db.Table('invoice_items',
                         db.Column('invoice_id', db.Integer, db.ForeignKey(
                             'invoice.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey(
                             'product.id'), primary_key=True),
                         db.Column('quantity', db.Integer,
                                   nullable=False, default=1),
                         # Price at time of invoice
                         db.Column('price', db.Float, nullable=False),
                         # NEW: Item-specific discount and tax
                         db.Column('discount', db.Float,
                                   nullable=False, default=0.0),
                         db.Column('tax', db.Float,
                                   nullable=False, default=0.0)
                         )


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    date_issued = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False,
                       default='Unpaid')
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Note: We removed the overall discount and tax columns from this model

    items = db.relationship('Product', secondary=invoice_items, lazy='subquery',
                            backref=db.backref('invoices', lazy=True))

    def get_total(self):
        total = 0
        # Query the association table directly to get all details
        invoice_item_details = db.session.query(
            invoice_items).filter_by(invoice_id=self.id).all()

        for item in invoice_item_details:
            # Calculate total for each line item
            base_price = item.price * item.quantity
            price_after_discount = base_price * (1 - item.discount / 100)
            final_price = price_after_discount * (1 + item.tax / 100)
            total += final_price

        return round(total, 2)

    def __repr__(self):
        return f"Invoice('{self.invoice_number}', Status: '{self.status}')"
