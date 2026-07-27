// Global Application State
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
    setInterval(() => {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }, 1000);
}

// Fetch Market Data
async function fetchData() {
    const loader = document.getElementById('chart-loader');
    const statusText = document.getElementById('connection-status');
    
    // Check if data is already injected by Streamlit Python wrapper
    if (window.marketData) {
        console.log('Using injected Streamlit market data');
        marketData = window.marketData;
        statusText.textContent = 'Connected (Cloud)';
        statusText.parentElement.style.borderColor = 'rgba(0, 255, 135, 0.2)';
        updateDashboard();
        loader.classList.add('hidden');
        return;
    }
    
    try {
        loader.classList.remove('hidden');
        statusText.textContent = 'Syncing Gold Data...';
        
        // Single unified fetch to prevent being blocked (as required)
        const response = await fetch('/api/gold-data');
        if (!response.ok) throw new Error('Network response was not ok');
        
        marketData = await response.json();
        
        statusText.textContent = 'Connected Live';
        statusText.parentElement.style.borderColor = 'rgba(0, 255, 135, 0.2)';
        
        // Render initial view
        updateDashboard();
        loader.classList.add('hidden');
    } catch (error) {
        console.error('Fetch error:', error);
        statusText.textContent = 'Connection Error';
        statusText.parentElement.style.borderColor = 'rgba(255, 56, 96, 0.3)';
        document.querySelector('.pulse-dot').style.backgroundColor = 'var(--red)';
        document.querySelector('.pulse-dot').style.boxShadow = '0 0 8px var(--red)';
        
        const loaderText = loader.querySelector('p');
        loaderText.textContent = 'Failed to load market data. Retrying in 10s...';
        loader.querySelector('.spinner').style.borderTopColor = 'var(--red)';
        
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
    document.getElementById('btn-calc-custom').addEventListener('click', calculateCustomFibo);
    document.getElementById('btn-reset-custom').addEventListener('click', resetToAuto);

    // Portfolio Form Button
    document.getElementById('btn-add-position').addEventListener('click', addPosition);
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
    const lots = parseFloat(document.getElementById('pos-lots').value);
    const slInput = document.getElementById('pos-sl').value;
    const tpInput = document.getElementById('pos-tp').value;

    if (isNaN(entry) || isNaN(lots) || entry <= 0 || lots <= 0) {
        alert('Please enter a valid positive Entry Price and Lot Size.');
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
        lots: roundToTwo(lots),
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
    document.getElementById('pos-lots').value = '0.10';

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
    
    totalCountEl.textContent = activePositions.length;
    
    if (activePositions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center text-muted">No active positions. Add trades using the form above.</td></tr>`;
        totalPnlEl.textContent = '$0.00';
        totalPnlEl.className = '';
        return;
    }

    tbody.innerHTML = '';
    let totalPnl = 0;

    activePositions.forEach(pos => {
        // P&L calculation: 1 Standard Lot = 100 oz of gold
        let pnl = 0;
        if (pos.type === 'BUY') {
            pnl = (latestPrice - pos.entry) * pos.lots * 100;
        } else {
            pnl = (pos.entry - latestPrice) * pos.lots * 100;
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
        const rating = evaluatePosition(pos, currentFibLevels);

        // Format classes
        const typeBadge = pos.type === 'BUY' ? 'badge-buy' : 'badge-sell';
        const pnlClass = pnl >= 0 ? 'profit-text' : 'loss-text';
        const formattedPnl = (pnl >= 0 ? '+$' : '-$') + Math.abs(pnl).toLocaleString('en-US', { minimumFractionDigits: 2 });

        tbody.innerHTML += `
            <tr>
                <td><span class="${typeBadge}">${pos.type}</span></td>
                <td><strong>${pos.lots.toFixed(2)}</strong></td>
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

    totalPnlEl.textContent = (totalPnl >= 0 ? '+$' : '-$') + Math.abs(totalPnl).toLocaleString('en-US', { minimumFractionDigits: 2 });
    totalPnlEl.className = totalPnl >= 0 ? 'green-color' : 'red-color';
}

// AI Position Quality Evaluator
function evaluatePosition(pos, levels) {
    const high = levels.find(l => l.name === '100.0%').price;
    const low = levels.find(l => l.name === '0.0%').price;
    const fib618 = levels.find(l => l.name === '61.8%').price;
    const fib50 = levels.find(l => l.name === '50.0%').price;
    const fib786 = levels.find(l => l.name === '78.6%').price;
    const diff = high - low;

    // 1. Critical Danger: No Stop Loss
    if (!pos.sl) {
        return { label: 'CRITICAL: NO SL SET', class: 'eval-critical' };
    }

    // 2. Risk/Reward Ratio Check
    if (pos.sl && pos.tp) {
        const reward = Math.abs(pos.tp - pos.entry);
        const risk = Math.abs(pos.entry - pos.sl);
        if (risk > 0 && (reward / risk) < 1.5) {
            return { label: 'WARNING: POOR R:R', class: 'eval-warning' };
        }
    }

    // 3. Entry Quality against Fibonacci
    if (pos.type === 'BUY') {
        // Buy in the Golden zone (50.0% - 61.8% retracement)
        // Note: fib618 is less than high, and fib50 is higher than low.
        // In retracement, 61.8% is closer to the bottom (lower price than 50.0% in normal ascending retracements).
        // Let's sort levels
        const goldenLower = Math.min(fib618, fib50);
        const goldenUpper = Math.max(fib618, fib50);

        if (pos.entry >= goldenLower - (diff * 0.005) && pos.entry <= goldenUpper + (diff * 0.005)) {
            return { label: 'OPTIMAL: GOLDEN ZONE BUY', class: 'eval-optimal' };
        }
        
        // Buy near major low support (0.0% - 23.6%)
        const supportUpper = low + (diff * 0.236);
        if (pos.entry >= low - (diff * 0.01) && pos.entry <= supportUpper) {
            return { label: 'SAFE: SUPPORT BUY', class: 'eval-safe' };
        }

        // Chasing high (above 78.6% Fibonacci)
        const chasingLower = low + (diff * 0.786);
        if (pos.entry >= chasingLower) {
            return { label: 'CRITICAL: CHASING DOME', class: 'eval-critical' };
        }
    } else { // SELL (Short)
        // Sell in the Golden Zone (retracement up to 50%-61.8% to drop)
        const goldenLower = Math.min(fib618, fib50);
        const goldenUpper = Math.max(fib618, fib50);

        if (pos.entry >= goldenLower - (diff * 0.005) && pos.entry <= goldenUpper + (diff * 0.005)) {
            return { label: 'OPTIMAL: GOLDEN ZONE SELL', class: 'eval-optimal' };
        }

        // Sell near major high resistance (78.6% - 100.0%)
        const resistanceLower = low + (diff * 0.786);
        if (pos.entry >= resistanceLower && pos.entry <= high + (diff * 0.01)) {
            return { label: 'SAFE: RESISTANCE SELL', class: 'eval-safe' };
        }

        // Chasing low (below 23.6% Fibonacci)
        const chasingUpper = low + (diff * 0.236);
        if (pos.entry <= chasingUpper) {
            return { label: 'CRITICAL: CHASING BOTTOM', class: 'eval-critical' };
        }
    }

    return { label: 'SAFE: VALID ENTRY', class: 'eval-safe' };
}

// ==========================================
// SWING PLANNER RECOMMENDATION
// ==========================================

function generateTradingPlan(latestPrice, levels) {
    const trendBadge = document.getElementById('recommendation-trend-badge');
    const typeBadge = document.getElementById('rec-trade-type');
    const descEl = document.getElementById('rec-trade-desc');
    const entryEl = document.getElementById('rec-entry-val');
    const slEl = document.getElementById('rec-sl-val');
    const tpEl = document.getElementById('rec-tp-val');
    const analysisEl = document.getElementById('rec-analysis-desc');

    const high = levels.find(l => l.name === '100.0%').price;
    const low = levels.find(l => l.name === '0.0%').price;
    const fib618 = levels.find(l => l.name === '61.8%').price;
    const fib50 = levels.find(l => l.name === '50.0%').price;
    const fib786 = levels.find(l => l.name === '78.6%').price;
    const diff = high - low;

    // Simple Trend Identification:
    // If latest price is above the 50.0% psychological level, structure is BULLISH.
    // If below 50.0%, structure is BEARISH.
    const isBullish = latestPrice >= fib50;

    if (isBullish) {
        trendBadge.textContent = 'BULLISH';
        trendBadge.className = 'badge badge-auto';
        trendBadge.style.background = 'rgba(0, 255, 135, 0.1)';
        trendBadge.style.color = 'var(--green)';
        trendBadge.style.borderColor = 'rgba(0, 255, 135, 0.2)';

        typeBadge.textContent = 'BUY LIMIT';
        typeBadge.className = 'rec-type-badge buy';

        descEl.textContent = 'Buy the Retracement';

        // Recommended Entry: between 61.8% and 50.0% levels
        const entryLow = Math.min(fib618, fib50);
        const entryHigh = Math.max(fib618, fib50);
        entryEl.textContent = `$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}`;

        // Recommended SL: Just below 78.6% (by 1% of the swing height)
        const recommendedSL = fib786 - (diff * 0.015);
        slEl.textContent = `$${recommendedSL.toFixed(2)}`;

        // Recommended TP: Previous swing High (100%)
        tpEl.textContent = `$${high.toFixed(2)}`;

        analysisEl.innerHTML = `
            Gold displays a <strong>bullish structural advantage</strong> on the ${activeTimeframe.toUpperCase()} timeframe, trading above the 50% midpoint. 
            The most optimal risk-reward strategy is to set a <strong>Buy Limit order in the Golden zone ($${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)})</strong>. 
            Keep Stop Loss tight below the 78.6% retracement ($${recommendedSL.toFixed(2)}) to mitigate market hunt risks, targeting the previous Swing High ($${high.toFixed(2)}) for a clean R:R ratio exceeding 1:2.
        `;
    } else {
        trendBadge.textContent = 'BEARISH';
        trendBadge.className = 'badge badge-auto';
        trendBadge.style.background = 'rgba(255, 56, 96, 0.1)';
        trendBadge.style.color = 'var(--red)';
        trendBadge.style.borderColor = 'rgba(255, 56, 96, 0.2)';

        typeBadge.textContent = 'SELL LIMIT';
        typeBadge.className = 'rec-type-badge sell';

        descEl.textContent = 'Sell the Rally';

        // Recommended Entry: between 50.0% and 61.8% (during correction upwards)
        const entryLow = Math.min(fib618, fib50);
        const entryHigh = Math.max(fib618, fib50);
        entryEl.textContent = `$${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)}`;

        // Recommended SL: Just above 78.6% (by 1% of the swing height)
        const recommendedSL = fib786 + (diff * 0.015);
        slEl.textContent = `$${recommendedSL.toFixed(2)}`;

        // Recommended TP: Previous swing Low (0%)
        tpEl.textContent = `$${low.toFixed(2)}`;

        analysisEl.innerHTML = `
            Gold displays a <strong>bearish structural advantage</strong> on the ${activeTimeframe.toUpperCase()} timeframe, trading below the 50% midpoint. 
            The most optimal strategy is to set a <strong>Sell Limit order on relief rallies near the Golden zone ($${entryLow.toFixed(2)} - $${entryHigh.toFixed(2)})</strong>. 
            Position Stop Loss just above the 78.6% retracement ($${recommendedSL.toFixed(2)}) to avoid spikes, targeting the Swing Low support ($${low.toFixed(2)}) for full profit.
        `;
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
    document.getElementById('spot-price').textContent = `$${latestPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    
    const rawTime = new Date(marketData.latest_time);
    document.getElementById('spot-time').textContent = `As of: ${rawTime.toLocaleString('en-US')}`;

    // 2. Update Period Cards
    const periodHigh = tfData.meta.high;
    const periodLow = tfData.meta.low;
    const range = periodHigh - periodLow;
    const rangePercent = (range / periodLow) * 100;

    document.getElementById('high-price').textContent = `$${periodHigh.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('low-price').textContent = `$${periodLow.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('range-val').textContent = `$${range.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('range-percentage').textContent = `+${rangePercent.toFixed(2)}%`;

    const tfLabel = activeTimeframe.toUpperCase();
    document.getElementById('high-label').textContent = `${tfLabel} Period High`;
    document.getElementById('low-label').textContent = `${tfLabel} Period Low`;
    document.getElementById('auto-tf-badge').textContent = tfLabel;

    // 3. Draw/Update Auto Fibonacci levels table
    const autoLevels = calculateFibonacciLevels(periodHigh, periodLow);
    const autoTbody = document.getElementById('auto-fibo-tbody');
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

    const activeLevels = isManualMode ? calculateFibonacciLevels(manualHigh, manualLow) : autoLevels;

    // 4. Generate AI recommendations
    generateTradingPlan(latestPrice, activeLevels);

    // 5. Update Positioning signals
    updateTradingSignals(latestPrice, activeLevels);

    // 6. Render Live Trades Portfolio
    renderPortfolio(latestPrice, activeLevels);

    // 7. Draw/Update Chart
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

    document.getElementById('custom-levels-result').classList.remove('hidden');
    
    updateDashboard();
}

// Reset custom and restore auto levels
function resetToAuto() {
    isManualMode = false;
    manualHigh = null;
    manualLow = null;
    
    document.getElementById('custom-high').value = '';
    document.getElementById('custom-low').value = '';
    document.getElementById('custom-levels-result').classList.add('hidden');
    
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
            borderColor: 'rgba(255,255,255,0.05)'
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
    const signalCard = document.getElementById('trading-signals-card');
    const content = document.getElementById('positioning-content');
    
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
