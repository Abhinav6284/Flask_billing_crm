from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class ProductForm(FlaskForm):
    name = StringField('Product/Service Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    price = DecimalField('Price (₹)', validators=[
                         DataRequired(), NumberRange(min=0.01)], places=2)
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('product', 'Product'),
        ('service', 'Service'),
        ('digital', 'Digital Product'),
        ('subscription', 'Subscription'),
        ('consulting', 'Consulting'),
        ('other', 'Other')
    ], validators=[Optional()])
    unit = StringField('Unit (e.g., piece, kg, hour)',
                       validators=[Optional(), Length(max=20)])
    stock_quantity = IntegerField('Stock Quantity', validators=[
                                  Optional(), NumberRange(min=0)], default=0)
    sku = StringField('SKU/Product Code',
                      validators=[Optional(), Length(max=50)])
    tax_rate = DecimalField('Tax Rate (%)', validators=[
                            Optional(), NumberRange(min=0, max=100)], places=2, default=18.0)
    status = SelectField('Status', choices=[
                         ('active', 'Active'), ('inactive', 'Inactive')], default='active')
    submit = SubmitField('Save Product')
