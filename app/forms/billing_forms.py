from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, FloatField, FieldList, FormField, HiddenField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange


class InvoiceItemForm(FlaskForm):
    # This subform is used within the InvoiceForm
    product_id = SelectField('Product', coerce=int,
                             validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
                            DataRequired(), NumberRange(min=1)], default=1)
    price = HiddenField('Price')  # Price will be populated via JS
    # NEW: Item-specific discount and tax fields
    discount = FloatField('Discount (%)', default=0.0, validators=[
                          NumberRange(min=0, max=100)])
    tax = FloatField('Tax (%)', default=0.0, validators=[
                     NumberRange(min=0, max=100)])


class InvoiceForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int,
                              validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d',
                         validators=[Optional()])
    status = SelectField('Status', choices=[(
        'Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Overdue', 'Overdue')], validators=[DataRequired()])
    # Note: We removed the overall discount and tax fields from this form
    items = FieldList(FormField(InvoiceItemForm), min_entries=1)
    submit = SubmitField('Create Invoice')
