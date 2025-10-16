from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class CustomerForm(FlaskForm):
    name = StringField('Full Name/Company Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
                        DataRequired(), Length(min=10, max=20)])
    company = StringField('Company Name', validators=[
                          Optional(), Length(max=100)])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField(
        'State/Province', validators=[Optional(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[
                              Optional(), Length(max=10)])
    country = StringField('Country', validators=[
                          Optional(), Length(max=50)], default='India')
    tax_number = StringField(
        'Tax/GST Number', validators=[Optional(), Length(max=20)])
    customer_type = SelectField('Customer Type', choices=[
        ('individual', 'Individual'),
        ('business', 'Business')
    ], default='individual')
    status = SelectField('Status', choices=[
                         ('active', 'Active'), ('inactive', 'Inactive')], default='active')
    submit = SubmitField('Save Customer')
