# serv.py - Version corrigée avec le patch original
import warnings
warnings.filterwarnings('ignore')

# PATCH YFINANCE - API DIRECTE (à conserver)
import yfinance_patch  # Ceci active le patch

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import os
import pytz
import logging
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'trading-monitor-secret-key'
CORS(app)

US_TIMEZONE = pytz.timezone('America/New_York')
cache = {}
CACHE_DURATION = 300  # 5 minutes

# ============================================================
# CATÉGORIES D'INDICES - Version réduite
# ============================================================

CATEGORIES = [
    {'id': 'us', 'name': 'US', 'color': '#00e5a0', 
     'symbols': ['^GSPC', '^DJI', '^IXIC', '^NDX', '^RUT']},
    {'id': 'europe', 'name': 'Europe', 'color': '#ffd166',
     'symbols': ['^FTSE', '^GDAXI', '^FCHI', '^STOXX50E', '^SMI']},
    {'id': 'asia', 'name': 'Asie', 'color': '#e63946',
     'symbols': ['^N225', '^HSI', '^AXJO', '^KS11', '^TWII']},
]

ALL_SYMBOLS = []
for cat in CATEGORIES:
    ALL_SYMBOLS.extend(cat['symbols'])

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_cached(key):
    if key in cache:
        data, ts = cache[key]
        if (datetime.now() - ts).seconds < CACHE_DURATION:
            return data
    return None

def set_cached(key, data):
    cache[key] = (data, datetime.now())

def get_interval_for_period(period):
    intervals = {
        '1d': '1m',
        '5d': '5m',
        '1mo': '15m',
        '3mo': '1h',
        '6mo': '1d',
        '1y': '1d'
    }
    return intervals.get(period, '1d')

def safe_float(v, default=0.0):
    try:
        if pd.isna(v) or v is None:
            return default
        return float(v)
    except:
        return default

def safe_int(v, default=0):
    try:
        if pd.isna(v) or v is None:
            return default
        return int(v)
    except:
        return default

# ============================================================
# INDICATEURS TECHNIQUES
# ============================================================

def calculate_rsi(data, period=14):
    if len(data) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100
    return 100 - (100 / (1 + avg_gain / avg_loss))

def calculate_all_indicators(candles):
    if not candles or len(candles) < 20:
        return {}
    close = [c['close'] for c in candles]
    current_price = close[-1]
    
    indicators = {
        'current_price': current_price,
        'last_rsi': calculate_rsi(close, 14),
        'last_sma_20': sum(close[-20:]) / 20 if len(close) >= 20 else None,
        'volatility': round(np.std(close[-20:]) / np.mean(close[-20:]) * 100, 2) if len(close) >= 20 else 0,
    }
    
    # Signaux
    signals = []
    score = 0
    
    if indicators['last_rsi'] is not None:
        if indicators['last_rsi'] < 30:
            signals.append({'type': 'buy', 'indicator': 'RSI', 'value': f"{indicators['last_rsi']:.1f}", 'message': 'Survente'})
            score += 15
        elif indicators['last_rsi'] > 70:
            signals.append({'type': 'sell', 'indicator': 'RSI', 'value': f"{indicators['last_rsi']:.1f}", 'message': 'Surexploitation'})
            score -= 15
    
    if score > 20:
        recommendation = 'ACHAT'
        confidence = min(95, 50 + abs(score) * 0.8)
    elif score < -20:
        recommendation = 'VENTE'
        confidence = min(95, 50 + abs(score) * 0.8)
    else:
        recommendation = 'NEUTRE'
        confidence = 50 + (abs(score) / 2)
    
    indicators['signals'] = signals
    indicators['recommendation'] = recommendation
    indicators['confidence'] = min(95, max(15, confidence))
    indicators['score'] = score
    
    return indicators

# ============================================================
# ROUTES
# ============================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/clear-cache')
def clear_cache():
    cache.clear()
    return jsonify({'status': 'ok'})

@app.route('/api/chart/<symbol>')
def get_chart(symbol):
    """Récupère les données de chandeliers avec le patch yfinance"""
    try:
        period = request.args.get('period', '1mo')
        interval = get_interval_for_period(period)
        
        cache_key = f"chart_{symbol}_{period}"
        cached = get_cached(cache_key)
        if cached:
            logger.info(f"✅ Cache pour {symbol}")
            return jsonify(cached)
        
        logger.info(f"📊 Chart request: {symbol} period={period}")
        
        # Utiliser yfinance patché
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            logger.warning(f"⚠️ Pas de données pour {symbol}")
            return jsonify({'error': f'No data for {symbol}', 'candles': []}), 404
        
        candles = []
        for idx, row in hist.iterrows():
            candles.append({
                'time': int(idx.timestamp()),
                'open': safe_float(row['Open']),
                'high': safe_float(row['High']),
                'low': safe_float(row['Low']),
                'close': safe_float(row['Close']),
                'volume': safe_int(row['Volume'])
            })
        
        result = {'candles': candles}
        set_cached(cache_key, result)
        
        logger.info(f"✅ {len(candles)} bougies pour {symbol}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur {symbol}: {e}")
        return jsonify({'error': str(e), 'candles': []}), 500

@app.route('/api/indicators/<symbol>')
def get_indicators(symbol):
    try:
        period = request.args.get('period', '1mo')
        
        cache_key = f"indicators_{symbol}_{period}"
        cached = get_cached(cache_key)
        if cached:
            return jsonify(cached)
        
        # Récupérer les données via la route chart
        response = get_chart(symbol)
        if hasattr(response, 'json'):
            data = response.json
        else:
            data = response
        
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
        else:
            return jsonify({'error': 'No data'}), 404
        
        indicators = calculate_all_indicators(candles)
        indicators['symbol'] = symbol
        
        set_cached(cache_key, indicators)
        return jsonify(indicators)
        
    except Exception as e:
        logger.error(f"❌ Erreur indicateurs {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/watchlist')
def get_watchlist():
    """Charge séquentiellement les symboles"""
    try:
        results = []
        symbols_to_fetch = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^GDAXI', '^FCHI', '^N225', '^HSI']
        
        for symbol in symbols_to_fetch:
            try:
                # Attendre entre chaque requête (important !)
                time.sleep(random.uniform(0.8, 1.5))
                
                response = get_chart(symbol)
                if hasattr(response, 'json'):
                    data = response.json
                else:
                    data = response
                
                if isinstance(data, dict) and 'candles' in data:
                    candles = data['candles']
                    if candles and len(candles) > 1:
                        current = candles[-1]['close']
                        prev = candles[-2]['close']
                        change_pct = ((current - prev) / prev * 100) if prev else 0
                        
                        results.append({
                            'symbol': symbol,
                            'name': symbol,
                            'price': current,
                            'changePercent': change_pct,
                            'change': current - prev,
                        })
            except Exception as e:
                logger.warning(f"Skip {symbol}: {e}")
                continue
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erreur watchlist: {e}")
        return jsonify([])

@app.route('/api/market-status')
def market_status():
    now = datetime.now(US_TIMEZONE)
    is_open = now.weekday() < 5 and 9 <= now.hour <= 16
    return jsonify({
        'status': 'open' if is_open else 'closed',
        'label': 'Ouvert' if is_open else 'Fermé',
        'icon': '🟢' if is_open else '🔴',
        'time': now.strftime('%H:%M:%S')
    })

@app.route('/')
def index():
    return render_template('monitor.html')

# ============================================================
# LANCEMENT
# ============================================================

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 70)
    print("📊 TRADING MONITOR - AVEC PATCH YFINANCE")
    print("=" * 70)
    print("🌐 http://localhost:5001")
    print("=" * 70)
    print("📈 Symboles disponibles:")
    for cat in CATEGORIES:
        print(f"   {cat['name']}: {', '.join(cat['symbols'])}")
    print("=" * 70)
    print("⏱️  Délai entre les requêtes: 0.8-1.5 secondes")
    print("   Cache: 5 minutes")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5001, debug=True)