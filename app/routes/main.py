from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, current_app
from flask_login import login_required, current_user
import requests
from app.forms.dashboard_forms import StockTickerForm

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    form = StockTickerForm()
    # Tracked stocks are stored in the session
    tracked_stocks = session.get('tracked_stocks', [])
    return render_template('dashboard/dashboard.html', title='Dashboard', form=form, tracked_stocks=tracked_stocks)


@main_bp.route("/track_stock", methods=['POST'])
@login_required
def track_stock():
    form = StockTickerForm()
    if form.validate_on_submit():
        ticker = form.ticker.data.upper()
        tracked_stocks = session.get('tracked_stocks', [])
        if ticker not in tracked_stocks:
            tracked_stocks.append(ticker)
            session['tracked_stocks'] = tracked_stocks
    return redirect(url_for('main.dashboard'))


@main_bp.route("/untrack_stock/<ticker>")
@login_required
def untrack_stock(ticker):
    tracked_stocks = session.get('tracked_stocks', [])
    if ticker in tracked_stocks:
        tracked_stocks.remove(ticker)
        session['tracked_stocks'] = tracked_stocks
    return redirect(url_for('main.dashboard'))

# API endpoint for the frontend to fetch data


@main_bp.route("/api/market_data")
@login_required
def market_data():
    api_key = current_app.config['ALPHA_VANTAGE_API_KEY']
    if not api_key:
        return jsonify({"error": "API key is not configured."}), 500

    data = {}

    # Fetch Commodity Data (Gold, Silver, Oil)
    commodities = {
        'GOLD': 'XAU',
        'SILVER': 'XAG',
        'CRUDE_OIL': 'WTI'
    }
    for name, symbol in commodities.items():
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
            if name == 'CRUDE_OIL':
                url = f'https://www.alphavantage.co/query?function=WTI&interval=monthly&apikey={api_key}'

            r = requests.get(url)
            r.raise_for_status()
            api_data = r.json()

            if name == 'CRUDE_OIL':
                price = api_data.get('data', [{}])[0].get('value')
            else:
                price = api_data.get('Global Quote', {}).get('05. price')

            if price and price != 'null':
                data[name] = f"${float(price):.2f}"
            else:
                data[name] = "N/A"
        except (requests.exceptions.RequestException, KeyError, IndexError):
            data[name] = "Error"

    # Fetch Stock Data
    tracked_stocks = session.get('tracked_stocks', [])
    stock_data = {}
    for ticker in tracked_stocks:
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}'
            r = requests.get(url)
            r.raise_for_status()
            api_data = r.json()
            price = api_data.get('Global Quote', {}).get('05. price')
            if price:
                stock_data[ticker] = f"${float(price):.2f}"
            else:
                stock_data[ticker] = "N/A"
        except (requests.exceptions.RequestException, KeyError):
            stock_data[ticker] = "Error"

    data['stocks'] = stock_data
    return jsonify(data)
