from extensions import db


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(50), default='India')
    tax_number = db.Column(db.String(20), nullable=True)  # GST/Tax ID
    customer_type = db.Column(
        db.String(20), default='individual')  # individual/business
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invoices = db.relationship('Invoice', backref='customer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.name}', '{self.email}')"
