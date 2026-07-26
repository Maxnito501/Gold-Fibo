// Global Application State
let marketData = null;
let activeTimeframe = 'h4';
let chartInstance = null;
let isManualMode = false;
let manualHigh = null;
let manualLow = null;

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

    // Custom Fibonacci Button
    document.getElementById('btn-calc-custom').addEventListener('click', calculateCustomFibo);
    
    // Reset Fibonacci Button
    document.getElementById('btn-reset-custom').addEventListener('click', resetToAuto);
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

// Update UI dashboard based on current state
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

    // Dynamic High/Low Card Labels based on active timeframe
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

    // 4. Update Positioning signals and insights
    updateTradingSignals(latestPrice, isManualMode ? calculateFibonacciLevels(manualHigh, manualLow) : autoLevels);

    // 5. Draw/Update Chart
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

    // Calculate levels
    const customLevels = calculateFibonacciLevels(manualHigh, manualLow);

    // Update manual levels UI table
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
    
    // Refresh dashboard visuals to draw manual annotations
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

    // Calculate Fibonacci levels for drawing line annotations on chart
    const fibLevels = calculateFibonacciLevels(meta.high, meta.low);
    
    // Chart options
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
