from flask import Flask, request, jsonify, send_file
import os
from functools import wraps
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Ensure firebase_config is imported to initialize Firebase once
import firebase_config            # calls initialize_app(), provides firestore_db
from firebase_admin import auth as firebase_auth
from db_config import DB_CONFIG as DB_URI


from model import db, ma, bcrypt
from model.user import User
from model.transaction import Transaction, transaction_schema, transactions_schema
from model.trigger import Trigger
from model.wallet import WalletBalance
from model.order import Order
from model.escrow import Escrow
from model.rating import Rating

from services.exchange_api import (
    get_live_rates,
    get_historical_rates,
    get_margin_info,
    get_historical_rates_df
)
from services.gold_api import get_gold_price, get_historical_gold_prices
from services.prediction import forecast_rates_hw
from services.firestore_sync import sync_transaction_to_firestore

# -------------------------- Load Environment --------------------------

from db_config import DB_CONFIG
SECRET_KEY = "default_secret_key"         # or hard‑code your secret here


# -------------------------- Flask App --------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']      = DB_URI
app.config['SECRET_KEY']                   = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize extensions
db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)
limiter = Limiter(get_remote_address)
limiter.init_app(app)
CORS(app)

# -------------------------- Auth Decorator --------------------------
def firebase_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        hdr = request.headers.get('Authorization','')
        if not hdr.startswith('Bearer '):
            return jsonify({'error':'Missing token'}), 403
        token = hdr.split()[1]
        try:
            decoded = firebase_auth.verify_id_token(token)
        except Exception as e:
            return jsonify({'error': str(e)}), 403

        user = User.query.filter_by(firebase_uid=decoded['uid']).first()
        if not user:
            user = User(firebase_uid=decoded['uid'], email=decoded.get('email'))
            db.session.add(user)
            db.session.commit()

        return f(user, *args, **kwargs)
    return decorated

# -------------------------- Feature 4: Transactions --------------------------
@app.route('/transaction', methods=['POST'])
@limiter.limit('10 per minute')
@firebase_token_required
def add_transaction(current_user):
    data       = request.json or {}
    usd_amount = float(data.get('usd_amount', 0))
    lbp_amount = float(data.get('lbp_amount', 0))
    usd_to_lbp = data.get('usd_to_lbp')
    if usd_amount <= 0 or lbp_amount <= 0 or usd_to_lbp is None:
        return jsonify({'error':'Invalid input values'}), 400

    txn = Transaction(
        usd_amount=usd_amount,
        lbp_amount=lbp_amount,
        usd_to_lbp=bool(usd_to_lbp),
        user_id=current_user.id
    )
    db.session.add(txn)
    db.session.commit()
    sync_transaction_to_firestore(txn)
    return jsonify(transaction_schema.dump(txn)), 201

@app.route('/transactions', methods=['GET'])
@limiter.limit('5 per minute')
@firebase_token_required
def get_user_transactions(current_user):
    txns = Transaction.query.filter_by(user_id=current_user.id).all()
    return jsonify(transactions_schema.dump(txns)), 200

@app.route('/latest', methods=['GET'])
@firebase_token_required
def get_latest_transaction(current_user):
    txn = Transaction.query.filter_by(user_id=current_user.id) \
            .order_by(Transaction.added_date.desc()).first()
    if not txn:
        return jsonify({'error':'No transactions found'}), 404
    return jsonify(transaction_schema.dump(txn)), 200

# -------------------------- Feature 1 & 2: Rates & Predictions --------------------------
@app.route('/exchangeRate', methods=['GET'])
def get_exchange_rate():
    from datetime import datetime, timedelta
    end   = datetime.utcnow()
    start = end - timedelta(hours=72)
    txns  = Transaction.query.filter(
                Transaction.added_date.between(start,end),
                Transaction.usd_to_lbp.is_(True)
            ).all()
    if not txns:
        return jsonify({'error':'No transactions'}), 404
    total_usd = sum(t.usd_amount for t in txns)
    total_lbp = sum(t.lbp_amount for t in txns)
    if total_usd == 0:
        return jsonify({'error':'Invalid txn data'}), 400
    rate = total_lbp / total_usd
    return jsonify({'usd_to_lbp': rate, 'lbp_to_usd': 1/rate}), 200

@app.route('/api/live-rates')
def live_rates():
    try:
        return jsonify(get_live_rates())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gold-price')
def gold_price():
    try:
        return jsonify(get_gold_price())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/gold')
def historical_gold():
    days = int(request.args.get('days', 7))
    try:
        return jsonify(get_historical_gold_prices(days=days))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-rates')
def dashboard_rates():
    try:
        ex = get_live_rates()
        gd = get_gold_price()
        return jsonify({
            'currency_rates': ex['quotes'],
            'base_currency':  ex['source'],
            'gold_price':     gd
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/margin/<currency>')
@firebase_token_required    # or remove this decorator if you want it public
def show_margin(current_user, currency):
    # read `percent` query‐param (default 2%)
    percent = float(request.args.get("percent", 2))
    try:
        result = get_margin_info(
            currency=currency.upper(),
            source="USD",         # or whatever base you want
            margin_percent=percent
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/historical/<currency>')
def historical_currency(currency):
    days = int(request.args.get('days', 7))
    try:
        return jsonify(get_historical_rates(
            source='USD', currency=currency.upper(), days=days
        ))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historical-df')
def historical_df():
    src  = request.args.get('source', 'USD').upper()
    cur  = request.args.get('currency', 'EUR').upper()
    days = int(request.args.get('days', 7))
    df   = get_historical_rates_df(source=src, currency=cur, days=days)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return jsonify({'status':'success','data': df.to_dict('records')}), 200

@app.route('/predict-df')
def predict_df():
    src = request.args.get('source', 'USD').upper()
    cur = request.args.get('currency', 'EUR').upper()
    h   = int(request.args.get('history_days', 30))
    f   = int(request.args.get('forecast_days', 7))
    dfh = get_historical_rates_df(src, cur, h)
    last= dfh['rate'].iloc[-1]
    dfp = forecast_rates_hw(src, cur, h, f)
    first = dfp['yhat'].iloc[0]
    suggestion = 'BUY' if first > last else 'SELL' if first < last else 'HOLD'
    dfp['date'] = pd.to_datetime(dfp['date']).dt.strftime('%Y-%m-%d')
    return jsonify({'status':'success','suggestion':suggestion,'data':dfp.to_dict('records')}), 200

@app.route('/predict-plot')
def predict_plot():
    src = request.args.get('source', 'USD').upper()
    cur = request.args.get('currency', 'EUR').upper()
    h   = int(request.args.get('history_days', 30))
    f   = int(request.args.get('forecast_days', 7))
    dfh = get_historical_rates_df(src, cur, h)
    dfp = forecast_rates_hw(src, cur, h, f)
    dfp['date'] = pd.to_datetime(dfp['date'])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dfh['date'], dfh['rate'], label='Historical')
    ax.plot(dfp['date'], dfp['yhat'], linestyle='--', marker='x', label='Forecast')
    ax.set_title(f'{src} → {cur} Forecast')
    ax.set_xlabel('Date'); ax.set_ylabel('Rate')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    buf = io.BytesIO(); plt.savefig(buf, format='png'); buf.seek(0); plt.close(fig)
    return send_file(buf, mimetype='image/png')

# -------------------------- Feature 8: Triggers --------------------------
@app.route('/check-triggers', methods=['POST'])
@firebase_token_required
def create_trigger(current_user):
    data = request.get_json() or {}
    bc, tc, op, th = (
        data.get('base_currency',''),
        data.get('target_currency',''),
        data.get('operator'),
        data.get('threshold')
    )
    if not all([bc, tc, op, th]):
        return jsonify({'error':'Missing fields'}), 400
    if op not in ['>', '<', '>=', '<=', '==']:
        return jsonify({'error':'Invalid operator'}), 400
    try:
        th = float(th)
    except:
        return jsonify({'error':'Threshold must be number'}), 400

    trig = Trigger(
        base_currency=bc.upper(),
        target_currency=tc.upper(),
        operator=op,
        threshold=th
    )
    db.session.add(trig)
    db.session.commit()
    return jsonify({'id':trig.id}), 201

@app.route('/check-live-triggers', methods=['POST'])
def check_live_triggers():
    alerts = []
    for t in Trigger.query.filter_by(triggered=False).all():
        try:
            data = get_live_rates(source=t.base_currency, currencies=[t.target_currency])
            rate = data['quotes'][t.base_currency + t.target_currency]
            if eval(f"{rate}{t.operator}{t.threshold}"):
                t.triggered = True
                db.session.commit()
                alerts.append({
                    'id': t.id,
                    'base_currency': t.base_currency,
                    'target_currency': t.target_currency,
                    'operator': t.operator,
                    'threshold': t.threshold,
                    'live_rate': rate
                })
        except:
            pass
    return jsonify({'triggered_alerts': alerts}), 200

# -------------------------- Feature 7: P2P Exchange --------------------------
@app.route('/api/wallet', methods=['GET'])
@firebase_token_required
def get_wallet(current_user):
    ws = WalletBalance.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'currency':w.currency,'balance':w.balance} for w in ws]), 200

@app.route('/api/wallet/deposit', methods=['POST'])
@firebase_token_required
def deposit(current_user):
    d   = request.get_json() or {}
    cur = d.get('currency')
    amt = float(d.get('amount', 0))
    if amt <= 0 or not cur:
        return jsonify({'error':'Invalid input'}), 400
    w = WalletBalance.query.filter_by(user_id=current_user.id, currency=cur).first()
    if not w:
        w = WalletBalance(user_id=current_user.id, currency=cur, balance=0)
        db.session.add(w)
    w.balance += amt
    db.session.commit()
    return jsonify({'currency': w.currency, 'balance': w.balance}), 200

@app.route('/api/orders', methods=['GET'])
def list_orders():
    os = Order.query.filter_by(status='OPEN').all()
    return jsonify([{
        'id': o.id,
        'user_id': o.user_id,
        'type': o.type,
        'base_currency': o.base_currency,
        'target_currency': o.target_currency,
        'amount': o.amount,
        'price': o.price
    } for o in os]), 200

@app.route('/api/orders', methods=['POST'])
@firebase_token_required
def create_order(current_user):
    d = request.get_json() or {}
    o = Order(
        user_id=current_user.id,
        type=d['type'],
        base_currency=d['base'],
        target_currency=d['target'],
        amount=float(d['amount']),
        price=float(d['price'])
    )
    db.session.add(o)
    db.session.commit()
    return jsonify({'id': o.id}), 201

@app.route('/api/orders/<int:order_id>/accept', methods=['POST'])
@firebase_token_required
def accept_order(current_user, order_id):
    o = Order.query.get_or_404(order_id)
    if o.user_id == current_user.id or o.status != 'OPEN':
        return jsonify({'error':'Cannot accept'}), 400
    bw = WalletBalance.query.filter_by(
        user_id=current_user.id,
        currency=o.base_currency
    ).first()
    if not bw or bw.balance < o.amount:
        return jsonify({'error':'Insufficient balance'}), 400
    bw.balance -= o.amount
    o.status = 'COMPLETED'
    e = Escrow(
        order_id=o.id,
        buyer_id=current_user.id,
        seller_id=o.user_id,
        amount=o.amount,
        price=o.price,
        target_currency=o.target_currency
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({'escrow_id': e.id}), 201


@app.route('/api/escrow/<int:escrow_id>/release', methods=['POST'])
@firebase_token_required
def release_escrow(current_user, escrow_id):
    e = Escrow.query.get_or_404(escrow_id)
    if current_user.id != e.seller_id or e.status != 'PENDING':
        return jsonify({'error':'Unauthorized'}), 403
    sw = WalletBalance.query.filter_by(
        user_id=e.buyer_id,
        currency=e.target_currency
    ).first()
    if not sw:
        sw = WalletBalance(user_id=e.buyer_id, currency=e.target_currency, balance=0)
        db.session.add(sw)
    sw.balance += e.amount * e.price
    e.status = 'RELEASED'
    db.session.commit()
    return jsonify({'status':'released'}), 200

@app.route('/api/rating', methods=['POST'])
@firebase_token_required
def rate_user(current_user):
    d = request.get_json() or {}
    r = Rating(
        rater_id=current_user.id,
        ratee_id=d['ratee_id'],
        score=int(d['score']),
        comment=d.get('comment','')
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({'id': r.id}), 201


from utils.location import get_country_from_ip, get_currency_for_country, get_travel_currency_suggestions

@app.route('/detect-currency', methods=['GET'])
def detect_currency():
    # Get the client’s IP address (with fallback to localhost)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # 1. Get the country
    country = get_country_from_ip(ip)

    # 2. Get the currency
    currency = get_currency_for_country(country)

    # 3. Get nearby/travel currencies
    travel_suggestions = get_travel_currency_suggestions(country)

    # 4. Return the result
    return jsonify({
        "status": "success",
        "ip": ip,
        "country": country,
        "default_currency": currency,
        "travel_currency_suggestions": travel_suggestions
    })
from services.currency_recognition import recognize_currency


@app.route('/recognize-currency', methods=['POST'])
def recognize_currency_route():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Empty filename"}), 400

    temp_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(temp_path)

    try:
        label = recognize_currency(temp_path)
        return jsonify({"status": "success", "currency": label})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        os.remove(temp_path)


# -------------------------- App Runner --------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)