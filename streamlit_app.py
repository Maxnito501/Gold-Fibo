import os
import json
import time
import yfinance as yf
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Configure Streamlit Page
st.set_page_config(
    page_title="trade forex by กุลกิม - Gold Price Analysis",
    page_icon="📊",
    layout="wide"
)

# Hide Streamlit header/footer for premium custom feel
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem;}
            iframe {border: none; width: 100% !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def calculate_fibonacci(high, low):
    diff = high - low
    return {
        '100.0': round(high, 2),
        '78.6': round(low + diff * 0.786, 2),
        '61.8': round(low + diff * 0.618, 2),
        '50.0': round(low + diff * 0.50, 2),
        '38.2': round(low + diff * 0.382, 2),
        '23.6': round(low + diff * 0.236, 2),
        '0.0': round(low, 2)
    }

def process_df(df):
    if df.empty:
        return []
    
    candles = []
    for idx, row in df.iterrows():
        if hasattr(idx, 'isoformat'):
            time_str = idx.isoformat()
        else:
            time_str = str(idx)
        
        candles.append({
            'time': time_str,
            'open': round(float(row['Open']), 2),
            'high': round(float(row['High']), 2),
            'low': round(float(row['Low']), 2),
            'close': round(float(row['Close']), 2),
            'volume': int(row['Volume'])
        })
    return candles

# Cache data for 5 minutes (300 seconds) to avoid getting blocked
@st.cache_data(ttl=300)
def fetch_gold_data():
    ticker = yf.Ticker("GC=F")
    
    # 1. Fetch 1h data
    df_h1 = ticker.history(period="1mo", interval="1h")
    
    # 2. Resample H1 to H4
    df_h4 = pd.DataFrame()
    if not df_h1.empty:
        df_h4 = df_h1.resample("4h").agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"
        }).dropna()

    # 3. Fetch Daily data (last 1 year)
    df_d = ticker.history(period="1y", interval="1d")

    # 4. Fetch Weekly data (last 2 years)
    df_w = ticker.history(period="2y", interval="1wk")

    # Process all to candles list
    h1_candles = process_df(df_h1)
    h4_candles = process_df(df_h4)
    d_candles = process_df(df_d)
    w_candles = process_df(df_w)

    def get_meta(candles):
        if not candles:
            return {'high': 0, 'low': 0, 'fibonacci': {}}
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        max_high = max(highs)
        min_low = min(lows)
        return {
            'high': max_high,
            'low': min_low,
            'fibonacci': calculate_fibonacci(max_high, min_low)
        }

    return {
        'h1': {
            'candles': h1_candles,
            'meta': get_meta(h1_candles)
        },
        'h4': {
            'candles': h4_candles,
            'meta': get_meta(h4_candles)
        },
        'day': {
            'candles': d_candles,
            'meta': get_meta(d_candles)
        },
        'week': {
            'candles': w_candles,
            'meta': get_meta(w_candles)
        },
        'latest_price': h1_candles[-1]['close'] if h1_candles else (d_candles[-1]['close'] if d_candles else 0.0),
        'latest_time': h1_candles[-1]['time'] if h1_candles else (d_candles[-1]['time'] if d_candles else '')
    }

def main():
    # 1. Fetch data
    try:
        data = fetch_gold_data()
        json_data = json.dumps(data)
    except Exception as e:
        st.error(f"Error fetching data from Yahoo Finance: {str(e)}")
        return

    # 2. Read static files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(script_dir, 'static')
    
    try:
        with open(os.path.join(static_dir, 'index.html'), 'r', encoding='utf-8') as f:
            html = f.read()
            
        with open(os.path.join(static_dir, 'styles.css'), 'r', encoding='utf-8') as f:
            css = f.read()
            
        with open(os.path.join(static_dir, 'app.js'), 'r', encoding='utf-8') as f:
            js = f.read()
    except Exception as e:
        st.error(f"Error reading frontend source files: {str(e)}")
        return

    # 3. Inline CSS and JS + Inject Market Data
    # Replace the stylesheet link
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>{css}</style>'
    )
    
    # Replace the app.js script tag with inlined code and injected data
    injected_js = f"""
    <script>
    window.marketData = {json_data};
    {js}
    </script>
    """
    html = html.replace('<script src="app.js"></script>', injected_js)

    # 4. Render HTML component (height=1400 is ideal for fitting the whole page)
    components.html(html, height=1400, scrolling=True)

if __name__ == '__main__':
    main()
