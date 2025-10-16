from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # product/service/digital/etc
    category = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(20), nullable=True)  # piece, kg, hour, etc
    stock_quantity = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), nullable=True)  # Product code
    tax_rate = db.Column(db.Numeric(5, 2), default=18.0)  # Tax percentage
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"
