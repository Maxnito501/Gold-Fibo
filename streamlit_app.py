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

# -------------------------------------------------------------
# FRONTEND SOURCE CODES (Inlined for 1-file GitHub upload)
# -------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>trade forex by กุลกิม - Gold Price Analysis Dashboard</title>
    <!-- Modern Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- ApexCharts CDN -->
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <!-- Custom Style -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="glow-bg"></div>
    <div class="app-container">
        
        <!-- Header -->
        <header class="main-header">
            <div class="brand">
                <i class="fa-solid fa-chart-line logo-icon"></i>
                <h1 class="gradient-text">trade forex by กุลกิม</h1>
            </div>
            <div class="header-status">
                <span class="server-badge">
                    <span class="pulse-dot"></span>
                    <span id="connection-status">Connecting to Market...</span>
                </span>
                <span class="time-badge" id="current-time">00:00:00</span>
            </div>
        </header>

        <!-- Main Dashboard Grid -->
        <main class="dashboard-grid">
            
            <!-- Quick Price Cards -->
            <section class="price-cards-row">
                <div class="glass-card price-card live" id="card-spot">
                    <div class="card-icon"><i class="fa-solid fa-coins gold-color"></i></div>
                    <div class="card-info">
                        <h3>Gold Spot (XAU/USD)</h3>
                        <p class="price-val" id="spot-price">$0.00</p>
                        <span class="sub-text" id="spot-time">Loading...</span>
                    </div>
                </div>

                <div class="glass-card price-card" id="card-high">
                    <div class="card-icon"><i class="fa-solid fa-arrow-trend-up green-color"></i></div>
                    <div class="card-info">
                        <h3 id="high-label">Period High</h3>
                        <p class="price-val green-color" id="high-price">$0.00</p>
                        <span class="sub-text">Resistance Target</span>
                    </div>
                </div>

                <div class="glass-card price-card" id="card-low">
                    <div class="card-icon"><i class="fa-solid fa-arrow-trend-down red-color"></i></div>
                    <div class="card-info">
                        <h3 id="low-label">Period Low</h3>
                        <p class="price-val red-color" id="low-price">$0.00</p>
                        <span class="sub-text">Support Target</span>
                    </div>
                </div>

                <div class="glass-card price-card" id="card-spread">
                    <div class="card-icon"><i class="fa-solid fa-right-left blue-color"></i></div>
                    <div class="card-info">
                        <h3>Period Range</h3>
                        <p class="price-val blue-color" id="range-val">$0.00</p>
                        <span class="sub-text" id="range-percentage">0.00%</span>
                    </div>
                </div>
            </section>

            <!-- Technical Indicators Row -->
            <section class="indicators-row">
                <!-- RSI Card -->
                <div class="glass-card indicator-card" id="ind-rsi">
                    <div class="ind-header">
                        <span>RSI (14)</span>
                        <span class="ind-status badge-neutral" id="rsi-status">NEUTRAL</span>
                    </div>
                    <div class="ind-value" id="rsi-val">50.0</div>
                    <div class="ind-desc">Relative Strength Index</div>
                </div>
                
                <!-- Stochastic Card -->
                <div class="glass-card indicator-card" id="ind-stoch">
                    <div class="ind-header">
                        <span>Stochastic (14,3,3)</span>
                        <span class="ind-status badge-neutral" id="stoch-status">NEUTRAL</span>
                    </div>
                    <div class="ind-value" id="stoch-val">%K: 50.0 | %D: 50.0</div>
                    <div class="ind-desc" id="stoch-crossover">No Crossover</div>
                </div>

                <!-- MACD Card -->
                <div class="glass-card indicator-card" id="ind-macd">
                    <div class="ind-header">
                        <span>MACD (12,26,9)</span>
                        <span class="ind-status badge-neutral" id="macd-status">NEUTRAL</span>
                    </div>
                    <div class="ind-value" id="macd-val">0.0000</div>
                    <div class="ind-desc" id="macd-crossover">Histogram: 0.0000</div>
                </div>

                <!-- Volume Trend Card -->
                <div class="glass-card indicator-card" id="ind-volume">
                    <div class="ind-header">
                        <span>Volume Trend (20)</span>
                        <span class="ind-status badge-neutral" id="vol-status">AVERAGE</span>
                    </div>
                    <div class="ind-value" id="vol-val">0 / 0</div>
                    <div class="ind-desc" id="vol-percentage">100% of Average</div>
                </div>
            </section>

            <!-- Chart Area -->
            <section class="chart-section glass-card">
                <div class="chart-header">
                    <div class="chart-title">
                        <h2>Gold Candlestick Chart ($/oz)</h2>
                        <span class="chart-desc">Exchange: COMEX (GC=F)</span>
                    </div>
                    <div class="timeframe-selector">
                        <button class="tf-btn" data-tf="h1">H1</button>
                        <button class="tf-btn active" data-tf="h4">H4</button>
                        <button class="tf-btn" data-tf="day">DAILY</button>
                        <button class="tf-btn" data-tf="week">WEEKLY</button>
                    </div>
                </div>
                <div class="chart-container">
                    <div id="chart-loader" class="loader-overlay">
                        <div class="spinner"></div>
                        <p>Fetching Gold Market Data...</p>
                    </div>
                    <div id="gold-chart"></div>
                </div>
            </section>

            <!-- Grid Part 3: Fibonacci & Swing Planner -->
            <section class="fibo-container-grid">
                
                <!-- Auto Fibonacci Table -->
                <div class="glass-card fibo-card">
                    <div class="card-header-fibo">
                        <h3><i class="fa-solid fa-calculator fibo-icon"></i> Auto Fibonacci Levels</h3>
                        <span class="badge badge-auto" id="auto-tf-badge">H4</span>
                    </div>
                    <div class="fibo-levels-list">
                        <table>
                            <thead>
                                <tr>
                                    <th>Level (%)</th>
                                    <th>Ratio</th>
                                    <th>Price ($/oz)</th>
                                    <th>Role</th>
                                </tr>
                            </thead>
                            <tbody id="auto-fibo-tbody">
                                <tr><td colspan="4" class="text-center">Loading levels...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Swing Trading Planner (AI Recommendation) -->
                <div class="glass-card fibo-card">
                    <div class="card-header-fibo">
                        <h3><i class="fa-solid fa-wand-magic-sparkles fibo-icon"></i> Swing Trading Plan</h3>
                        <span class="badge badge-auto" id="recommendation-trend-badge">ANALYZING</span>
                    </div>
                    <div class="recommendation-content">
                        <div class="rec-card" id="trading-setup-card">
                            <div class="rec-setup-header">
                                <span class="rec-type-badge" id="rec-trade-type">BUY/SELL</span>
                                <h4 class="rec-title" id="rec-trade-desc">Analyzing price action...</h4>
                            </div>
                            <div class="rec-levels-grid">
                                <div class="rec-level-item entry">
                                    <span class="label">ENTRY ZONE (61.8% - 50.0%)</span>
                                    <span class="val" id="rec-entry-val">$0.00</span>
                                </div>
                                <div class="rec-level-item stoploss">
                                    <span class="label">STOP LOSS (below 78.6%)</span>
                                    <span class="val" id="rec-sl-val">$0.00</span>
                                </div>
                                <div class="rec-level-item takeprofit">
                                    <span class="label">TAKE PROFIT (0.0% / High)</span>
                                    <span class="val" id="rec-tp-val">$0.00</span>
                                </div>
                            </div>
                            <div class="rec-analysis-text" id="rec-analysis-desc">
                                Loading swing trade recommendation...
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Grid Part 4: Custom Fibo & Live Trade Portfolio -->
            <section class="fibo-container-grid">
                
                <!-- Custom Fibonacci Inputs -->
                <div class="glass-card fibo-card">
                    <div class="card-header-fibo">
                        <h3><i class="fa-solid fa-user-gear fibo-icon"></i> Custom Fibonacci Input</h3>
                        <span class="badge badge-manual">MANUAL OVERRIDE</span>
                    </div>
                    <div class="fibo-form-container">
                        <p class="form-desc">Define custom High & Low boundary prices to calculate specific Fibonacci Retracements.</p>
                        <div class="form-group-row">
                            <div class="input-group">
                                <label for="custom-high">Custom High Price ($/oz)</label>
                                <div class="input-wrapper">
                                    <span class="input-prefix">$</span>
                                    <input type="number" id="custom-high" step="0.01" placeholder="e.g. 2480.00">
                                </div>
                            </div>
                            <div class="input-group">
                                <label for="custom-low">Custom Low Price ($/oz)</label>
                                <div class="input-wrapper">
                                    <span class="input-prefix">$</span>
                                    <input type="number" id="custom-low" step="0.01" placeholder="e.g. 2350.00">
                                </div>
                            </div>
                        </div>
                        <div class="form-actions">
                            <button id="btn-calc-custom" class="btn btn-primary"><i class="fa-solid fa-circle-check"></i> Calculate & Overlay</button>
                            <button id="btn-reset-custom" class="btn btn-secondary"><i class="fa-solid fa-arrow-rotate-left"></i> Reset to Auto</button>
                        </div>

                        <!-- Manual Levels Table -->
                        <div class="custom-levels-result hidden" id="custom-levels-result">
                            <h4 class="sub-title">Calculated Custom Levels</h4>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Level (%)</th>
                                        <th>Price ($/oz)</th>
                                        <th>Distance</th>
                                    </tr>
                                </thead>
                                <tbody id="custom-fibo-tbody">
                                    <!-- Populated on calculation -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Position Portfolio Analyzer -->
                <div class="glass-card fibo-card">
                    <div class="card-header-fibo">
                        <h3><i class="fa-solid fa-briefcase fibo-icon"></i> Gold Position Analyzer</h3>
                        <span class="badge badge-manual">PORTFOLIO TRACKER</span>
                    </div>
                    <div class="portfolio-container">
                        <p class="form-desc">Enter your active/pending trades to calculate floating P&L and evaluate entry quality.</p>
                        
                        <!-- Add Position Form -->
                        <form id="add-position-form" class="fibo-form-container" onsubmit="event.preventDefault();">
                            <div class="form-group-row-triple">
                                <div class="input-group">
                                    <label for="pos-type">Order Type</label>
                                    <select id="pos-type" class="custom-select">
                                        <option value="BUY">BUY (Long)</option>
                                        <option value="SELL">SELL (Short)</option>
                                    </select>
                                </div>
                                <div class="input-group">
                                    <label for="pos-entry">Entry Price ($/oz)</label>
                                    <input type="number" id="pos-entry" step="0.01" required placeholder="e.g. 2380.00" class="portfolio-input">
                                </div>
                                <div class="input-group">
                                    <label for="pos-lots">Volume (Ounces / ออนซ์)</label>
                                    <input type="number" id="pos-lots" step="0.10" min="0.10" max="100.0" value="1.00" required class="portfolio-input">
                                </div>
                            </div>
                            <div class="form-group-row">
                                <div class="input-group">
                                    <label for="pos-sl">Stop Loss (SL) - Optional</label>
                                    <input type="number" id="pos-sl" step="0.01" placeholder="e.g. 2350.00" class="portfolio-input">
                                </div>
                                <div class="input-group">
                                    <label for="pos-tp">Take Profit (TP) - Optional</label>
                                    <input type="number" id="pos-tp" step="0.01" placeholder="e.g. 2440.00" class="portfolio-input">
                                </div>
                            </div>
                            <button type="button" id="btn-add-position" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Add Trade Position</button>
                        </form>
                    </div>
                </div>
            </section>

            <!-- Live Positions Table -->
            <section class="glass-card portfolio-list-section">
                <div class="section-header-portfolio">
                    <h3><i class="fa-solid fa-list-check logo-icon"></i> Active Trades & Live P&L (Unit: Ounces / ออนซ์)</h3>
                    <div class="portfolio-summary-badges">
                        <span class="summary-badge">Total Positions: <strong id="total-positions-count">0</strong></span>
                        <span class="summary-badge">Total Floating P&L: <strong id="total-portfolio-pnl">$0.00</strong></span>
                    </div>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Ounces</th>
                                <th>Entry Price</th>
                                <th>Current Price</th>
                                <th>Stop Loss (SL)</th>
                                <th>Take Profit (TP)</th>
                                <th>R:R Ratio</th>
                                <th>Floating P&L (USD)</th>
                                <th>AI Action Plan</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="positions-tbody">
                            <tr><td colspan="10" class="text-center text-muted">No active positions. Add trades using the form above.</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Technical Analysis Context -->
            <section class="analysis-section glass-card">
                <h3><i class="fa-solid fa-circle-info analysis-icon"></i> Market Structure Analysis (Fibonacci Retracement)</h3>
                <div class="analysis-grid">
                    <div class="analysis-card">
                        <h4>Fibonacci Support & Resistance Roles</h4>
                        <p>Fibonacci Retracements help identify potential support and resistance zones where price action might stall or reverse:</p>
                        <ul>
                            <li><strong>23.6% & 38.2%</strong>: Shallow retracements. Typical in strong trends. Indicates high market momentum.</li>
                            <li><strong>50.0%</strong>: Psychological midpoint. Highly watched level for reversal confirmations.</li>
                            <li><strong>61.8% (The Golden Ratio)</strong>: The key retracement level. A bounce here represents a classic trend continuation entry.</li>
                            <li><strong>78.6%</strong>: Deep retracement. Reaching here shows a weakening trend, often leading to a full retest of the start (100% or 0%).</li>
                        </ul>
                    </div>
                    <div class="analysis-card" id="trading-signals-card">
                        <h4>XAU/USD Current Positioning</h4>
                        <div id="positioning-content">
                            <p>Analyzing price trends against Fibonacci levels...</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Risk Disclaimer Card -->
            <section class="glass-card risk-warning-card">
                <div class="warning-header">
                    <i class="fa-solid fa-triangle-exclamation warning-icon"></i>
                    <h3>คำเตือนความเสี่ยงการลงทุน (Investment Risk Warning)</h3>
                </div>
                <p>
                    <strong>คำเตือน:</strong> การซื้อขายฟอเร็กซ์ สัญญาซื้อขายล่วงหน้า (Futures) และสินค้าโภคภัณฑ์อย่างทองคำ (XAU/USD) 
                    มีความเสี่ยงสูงและอาจไม่เหมาะกับนักลงทุนทุกคน ข้อมูลอัตราแลกเปลี่ยน ระดับ Fibonacci ดัชนีชี้วัดทางเทคนิค (RSI, Stochastic, MACD) 
                    และสัญญาณวิเคราะห์ทั้งหมดในแอปพลิเคชันนี้ <strong>ถูกสร้างขึ้นจากสูตรสถิติและแบบจำลองทางคณิตศาสตร์ย้อนหลังเพื่อวิเคราะห์โครงสร้างตลาดเท่านั้น</strong> 
                    ไม่ใช่บริการนำเทรด สัญญาณบอกจุดเข้าอย่างเป็นทางการ หรือคำปรึกษาชี้ชวนการลงทุนแต่อย่างใด 
                    ผู้พัฒนาแอปพลิเคชัน <strong>ไม่รับผิดชอบต่อผลกำไร ขาดทุน หรือความเสียหายใดๆ ที่เกิดขึ้นจากการเทรดจริงของผู้ใช้งานทั้งสิ้น</strong> 
                    ผู้ลงทุนควรทำการศึกษาความเสี่ยงและฝึกฝนการจัดการเงินทุน (Risk & Money Management) ก่อนทำการลงทุนจริงเสมอ
                </p>
            </section>
        </main>
        
        <!-- Footer -->
        <footer class="main-footer">
            <p>&copy; 2026 Gold Price Analysis Dashboard - Naming: <strong>trade forex by กุลกิม</strong></p>
            <p class="footer-note">Disclaimer: Trading forex and precious metals carries high risk. This dashboard is for educational/analytical purposes only.</p>
        </footer>
    </div>

    <!-- Main JavaScript Logic -->
    <script src="app.js"></script>
</body>
</html>"""

CSS_STYLES = """/* Root Theme Variables */
:root {
    --bg-main: #070a13;
    --bg-darker: #04060c;
    --card-bg: rgba(15, 22, 40, 0.65);
    --card-bg-hover: rgba(20, 30, 55, 0.8);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(255, 255, 255, 0.18);
    --gold: #f0b90b;
    --gold-glow: rgba(240, 185, 11, 0.25);
    --cyan: #00d2ff;
    --cyan-glow: rgba(0, 210, 255, 0.25);
    --green: #00ff87;
    --red: #ff3860;
    --blue: #3b82f6;
    --orange: #ff9f43;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
}

/* Global Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: var(--font-body);
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* Background Glow Effects */
.glow-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: -1;
    background: 
        radial-gradient(circle at 10% 20%, rgba(0, 210, 255, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(240, 185, 11, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95) 0%, var(--bg-darker) 100%);
    pointer-events: none;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-darker);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--gold);
}

/* App Container Layout */
.app-container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    min-height: 100vh;
}

/* Header */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    font-size: 24px;
    color: var(--gold);
    text-shadow: 0 0 10px var(--gold-glow);
}

.gradient-text {
    font-family: var(--font-heading);
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--gold) 0%, var(--cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-status {
    display: flex;
    align-items: center;
    gap: 16px;
}

.server-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 6px rgba(0, 255, 135, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(0, 255, 135, 0);
    }
}

.time-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: monospace;
}

/* Glass Card Styling */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: transform var(--transition-normal), border-color var(--transition-fast), box-shadow var(--transition-normal);
}

.glass-card:hover {
    border-color: var(--border-hover);
}

/* Dashboard Layout Grid */
.dashboard-grid {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* Quick Price Cards Row */
.price-cards-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
}

.price-card {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 24px;
}

.price-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.price-card.live {
    background: linear-gradient(135deg, rgba(15, 22, 40, 0.7) 0%, rgba(240, 185, 11, 0.05) 100%);
    border-color: rgba(240, 185, 11, 0.2);
}

.price-card.live:hover {
    border-color: rgba(240, 185, 11, 0.4);
    box-shadow: 0 12px 40px rgba(240, 185, 11, 0.1);
}

.card-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.04);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    border: 1px solid var(--border-color);
}

.card-info h3 {
    font-family: var(--font-heading);
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 4px;
}

.price-val {
    font-family: var(--font-heading);
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* Indicators Row */
.indicators-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
}

.indicator-card {
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.ind-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
}

.ind-status {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 800;
}

.ind-value {
    font-family: var(--font-heading);
    font-size: 20px;
    font-weight: 800;
}

.ind-desc {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 500;
}

/* Status Badges */
.badge-neutral { background: rgba(255,255,255,0.06); color: var(--text-secondary); border: 1px solid var(--border-color); }
.badge-bullish { background: rgba(0, 255, 135, 0.12); color: var(--green); border: 1px solid rgba(0, 255, 135, 0.2); }
.badge-bearish { background: rgba(255, 56, 96, 0.12); color: var(--red); border: 1px solid rgba(255, 56, 96, 0.2); }
.badge-warning { background: rgba(255, 159, 67, 0.12); color: var(--orange); border: 1px solid rgba(255, 159, 67, 0.2); }

.sub-text {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
}

/* Color Helpers */
.gold-color { color: var(--gold); }
.green-color { color: var(--green); }
.red-color { color: var(--red); }
.blue-color { color: var(--cyan); }
.orange-color { color: var(--orange); }

/* Chart Section */
.chart-section {
    padding: 24px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}

.chart-title h2 {
    font-family: var(--font-heading);
    font-size: 20px;
    font-weight: 700;
}

.chart-desc {
    font-size: 13px;
    color: var(--text-secondary);
}

.timeframe-selector {
    display: flex;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    padding: 4px;
    border-radius: 12px;
}

.tf-btn {
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-secondary);
    padding: 8px 18px;
    border-radius: 8px;
    font-family: var(--font-heading);
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all var(--transition-fast);
}

.tf-btn:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
}

.tf-btn.active {
    color: var(--bg-darker);
    background: var(--gold);
    box-shadow: 0 4px 12px var(--gold-glow);
}

.chart-container {
    position: relative;
    width: 100%;
    min-height: 400px;
    background: rgba(4, 6, 12, 0.4);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    padding: 12px;
}

/* Spinner Loader Overlay */
.loader-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(7, 10, 19, 0.85);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    z-index: 10;
    transition: opacity var(--transition-normal);
}

.loader-overlay.hidden {
    opacity: 0;
    pointer-events: none;
}

.spinner {
    width: 48px;
    height: 48px;
    border: 3px solid rgba(240, 185, 11, 0.1);
    border-top: 3px solid var(--gold);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Fibonacci Section Grid */
.fibo-container-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
    gap: 24px;
}

@media (max-width: 1024px) {
    .fibo-container-grid {
        grid-template-columns: 1fr;
    }
}

.fibo-card {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.card-header-fibo {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header-fibo h3 {
    font-family: var(--font-heading);
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}

.fibo-icon {
    color: var(--gold);
}

.badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.badge-auto {
    background: rgba(0, 210, 255, 0.1);
    color: var(--cyan);
    border: 1px solid rgba(0, 210, 255, 0.2);
}

.badge-manual {
    background: rgba(240, 185, 11, 0.1);
    color: var(--gold);
    border: 1px solid rgba(240, 185, 11, 0.2);
}

/* Styled Table */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    text-align: left;
}

th {
    padding: 12px 16px;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 2px solid var(--border-color);
}

td {
    padding: 12px 16px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color);
}

tr:last-child td {
    border-bottom: none;
}

tbody tr {
    transition: background-color var(--transition-fast);
}

tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

.text-center {
    text-align: center;
}

/* Fibonacci Form */
.fibo-form-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.form-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.form-group-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-group-row-triple {
    display: grid;
    grid-template-columns: 1fr 1.2fr 0.8fr;
    gap: 16px;
}

@media (max-width: 480px) {
    .form-group-row, .form-group-row-triple {
        grid-template-columns: 1fr;
    }
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-prefix {
    position: absolute;
    left: 14px;
    color: var(--text-muted);
    font-weight: 600;
}

.input-wrapper input, .portfolio-input, .custom-select {
    width: 100%;
    padding: 12px;
    background: rgba(4, 6, 12, 0.5);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    color: var(--text-primary);
    font-family: var(--font-heading);
    font-weight: 600;
    font-size: 15px;
    outline: none;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.input-wrapper input {
    padding-left: 28px;
}

.input-wrapper input:focus, .portfolio-input:focus, .custom-select:focus {
    border-color: var(--gold);
    box-shadow: 0 0 10px var(--gold-glow);
}

.custom-select {
    appearance: none;
    background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
    background-repeat: no-repeat;
    background-position: right 10px center;
    background-size: 16px;
    padding-right: 32px;
    cursor: pointer;
}

.custom-select option {
    background-color: var(--bg-darker);
    color: var(--text-primary);
}

.form-actions {
    display: flex;
    gap: 12px;
}

.btn {
    padding: 12px 20px;
    border-radius: 10px;
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    border: none;
    outline: none;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all var(--transition-fast);
}

.btn-primary {
    background: var(--gold);
    color: var(--bg-darker);
    box-shadow: 0 4px 14px var(--gold-glow);
}

.btn-primary:hover {
    background: #f7c92b;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(240, 185, 11, 0.4);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: var(--text-secondary);
}

/* Custom results list */
.custom-levels-result {
    border-top: 1px solid var(--border-color);
    padding-top: 16px;
    margin-top: 8px;
    animation: fadeIn var(--transition-normal);
}

.custom-levels-result.hidden {
    display: none;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

.sub-title {
    font-family: var(--font-heading);
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--cyan);
}

/* Swing Trading Recommendation Card CSS */
.recommendation-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
}

.rec-card {
    background: rgba(4, 6, 12, 0.35);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    transition: border-color var(--transition-fast);
}

.rec-card:hover {
    border-color: rgba(240, 185, 11, 0.25);
}

.rec-setup-header {
    display: flex;
    align-items: center;
    gap: 12px;
}

.rec-type-badge {
    padding: 6px 12px;
    border-radius: 8px;
    font-family: var(--font-heading);
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.rec-type-badge.buy {
    background: rgba(0, 255, 135, 0.12);
    color: var(--green);
    border: 1px solid rgba(0, 255, 135, 0.25);
    box-shadow: 0 0 10px rgba(0, 255, 135, 0.15);
}

.rec-type-badge.sell {
    background: rgba(255, 56, 96, 0.12);
    color: var(--red);
    border: 1px solid rgba(255, 56, 96, 0.25);
    box-shadow: 0 0 10px rgba(255, 56, 96, 0.15);
}

.rec-type-badge.hold {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
}

.rec-title {
    font-family: var(--font-heading);
    font-size: 16px;
    font-weight: 700;
}

.rec-levels-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    background: rgba(4, 6, 12, 0.2);
    border-radius: 8px;
    padding: 12px;
    border: 1px solid rgba(255, 255, 255, 0.03);
}

.rec-level-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 4px;
}

.rec-level-item .label {
    font-size: 10px;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
}

.rec-level-item .val {
    font-family: var(--font-heading);
    font-size: 16px;
    font-weight: 800;
}

.rec-level-item.entry .val { color: var(--cyan); }
.rec-level-item.stoploss .val { color: var(--red); }
.rec-level-item.takeprofit .val { color: var(--green); }

.rec-analysis-text {
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-secondary);
}

/* Portfolio Table & Sections */
.portfolio-list-section {
    padding: 24px;
}

.section-header-portfolio {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}

.section-header-portfolio h3 {
    font-family: var(--font-heading);
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}

.portfolio-summary-badges {
    display: flex;
    gap: 12px;
}

.summary-badge {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

.summary-badge strong {
    color: var(--gold);
    margin-left: 4px;
}

.table-responsive {
    width: 100%;
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: rgba(4, 6, 12, 0.25);
}

/* Order Badges */
.badge-buy {
    background: rgba(0, 255, 135, 0.1);
    color: var(--green);
    border: 1px solid rgba(0, 255, 135, 0.2);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.badge-sell {
    background: rgba(255, 56, 96, 0.1);
    color: var(--red);
    border: 1px solid rgba(255, 56, 96, 0.2);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.profit-text {
    color: var(--green);
    font-weight: 700;
    text-shadow: 0 0 10px rgba(0, 255, 135, 0.15);
}

.loss-text {
    color: var(--red);
    font-weight: 700;
    text-shadow: 0 0 10px rgba(255, 56, 96, 0.15);
}

/* Evaluation Badges */
.eval-badge {
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    display: inline-block;
}

.eval-optimal {
    background: rgba(240, 185, 11, 0.12);
    color: var(--gold);
    border: 1px solid rgba(240, 185, 11, 0.25);
    box-shadow: 0 0 8px rgba(240, 185, 11, 0.1);
}

.eval-safe {
    background: rgba(0, 255, 135, 0.1);
    color: var(--green);
    border: 1px solid rgba(0, 255, 135, 0.2);
}

.eval-warning {
    background: rgba(255, 159, 67, 0.1);
    color: var(--orange);
    border: 1px solid rgba(255, 159, 67, 0.2);
}

.eval-critical {
    background: rgba(255, 56, 96, 0.1);
    color: var(--red);
    border: 1px solid rgba(255, 56, 96, 0.2);
    box-shadow: 0 0 8px rgba(255, 56, 96, 0.1);
}

/* Delete Button */
.btn-delete {
    background: rgba(255, 56, 96, 0.1);
    color: var(--red);
    border: 1px solid rgba(255, 56, 96, 0.2);
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
}

.btn-delete:hover {
    background: var(--red);
    color: var(--bg-darker);
}

/* Market Analysis Section */
.analysis-section {
    padding: 24px;
}

.analysis-icon {
    color: var(--cyan);
    margin-right: 6px;
}

.analysis-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-top: 16px;
}

@media (max-width: 768px) {
    .analysis-grid {
        grid-template-columns: 1fr;
    }
}

.analysis-card {
    background: rgba(4, 6, 12, 0.25);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 18px;
}

.analysis-card h4 {
    font-family: var(--font-heading);
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text-secondary);
    border-left: 3px solid var(--gold);
    padding-left: 8px;
}

.analysis-card p {
    font-size: 13.5px;
    line-height: 1.6;
    color: var(--text-secondary);
    margin-bottom: 12px;
}

.analysis-card ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.analysis-card li {
    font-size: 13px;
    line-height: 1.5;
    color: var(--text-secondary);
    position: relative;
    padding-left: 14px;
}

.analysis-card li::before {
    content: "•";
    color: var(--cyan);
    font-weight: bold;
    display: inline-block;
    width: 1em;
    margin-left: -1em;
    position: absolute;
    left: 8px;
}

/* Signals UI Elements */
.signal-box {
    padding: 12px 16px;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: 600;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.signal-neutral {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
}

.signal-bullish {
    background: rgba(0, 255, 135, 0.06);
    border: 1px solid rgba(0, 255, 135, 0.2);
    color: var(--green);
}

.signal-bearish {
    background: rgba(255, 56, 96, 0.06);
    border: 1px solid rgba(255, 56, 96, 0.2);
    color: var(--red);
}

/* Risk Warning Card CSS */
.risk-warning-card {
    padding: 24px;
    border-left: 4px solid var(--red);
    background: rgba(255, 56, 96, 0.04);
    border-color: rgba(255, 56, 96, 0.15) !important;
}

.risk-warning-card:hover {
    border-color: rgba(255, 56, 96, 0.25) !important;
}

.warning-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    color: var(--orange);
}

.warning-icon {
    font-size: 20px;
    text-shadow: 0 0 10px rgba(255, 159, 67, 0.25);
}

.warning-header h3 {
    font-family: var(--font-heading);
    font-size: 16px;
    font-weight: 700;
}

.risk-warning-card p {
    font-size: 13px;
    line-height: 1.7;
    color: var(--text-secondary);
}

/* Footer styling */
.main-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    font-size: 12px;
    color: var(--text-muted);
    border-top: 1px solid var(--border-color);
    flex-wrap: wrap;
    gap: 12px;
}

.footer-note {
    font-style: italic;
    max-width: 600px;
    text-align: right;
}

@media (max-width: 768px) {
    .main-header, .main-footer {
        flex-direction: column;
        gap: 12px;
        text-align: center;
    }
    .footer-note {
        text-align: center;
    }
}
"""

JS_CODE = """// Global Application State
let marketData = null;
let activeTimeframe = 'h4';
let chartInstance = null;
let isManualMode = false;
let manualHigh = null;
let manualLow = null;
let activePositions = [];

// Fibonacci levels ratios
const FIB_RATIOS = [
    { name: '100.0%', ratio: 1.0, role: 'Resistance (High)', desc: 'Starting point of retracement' },
    { name: '78.6%', ratio: 0.786, role: 'Deep Retracement', desc: 'Last line of defence for trend' },
    { name: '61.8%', ratio: 0.618, role: 'Golden Ratio', desc: 'Key continuation entry point' },
    { name: '50.0%', ratio: 0.50, role: 'Midpoint', desc: 'Strong psychological level' },
    { name: '38.2%', ratio: 0.382, role: 'Moderate Retracement', desc: 'Indicates healthy trend momentum' },
    { name: '23.6%', ratio: 0.236, role: 'Shallow Retracement', desc: 'Indicates very strong trend' },
    { name: '0.0%', ratio: 0.0, role: 'Support (Low)', desc: 'Ending point of retracement' }
];

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    initClock();
    fetchData();
    initPortfolio();
    setupEventListeners();
});

// Update Clock
function initClock() {
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        setInterval(() => {
            const now = new Date();
            clockElement.textContent = now.toLocaleTimeString('en-US', { hour12: false });
        }, 1000);
    }
}

// Fetch Market Data
async function fetchData() {
    const loader = document.getElementById('chart-loader');
    const statusText = document.getElementById('connection-status');
    
    // Check if data is already injected by Streamlit Python wrapper
    if (window.marketData) {
        console.log('Using injected Streamlit market data');
        marketData = window.marketData;
        if (statusText) {
            statusText.textContent = 'Connected (Cloud)';
            statusText.parentElement.style.borderColor = 'rgba(0, 255, 135, 0.2)';
        }
        updateDashboard();
        if (loader) loader.classList.add('hidden');
        return;
    }
    
    try {
        if (loader) loader.classList.remove('hidden');
        if (statusText) statusText.textContent = 'Syncing Gold Data...';
        
        // Single unified fetch to prevent being blocked (as required)
        const response = await fetch('/api/gold-data');
        if (!response.ok) throw new Error('Network response was not ok');
        
        marketData = await response.json();
        
        if (statusText) {
            statusText.textContent = 'Connected Live';
            statusText.parentElement.style.borderColor = 'rgba(0, 255, 135, 0.2)';
        }
        
        // Render initial view
        updateDashboard();
        if (loader) loader.classList.add('hidden');
    } catch (error) {
        console.error('Fetch error:', error);
        if (statusText) {
            statusText.textContent = 'Connection Error';
            statusText.parentElement.style.borderColor = 'rgba(255, 56, 96, 0.3)';
        }
        const pulse = document.querySelector('.pulse-dot');
        if (pulse) {
            pulse.style.backgroundColor = 'var(--red)';
            pulse.style.boxShadow = '0 0 8px var(--red)';
        }
        
        if (loader) {
            const loaderText = loader.querySelector('p');
            if (loaderText) loaderText.textContent = 'Failed to load market data. Retrying in 10s...';
            const spinner = loader.querySelector('.spinner');
            if (spinner) spinner.style.borderTopColor = 'var(--red)';
        }
        
        setTimeout(fetchData, 10000);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Timeframe selector buttons
    const tfButtons = document.querySelectorAll('.tf-btn');
    tfButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            tfButtons.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            activeTimeframe = e.target.getAttribute('data-tf');
            
            // Switch timeframe and redraw
            updateDashboard();
        });
    });

    // Custom Fibonacci Buttons
    const btnCalc = document.getElementById('btn-calc-custom');
    if (btnCalc) btnCalc.addEventListener('click', calculateCustomFibo);
    
    const btnReset = document.getElementById('btn-reset-custom');
    if (btnReset) btnReset.addEventListener('click', resetToAuto);

    // Portfolio Form Button
    const btnAddPos = document.getElementById('btn-add-position');
    if (btnAddPos) btnAddPos.addEventListener('click', addPosition);
}

// Calculate Fibonacci Levels helper
function calculateFibonacciLevels(high, low) {
    const diff = high - low;
    return FIB_RATIOS.map(item => {
        const price = low + (diff * item.ratio);
        return {
            name: item.name,
            ratio: item.ratio,
            price: roundToTwo(price),
            role: item.role,
            desc: item.desc
        };
    });
}

function roundToTwo(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
}

// ==========================================
// PORTFOLIO LOGIC (Local Storage)
// ==========================================

function initPortfolio() {
    const stored = localStorage.getItem('gold_portfolio');
    if (stored) {
        try {
            activePositions = JSON.parse(stored);
        } catch (e) {
            activePositions = [];
        }
    } else {
        activePositions = [];
    }
}

function savePortfolio() {
    localStorage.setItem('gold_portfolio', JSON.stringify(activePositions));
}

function addPosition() {
    const type = document.getElementById('pos-type').value;
    const entry = parseFloat(document.getElementById('pos-entry').value);
    const lots = parseFloat(document.getElementById('pos-lots').value); // Direct ounces
    const slInput = document.getElementById('pos-sl').value;
    const tpInput = document.getElementById('pos-tp').value;

    if (isNaN(entry) || isNaN(lots) || entry <= 0 || lots <= 0) {
        alert('Please enter a valid positive Entry Price and Volume.');
        return;
    }

    const sl = slInput ? parseFloat(slInput) : null;
    const tp = tpInput ? parseFloat(tpInput) : null;

    if (sl !== null && sl <= 0) {
        alert('Stop Loss must be a positive number.');
        return;
    }
    if (tp !== null && tp <= 0) {
        alert('Take Profit must be a positive number.');
        return;
    }

    const newPos = {
        id: Date.now(),
        type,
        entry: roundToTwo(entry),
        lots: roundToTwo(lots), // represents Ounces
        sl: sl ? roundToTwo(sl) : null,
        tp: tp ? roundToTwo(tp) : null,
        dateAdded: new Date().toISOString()
    };

    activePositions.push(newPos);
    savePortfolio();
    
    // Clear inputs
    document.getElementById('pos-entry').value = '';
    document.getElementById('pos-sl').value = '';
    document.getElementById('pos-tp').value = '';
    document.getElementById('pos-lots').value = '1.00';

    updateDashboard();
}

function deletePosition(id) {
    activePositions = activePositions.filter(p => p.id !== id);
    savePortfolio();
    updateDashboard();
}

// Render active positions & calculate P&L in USD
function renderPortfolio(latestPrice, currentFibLevels) {
    const tbody = document.getElementById('positions-tbody');
    const totalCountEl = document.getElementById('total-positions-count');
    const totalPnlEl = document.getElementById('total-portfolio-pnl');
    
    if (totalCountEl) totalCountEl.textContent = activePositions.length;
    
    if (!tbody) return;

    if (activePositions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center text-muted">No active positions. Add trades using the form above.</td></tr>`;
        if (totalPnlEl) {
            totalPnlEl.textContent = '$0.00';
            totalPnlEl.className = '';
        }
        return;
    }

    tbody.innerHTML = '';
    let totalPnl = 0;

    activePositions.forEach(pos => {
        // P&L calculation: volume is direct ounces (P&L = diff * oz)
        let pnl = 0;
        if (pos.type === 'BUY') {
            pnl = (latestPrice - pos.entry) * pos.lots;
        } else {
            pnl = (pos.entry - latestPrice) * pos.lots;
        }
        totalPnl += pnl;

        // Calculate R:R Ratio
        let rrText = 'N/A';
        if (pos.sl && pos.tp) {
            const reward = Math.abs(pos.tp - pos.entry);
            const risk = Math.abs(pos.entry - pos.sl);
            if (risk > 0) {
                rrText = `1:${(reward / risk).toFixed(2)}`;
            }
        }

        // Eval Rating
        const rating = evaluatePosition(pos, currentFibLevels, latestPrice);

        // Format classes
        const typeBadge = pos.type === 'BUY' ? 'badge-buy' : 'badge-sell';
        const pnlClass = pnl >= 0 ? 'profit-text' : 'loss-text';
        const formattedPnl = (pnl >= 0 ? '+$' : '-$') + Math.abs(pnl).toLocaleString('en-US', { minimumFractionDigits: 2 });

        tbody.innerHTML += `
            <tr>
                <td><span class="${typeBadge}">${pos.type}</span></td>
                <td><strong>${pos.lots.toFixed(2)} oz</strong></td>
                <td>$${pos.entry.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                <td>$${latestPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                <td>${pos.sl ? '$' + pos.sl.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '<span class="text-muted">None</span>'}</td>
                <td>${pos.tp ? '$' + pos.tp.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '<span class="text-muted">None</span>'}</td>
                <td><span class="sub-text">${rrText}</span></td>
                <td><span class="${pnlClass}">${formattedPnl}</span></td>
                <td><span class="eval-badge ${rating.class}">${rating.label}</span></td>
                <td>
                    <button class="btn-delete" onclick="deletePosition(${pos.id})" title="Delete Position">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    if (totalPnlEl) {
        totalPnlEl.textContent = (totalPnl >= 0 ? '+$' : '-$') + Math.abs(totalPnl).toLocaleString('en-US', { minimumFractionDigits: 2 });
        totalPnlEl.className = totalPnl >= 0 ? 'green-color' : 'red-color';
    }
}

// Upgraded AI Active Position Action Evaluator
function evaluatePosition(pos, levels, latestPrice) {
    const high = levels.find(l => l.name === '100.0%').price;
    const low = levels.find(l => l.name === '0.0%').price;
    const fib618 = levels.find(l => l.name === '61.8%').price;
    const fib50 = levels.find(l => l.name === '50.0%').price;
    const fib786 = levels.find(l => l.name === '78.6%').price;
    const diff = high - low;

    // 1. Critical Danger: No Stop Loss
    if (!pos.sl) {
        return { label: '⚠️ NO SL (เสี่ยงสูง!)', class: 'eval-critical' };
    }

    // 2. Action: Cut Loss
    if (pos.type === 'BUY' && latestPrice <= pos.sl) {
        return { label: '🚨 CUT LOSS (ต้องคัด!)', class: 'eval-critical' };
    }
    if (pos.type === 'SELL' && latestPrice >= pos.sl) {
        return { label: '🚨 CUT LOSS (ต้องคัด!)', class: 'eval-critical' };
    }

    // 3. Action: Take Profit
    if (pos.tp) {
        if (pos.type === 'BUY' && latestPrice >= pos.tp) {
            return { label: '🟣 TAKE PROFIT (ขายกําไร!)', class: 'eval-optimal' };
        }
        if (pos.type === 'SELL' && latestPrice <= pos.tp) {
            return { label: '🟣 TAKE PROFIT (ขายกําไร!)', class: 'eval-optimal' };
        }
    }

    // 4. Action: DCA / Buy More (ถัว)
    // For BUY: Price is below entry, but still above SL, and touching a lower strong support (e.g. 61.8% or 78.6%)
    if (pos.type === 'BUY' && latestPrice < pos.entry) {
        const supportGolden = Math.min(fib618, fib50);
        // If price is near the 61.8% support or 78.6% support and we haven't crossed SL
        if (latestPrice >= supportGolden - (diff * 0.01) && latestPrice <= supportGolden + (diff * 0.01)) {
            return { label: '🔵 DCA / BUY MORE (ถัว)', class: 'eval-warning' };
        }
        if (latestPrice >= fib786 - (diff * 0.01) && latestPrice <= fib786 + (diff * 0.01)) {
            return { label: '🔵 DCA / BUY MORE (ถัว)', class: 'eval-warning' };
        }
    }
    // For SELL: Price is above entry, below SL, and touching a higher strong resistance (50%, 61.8%, 78.6%)
    if (pos.type === 'SELL' && latestPrice > pos.entry) {
        const resistanceGolden = Math.max(fib618, fib50);
        if (latestPrice >= resistanceGolden - (diff * 0.01) && latestPrice <= resistanceGolden + (diff * 0.01)) {
            return { label: '🔵 DCA / SELL MORE (ถัว)', class: 'eval-warning' };
        }
        if (latestPrice >= fib786 - (diff * 0.01) && latestPrice <= fib786 + (diff * 0.01)) {
            return { label: '🔵 DCA / SELL MORE (ถัว)', class: 'eval-warning' };
        }
    }

    // 5. Action: Hold
    return { label: '🟢 HOLD (ถือต่อไป)', class: 'eval-safe' };
}

// ==========================================
// SWING PLANNER & CONFLUENCE RECOMMENDATION
// ==========================================

function updateIndicators(meta) {
    const rsiValEl = document.getElementById('rsi-val');
    const rsiStatusEl = document.getElementById('rsi-status');
    const stochValEl = document.getElementById('stoch-val');
    const stochStatusEl = document.getElementById('stoch-status');
    const stochCrossEl = document.getElementById('stoch-crossover');
    const macdValEl = document.getElementById('macd-val');
    const macdStatusEl = document.getElementById('macd-status');
    const macdCrossEl = document.getElementById('macd-crossover');
    const volValEl = document.getElementById('vol-val');
    const volStatusEl = document.getElementById('vol-status');
    const volPercentEl = document.getElementById('vol-percentage');

    if (!meta || !meta.latest_indicators) return;
    const ind = meta.latest_indicators;

    // 1. RSI
    if (rsiValEl && rsiStatusEl) {
        rsiValEl.textContent = ind.rsi.toFixed(1);
        if (ind.rsi <= 30) {
            rsiStatusEl.textContent = 'OVERSOLD';
            rsiStatusEl.className = 'ind-status badge-bullish';
        } else if (ind.rsi >= 70) {
            rsiStatusEl.textContent = 'OVERBOUGHT';
            rsiStatusEl.className = 'ind-status badge-bearish';
        } else {
            rsiStatusEl.textContent = 'NEUTRAL';
            rsiStatusEl.className = 'ind-status badge-neutral';
        }
    }

    // 2. Stochastic
    if (stochValEl && stochStatusEl && stochCrossEl) {
        stochValEl.textContent = `%K: ${ind.stoch_k.toFixed(1)} | %D: ${ind.stoch_d.toFixed(1)}`;
        
        // Oversold / Overbought status
        if (ind.stoch_k <= 20 && ind.stoch_d <= 20) {
            stochStatusEl.textContent = 'OVERSOLD';
            stochStatusEl.className = 'ind-status badge-bullish';
        } else if (ind.stoch_k >= 80 && ind.stoch_d >= 80) {
            stochStatusEl.textContent = 'OVERBOUGHT';
            stochStatusEl.className = 'ind-status badge-bearish';
        } else {
            stochStatusEl.textContent = 'NEUTRAL';
            stochStatusEl.className = 'ind-status badge-neutral';
        }

        // Crossover
        if (ind.stoch_k > ind.stoch_d) {
            stochCrossEl.textContent = 'Bullish Crossover (ตัดขึ้น)';
            stochCrossEl.className = 'ind-desc green-color';
        } else {
            stochCrossEl.textContent = 'Bearish Crossover (ตัดลง)';
            stochCrossEl.className = 'ind-desc red-color';
        }
    }

    // 3. MACD
    if (macdValEl && macdStatusEl && macdCrossEl) {
        macdValEl.textContent = ind.macd.toFixed(4);
        macdCrossEl.textContent = `Histogram: ${ind.macd_hist.toFixed(4)}`;
        
        if (ind.macd > ind.macd_signal) {
            macdStatusEl.textContent = 'BULLISH';
            macdStatusEl.className = 'ind-status badge-bullish';
            macdCrossEl.className = 'ind-desc green-color';
        } else {
            macdStatusEl.textContent = 'BEARISH';
            macdStatusEl.className = 'ind-status badge-bearish';
            macdCrossEl.className = 'ind-desc red-color';
        }
    }

    // 4. Volume
    if (volValEl && volStatusEl && volPercentEl) {
        volValEl.textContent = `${ind.volume.toLocaleString()} / ${Math.round(ind.vol_ma20).toLocaleString()}`;
        const pct = ind.vol_ma20 > 0 ? (ind.volume / ind.vol_ma20) * 100 : 100;
        volPercentEl.textContent = `${pct.toFixed(0)}% of 20-candle MA`;

        if (pct >= 150) {
            volStatusEl.textContent = 'HIGH VOLUME';
            volStatusEl.className = 'ind-status badge-bullish';
        } else if (pct <= 50) {
            volStatusEl.textContent = 'LOW VOLUME';
            volStatusEl.className = 'ind-status badge-neutral';
        } else {
            volStatusEl.textContent = 'AVERAGE';
            volStatusEl.className = 'ind-status badge-neutral';
        }
    }
}

function generateTradingPlan(latestPrice, levels, meta) {
    const trendBadge = document.getElementById('recommendation-trend-badge');
    const typeBadge = document.getElementById('rec-trade-type');
    const descEl = document.getElementById('rec-trade-desc');
    const entryEl = document.getElementById('rec-entry-val');
    const slEl = document.getElementById('rec-sl-val');
    const tpEl = document.getElementById('rec-tp-val');
    const analysisEl = document.getElementById('rec-analysis-desc');

    if (!trendBadge || !typeBadge || !descEl || !entryEl || !slEl || !tpEl || !analysisEl || !meta || !meta.latest_indicators) return;

    const high = levels.find(l => l.name === '100.0%').price;
    const low = levels.find(l => l.name === '0.0%').price;
    const fib618 = levels.find(l => l.name === '61.8%').price;
    const fib50 = levels.find(l => l.name === '50.0%').price;
    const fib786 = levels.find(l => l.name === '78.6%').price;
    const diff = high - low;

    const ind = meta.latest_indicators;
    const isBullish = latestPrice >= fib50;

    // Confluence Scoring System
    let score = 0;
    if (isBullish) {
        // Bullish signals
        if (ind.rsi <= 45) score++; // RSI oversold or low
        if (ind.stoch_k > ind.stoch_d || ind.stoch_k <= 25) score++; // Stoch cross or oversold
        if (ind.macd > ind.macd_signal) score++; // MACD golden cross
        if (ind.volume > ind.vol_ma20 * 1.2) score++; // Breakout volume

        // Recommended Entry: Golden zone
        const entryLow = Math.min(fib618, fib50);
        const entryHigh = Math.max(fib618, fib50);
        entryEl.textContent = `$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}`;

        const recommendedSL = fib786 - (diff * 0.015);
        slEl.textContent = `$${recommendedSL.toFixed(2)}`;
        tpEl.textContent = `$${high.toFixed(2)}`;

        if (score >= 3) {
            trendBadge.textContent = 'ACCUMULATE (STRONG BUY) 🔥';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(0, 255, 135, 0.12)';
            trendBadge.style.color = 'var(--green)';
            trendBadge.style.borderColor = 'rgba(0, 255, 135, 0.3)';

            typeBadge.textContent = 'ACCUMULATE';
            typeBadge.className = 'rec-type-badge buy';
            descEl.textContent = 'High-Confluence BUY Zone';
            
            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> ระบบประเมินว่าโครงสร้างเป็น <strong>ขาขึ้นที่มีระดับความแม่นยำสูง (High Confluence)</strong> 
                โดยระดับ Fibo ยอดซื้อย่อยตรงกับสัญญาณกลับตัวของอินดิเคเตอร์ครบครัน (RSI/Stochastic ต่ำ และ MACD ตัดขึ้น) 
                แนะนำตั้งจุดซื้อสะสมที่โซน <strong>$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}</strong> 
                ตั้งจุดคัดลอส (SL) ป้องกันขอบล่างที่ <strong>$${recommendedSL.toFixed(2)}</strong> และขายทำกำไรที่แนวต้านหลัก <strong>$${high.toFixed(2)}</strong>
            `;
        } else if (score >= 1) {
            trendBadge.textContent = 'ACCUMULATE (BUY) 🟢';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(0, 255, 135, 0.08)';
            trendBadge.style.color = 'var(--green)';
            trendBadge.style.borderColor = 'rgba(0, 255, 135, 0.15)';

            typeBadge.textContent = 'BUY SETUP';
            typeBadge.className = 'rec-type-badge buy';
            descEl.textContent = 'Standard BUY Zone';

            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> โครงสร้างหลักเป็นขาขึ้น แต่ <strong>อินดิเคเตอร์มีสัญญาณขัดแย้งบางส่วน</strong> 
                สามารถตั้งรับออเดอร์ในโซนสะสม <strong>$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}</strong> ได้ตามปกติ 
                แต่แนะนำให้ตั้งจุดคัดลอส (SL) ไว้เสมอที่ <strong>$${recommendedSL.toFixed(2)}</strong> และห้ามเปิดไม้หนาเกินไป (รักษา Money Management)
            `;
        } else {
            trendBadge.textContent = 'WAIT / HOLD (รอ) ⏳';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(255, 159, 67, 0.12)';
            trendBadge.style.color = 'var(--orange)';
            trendBadge.style.borderColor = 'rgba(255, 159, 67, 0.3)';

            typeBadge.textContent = 'WAIT';
            typeBadge.className = 'rec-type-badge hold';
            descEl.textContent = 'Wait for Support Confirmation';

            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> แม้ราคาจะย่อตัวลงมาแนวรับ Fibo แต่ <strong>โมเมนตัมอินดิเคเตอร์มีแรงเทขายกดดันหนาแน่นมาก</strong> (เสี่ยงจับมีดร่วง) 
                แนะนำให้ <strong>ชะลอการซื้อ/รอสัญญาณกลับตัว</strong> จนกว่าแท่งเทียน H1 จะเริ่มเกิดไส้ล่าง (Pinbar) หรือ Stochastic เริ่มมีสัญญาณตัดขึ้นคอนเฟิร์ม ค่อยหาจังหวะสะสมใหม่
            `;
        }
    } else {
        // Bearish signals
        if (ind.rsi >= 55) score++;
        if (ind.stoch_k < ind.stoch_d || ind.stoch_k >= 75) score++;
        if (ind.macd < ind.macd_signal) score++;
        if (ind.volume > ind.vol_ma20 * 1.2) score++;

        const entryLow = Math.min(fib618, fib50);
        const entryHigh = Math.max(fib618, fib50);
        entryEl.textContent = `$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}`;

        const recommendedSL = fib786 + (diff * 0.015);
        slEl.textContent = `$${recommendedSL.toFixed(2)}`;
        tpEl.textContent = `$${low.toFixed(2)}`;

        if (score >= 3) {
            trendBadge.textContent = 'DISTRIBUTE (STRONG SELL) 🚨';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(255, 56, 96, 0.12)';
            trendBadge.style.color = 'var(--red)';
            trendBadge.style.borderColor = 'rgba(255, 56, 96, 0.3)';

            typeBadge.textContent = 'SELL/SHORT';
            typeBadge.className = 'rec-type-badge sell';
            descEl.textContent = 'High-Confluence SELL Zone';

            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> โครงสร้างเป็น <strong>ขาลงและมีแรงกดดันเต็มรูปแบบ (High Confluence)</strong> 
                โมเมนตัมชี้วัดพร้อมเทขายเพิ่มเมื่อแตะโซนแนวต้าน <strong>$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}</strong> 
                แนะนำวางจุดจำหน่ายหรือเปิด Sell ป้องกันเสี่ยงโดยตั้ง SL ที่แนวต้านสำคัญ <strong>$${recommendedSL.toFixed(2)}</strong> เป้าหมายทำกำไร <strong>$${low.toFixed(2)}</strong>
            `;
        } else if (score >= 1) {
            trendBadge.textContent = 'DISTRIBUTE (SELL) 🔴';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(255, 56, 96, 0.08)';
            trendBadge.style.color = 'var(--red)';
            trendBadge.style.borderColor = 'rgba(255, 56, 96, 0.15)';

            typeBadge.textContent = 'SELL SETUP';
            typeBadge.className = 'rec-type-badge sell';
            descEl.textContent = 'Standard SELL Zone';

            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> ตลาดมีแรงเทขายหลักเด่นชัดกว่าขากล่อม ให้วางจุดดักขายหากราคารีบาวด์ขึ้นหาแนวต้านสวิง <strong>$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}</strong> 
                จำกัดจุดตัดขาดทุนเด็ดขาดไว้ที่ <strong>$${recommendedSL.toFixed(2)}</strong> และขายเก็บกำไรที่ขอบล่าง <strong>$${low.toFixed(2)}</strong>
            `;
        } else {
            trendBadge.textContent = 'WAIT / HOLD (รอ) ⏳';
            trendBadge.className = 'badge';
            trendBadge.style.background = 'rgba(255, 159, 67, 0.12)';
            trendBadge.style.color = 'var(--orange)';
            trendBadge.style.borderColor = 'rgba(255, 159, 67, 0.3)';

            typeBadge.textContent = 'WAIT';
            typeBadge.className = 'rec-type-badge hold';
            descEl.textContent = 'Wait for Resistance Confirmation';

            analysisEl.innerHTML = `
                ⚠️ <strong>คำเตือนการลงทุน:</strong> โครงสร้างหลักอ่อนแรงลง แต่ <strong>อินดิเคเตอร์มีแรงรีบาวด์ดันขึ้นค่อนข้างกระชั้นชิด</strong> 
                แนะนำให้ <strong>ชะลอการกดออเดอร์และเฝ้ารอก่อน</strong> จนกว่าจะถึงแนวต้านสำคัญหรือราคาแสดงความอ่อนแรงชัดเจน ค่อยเปิดเทรดตามเป้าหมายเพื่อลดความเสี่ยงโดนลากขาขึ้น
            `;
        }
    }
}

// ==========================================
// CORE DASHBOARD & CHART UPDATE
// ==========================================

function updateDashboard() {
    if (!marketData) return;

    const tfData = marketData[activeTimeframe];
    if (!tfData) return;

    // 1. Update latest gold price card
    const latestPrice = marketData.latest_price;
    const spotPriceEl = document.getElementById('spot-price');
    if (spotPriceEl) spotPriceEl.textContent = `$${latestPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    
    const spotTimeEl = document.getElementById('spot-time');
    const rawTime = new Date(marketData.latest_time);
    if (spotTimeEl) spotTimeEl.textContent = `As of: ${rawTime.toLocaleString('en-US')}`;

    // 2. Update Period Cards
    const periodHigh = tfData.meta.high;
    const periodLow = tfData.meta.low;
    const range = periodHigh - periodLow;
    const rangePercent = (range / periodLow) * 100;

    const highPriceEl = document.getElementById('high-price');
    const lowPriceEl = document.getElementById('low-price');
    const rangeValEl = document.getElementById('range-val');
    const rangePercentEl = document.getElementById('range-percentage');

    if (highPriceEl) highPriceEl.textContent = `$${periodHigh.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (lowPriceEl) lowPriceEl.textContent = `$${periodLow.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (rangeValEl) rangeValEl.textContent = `$${range.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (rangePercentEl) rangePercentEl.textContent = `+${rangePercent.toFixed(2)}%`;

    const tfLabel = activeTimeframe.toUpperCase();
    const highLabelEl = document.getElementById('high-label');
    const lowLabelEl = document.getElementById('low-label');
    const autoBadgeEl = document.getElementById('auto-tf-badge');

    if (highLabelEl) highLabelEl.textContent = `${tfLabel} Period High`;
    if (lowLabelEl) lowLabelEl.textContent = `${tfLabel} Period Low`;
    if (autoBadgeEl) autoBadgeEl.textContent = tfLabel;

    // 3. Draw/Update Auto Fibonacci levels table
    const autoLevels = calculateFibonacciLevels(periodHigh, periodLow);
    const autoTbody = document.getElementById('auto-fibo-tbody');
    
    if (autoTbody) {
        autoTbody.innerHTML = '';
        autoLevels.forEach(lvl => {
            let rowClass = '';
            if (lvl.name === '61.8%') rowClass = 'gold-color font-bold';
            if (lvl.name === '50.0%') rowClass = 'cyan-color font-bold';
            
            autoTbody.innerHTML += `
                <tr class="${rowClass}">
                    <td><strong>${lvl.name}</strong></td>
                    <td>${lvl.ratio}</td>
                    <td>$${lvl.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td><span class="sub-text">${lvl.role}</span></td>
                </tr>
            `;
        });
    }

    const activeLevels = isManualMode ? calculateFibonacciLevels(manualHigh, manualLow) : autoLevels;

    // 4. Update technical indicators dashboard row
    updateIndicators(tfData.meta);

    // 5. Generate AI recommendations (now passes meta for indicators)
    generateTradingPlan(latestPrice, activeLevels, tfData.meta);

    // 6. Update Positioning signals
    updateTradingSignals(latestPrice, activeLevels);

    // 7. Render Live Trades Portfolio
    renderPortfolio(latestPrice, activeLevels);

    // 8. Draw/Update Chart
    renderChart(tfData.candles, isManualMode ? {high: manualHigh, low: manualLow} : tfData.meta);
}

// Calculate Custom/Manual Fibonacci
function calculateCustomFibo() {
    const highInput = parseFloat(document.getElementById('custom-high').value);
    const lowInput = parseFloat(document.getElementById('custom-low').value);

    if (isNaN(highInput) || isNaN(lowInput)) {
        alert('Please enter valid numerical values for both High and Low prices.');
        return;
    }

    if (highInput <= lowInput) {
        alert('High Price must be greater than Low Price.');
        return;
    }

    isManualMode = true;
    manualHigh = highInput;
    manualLow = lowInput;

    const customLevels = calculateFibonacciLevels(manualHigh, manualLow);

    const customTbody = document.getElementById('custom-fibo-tbody');
    if (customTbody) {
        customTbody.innerHTML = '';
        customLevels.forEach(lvl => {
            customTbody.innerHTML += `
                <tr>
                    <td><strong>${lvl.name}</strong></td>
                    <td>$${lvl.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td><span class="sub-text">${lvl.role}</span></td>
                </tr>
            `;
        });
    }

    const customRes = document.getElementById('custom-levels-result');
    if (customRes) customRes.classList.remove('hidden');
    
    updateDashboard();
}

// Reset custom and restore auto levels
function resetToAuto() {
    isManualMode = false;
    manualHigh = null;
    manualLow = null;
    
    const cHigh = document.getElementById('custom-high');
    const cLow = document.getElementById('custom-low');
    const customRes = document.getElementById('custom-levels-result');

    if (cHigh) cHigh.value = '';
    if (cLow) cLow.value = '';
    if (customRes) customRes.classList.add('hidden');
    
    updateDashboard();
}

// Render Candlestick Chart with Fibonacci horizontal lines
function renderChart(candles, meta) {
    const seriesData = candles.map(c => ({
        x: new Date(c.time).getTime(),
        y: [c.open, c.high, c.low, c.close]
    }));

    const fibLevels = calculateFibonacciLevels(meta.high, meta.low);
    
    const options = {
        series: [{
            data: seriesData
        }],
        chart: {
            type: 'candlestick',
            height: 420,
            background: 'transparent',
            toolbar: {
                show: true,
                autoSelected: 'pan'
            },
            animations: {
                enabled: true
            }
        },
        theme: {
            mode: 'dark'
        },
        xaxis: {
            type: 'datetime',
            labels: {
                style: {
                    colors: '#94a3b8',
                    fontFamily: 'Plus Jakarta Sans'
                }
            }
        },
        yaxis: {
            tooltip: {
                enabled: true
            },
            labels: {
                formatter: function (val) {
                    return '$' + val.toFixed(2);
                },
                style: {
                    colors: '#94a3b8',
                    fontFamily: 'Plus Jakarta Sans'
                }
            }
        },
        plotOptions: {
            candlestick: {
                colors: {
                    upward: '#00ff87',
                    downward: '#ff3860'
                },
                wick: {
                    useFillColor: true
                }
            }
        },
        grid: {
            borderColor: 'rgba(255,255,255,0.05)',
            padding: {
                right: 120
            }
        },
        annotations: {
            yaxis: fibLevels.map(lvl => {
                let strokeColor = 'rgba(255,255,255,0.2)';
                let borderStyle = 'dashed';
                let labelText = `Fib ${lvl.name}: $${lvl.price}`;
                
                if (lvl.name === '61.8%') {
                    strokeColor = 'var(--gold)';
                    borderStyle = 'solid';
                } else if (lvl.name === '50.0%') {
                    strokeColor = 'var(--cyan)';
                    borderStyle = 'solid';
                } else if (lvl.name === '100.0%' || lvl.name === '0.0%') {
                    strokeColor = 'rgba(255,255,255,0.4)';
                    borderStyle = 'solid';
                }

                return {
                    y: lvl.price,
                    borderColor: strokeColor,
                    strokeDashArray: borderStyle === 'dashed' ? 3 : 0,
                    label: {
                        borderColor: strokeColor,
                        position: 'right',
                        offsetX: 110,
                        style: {
                            color: '#070a13',
                            background: strokeColor,
                            fontWeight: '600',
                            fontFamily: 'Outfit'
                        },
                        text: labelText
                    }
                };
            })
        }
    };

    if (chartInstance) {
        chartInstance.updateOptions(options);
    } else {
        chartInstance = new ApexCharts(document.querySelector("#gold-chart"), options);
        chartInstance.render();
    }
}

// Generate Positioning Signals / Analysis Context
function updateTradingSignals(currentPrice, levels) {
    const content = document.getElementById('positioning-content');
    if (!content) return;
    
    const sortedLevels = [...levels].sort((a, b) => b.price - a.price);
    
    let upperLevel = null;
    let lowerLevel = null;
    
    for (let i = 0; i < sortedLevels.length - 1; i++) {
        if (currentPrice <= sortedLevels[i].price && currentPrice >= sortedLevels[i+1].price) {
            upperLevel = sortedLevels[i];
            lowerLevel = sortedLevels[i+1];
            break;
        }
    }

    if (!upperLevel || !lowerLevel) {
        if (currentPrice > sortedLevels[0].price) {
            content.innerHTML = `
                <p>The price is trading <strong>above the 100.0% (${sortedLevels[0].name}) level</strong> of $${sortedLevels[0].price.toFixed(2)}.</p>
                <p>This is extremely bullish territory, indicating a potential breakout or continuation run.</p>
                <div class="signal-box signal-bullish">
                    <i class="fa-solid fa-circle-chevron-up"></i> BULLISH CONTINUATION TERRITORY
                </div>
            `;
        } else {
            content.innerHTML = `
                <p>The price is trading <strong>below the 0.0% (${sortedLevels[sortedLevels.length-1].name}) level</strong> of $${sortedLevels[sortedLevels.length-1].price.toFixed(2)}.</p>
                <p>This is extremely bearish territory, representing a breakdown below major support.</p>
                <div class="signal-box signal-bearish">
                    <i class="fa-solid fa-circle-chevron-down"></i> BEARISH BREAKDOWN TERRITORY
                </div>
            `;
        }
        return;
    }

    const totalDist = upperLevel.price - lowerLevel.price;
    const distFromLower = currentPrice - lowerLevel.price;
    const positionPercent = (distFromLower / totalDist) * 100;

    let sentiment = 'NEUTRAL CONSOLIDATION';
    let signalClass = 'signal-neutral';
    let signalIcon = 'fa-solid fa-scale-balanced';
    let strategyAdvice = '';

    if (lowerLevel.name === '50.0%' || lowerLevel.name === '61.8%') {
        sentiment = 'BULLISH WATCH (Golden Zone)';
        signalClass = 'signal-bullish';
        signalIcon = 'fa-solid fa-circle-check';
        strategyAdvice = 'Price is holding in the 50.0% - 61.8% golden pocket. This is a high-probability reversal zone. Look for bullish price action candles (pinbars, engulfing) on lower timeframes to establish long positions targeting the upper Fibonacci levels.';
    } else if (upperLevel.name === '61.8%' || upperLevel.name === '78.6%') {
        sentiment = 'RETRACEMENT WATCH';
        signalClass = 'signal-neutral';
        signalIcon = 'fa-solid fa-clock';
        strategyAdvice = 'Price has bounced but faces overhead resistance in the 61.8% - 78.6% zone. A failure to break above these levels suggests a secondary bearish wave towards 38.2% or 23.6%. Wait for confirmation.';
    } else if (lowerLevel.name === '0.0%' || lowerLevel.name === '23.6%') {
        sentiment = 'BEARISH PRESSURE';
        signalClass = 'signal-bearish';
        signalIcon = 'fa-solid fa-circle-exclamation';
        strategyAdvice = 'Price is hovering near the major range lows (0% to 23.6%). Buyers are failing to create sustained relief. A breakdown below the 0% support target will trigger stop-losses and open the door for further downside.';
    } else {
        sentiment = 'CONSOLIDATING MID-RANGE';
        strategyAdvice = 'Price is oscillating in the middle ranges between the 23.6% and 50% levels. Trading here carries lower probability. Best practice is to wait for price to reach extreme levels (0.0% support or 61.8% golden pocket resistance) before taking entries.';
    }

    content.innerHTML = `
        <p>The spot price of <strong>$${currentPrice.toFixed(2)}</strong> is currently consolidated between:</p>
        <ul>
            <li><strong>Resistance:</strong> $${upperLevel.price.toFixed(2)} (${upperLevel.name} - ${upperLevel.role})</li>
            <li><strong>Support:</strong> $${lowerLevel.price.toFixed(2)} (${lowerLevel.name} - ${lowerLevel.role})</li>
        </ul>
        <p>It is currently situated <strong>${positionPercent.toFixed(1)}%</strong> of the way up within this zone.</p>
        <p class="mt-2">${strategyAdvice}</p>
        <div class="signal-box ${signalClass}">
            <i class="${signalIcon}"></i> ${sentiment}
        </div>
    `;
}
"""

# -------------------------------------------------------------
# MAIN STREAMLIT APPLICATION
# -------------------------------------------------------------

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

    # Technical Indicators Engine (using pandas built-in math)
    def calculate_indicators(df):
        if len(df) < 30:
            df['RSI'] = 50.0
            df['Stoch_K'] = 50.0
            df['Stoch_D'] = 50.0
            df['MACD'] = 0.0
            df['MACD_Signal'] = 0.0
            df['MACD_Hist'] = 0.0
            df['Vol_MA20'] = df['Volume']
            return df

        # A. RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # B. Stochastic Oscillator (14, 3, 3)
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14 + 1e-10))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        df['Stoch_K'] = df['Stoch_K'].fillna(50.0)
        df['Stoch_D'] = df['Stoch_D'].fillna(50.0)

        # C. MACD (12, 26, 9)
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # D. Volume MA20
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        df['Vol_MA20'] = df['Vol_MA20'].fillna(df['Volume'])

        return df

    # Process all to candles list
    def process_df(df):
        if df.empty:
            return []
        
        # calculate indicators on df
        df = calculate_indicators(df)
        
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
                'volume': int(row['Volume']),
                'rsi': round(float(row['RSI']), 2) if 'RSI' in row else 50.0,
                'stoch_k': round(float(row['Stoch_K']), 2) if 'Stoch_K' in row else 50.0,
                'stoch_d': round(float(row['Stoch_D']), 2) if 'Stoch_D' in row else 50.0,
                'macd': round(float(row['MACD']), 4) if 'MACD' in row else 0.0,
                'macd_signal': round(float(row['MACD_Signal']), 4) if 'MACD_Signal' in row else 0.0,
                'macd_hist': round(float(row['MACD_Hist']), 4) if 'MACD_Hist' in row else 0.0,
                'vol_ma20': round(float(row['Vol_MA20']), 1) if 'Vol_MA20' in row else float(row['Volume'])
            })
        return candles

    h1_candles = process_df(df_h1)
    h4_candles = process_df(df_h4)
    d_candles = process_df(df_d)
    w_candles = process_df(df_w)

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

    def get_meta(candles):
        if not candles:
            return {'high': 0, 'low': 0, 'fibonacci': {}, 'latest_indicators': {}}
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        max_high = max(highs)
        min_low = min(lows)
        
        latest = candles[-1]
        
        return {
            'high': max_high,
            'low': min_low,
            'fibonacci': calculate_fibonacci(max_high, min_low),
            'latest_indicators': {
                'rsi': latest.get('rsi', 50.0),
                'stoch_k': latest.get('stoch_k', 50.0),
                'stoch_d': latest.get('stoch_d', 50.0),
                'macd': latest.get('macd', 0.0),
                'macd_signal': latest.get('macd_signal', 0.0),
                'macd_hist': latest.get('macd_hist', 0.0),
                'volume': latest.get('volume', 0),
                'vol_ma20': latest.get('vol_ma20', 0.0)
            }
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

    # 2. Inline CSS and JS + Inject Market Data
    html = HTML_TEMPLATE.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>{CSS_STYLES}</style>'
    )
    
    injected_js = f"""
    <script>
    window.marketData = {json_data};
    {JS_CODE}
    </script>
    """
    html = html.replace('<script src="app.js"></script>', injected_js)

    # 3. Render HTML component (height=1500 is ideal to fit indicators)
    components.html(html, height=1550, scrolling=True)

if __name__ == '__main__':
    main()
