from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class StockTickerForm(FlaskForm):
    ticker = StringField('Stock Ticker',
                         validators=[DataRequired(), Regexp(
                             '^[A-Z]{1,5}$', message="Invalid ticker symbol.")],
                         render_kw={"placeholder": "e.g., AAPL"})
    submit = SubmitField('Track')
