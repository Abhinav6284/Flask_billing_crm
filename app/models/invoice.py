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
                         # Price at the time of invoice creation
                         db.Column('price', db.Float, nullable=False)
                         )


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    date_issued = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False,
                       default='Unpaid')  # Paid, Unpaid, Overdue
    discount = db.Column(db.Float, nullable=False, default=0.0)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    items = db.relationship('Product', secondary=invoice_items, lazy='subquery',
                            backref=db.backref('invoices', lazy=True))

    def get_total(self):
        total = 0
        invoice_item_details = db.session.query(
            invoice_items).filter_by(invoice_id=self.id).all()
        for item in invoice_item_details:
            total += item.price * item.quantity

        # Apply discount
        total_after_discount = total * (1 - self.discount / 100)
        return round(total_after_discount, 2)

    def __repr__(self):
        return f"Invoice('{self.invoice_number}', Status: '{self.status}')"
