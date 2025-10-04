from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ProductForm(FlaskForm):
    name = StringField('Product/Service Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[
                       DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Product')
