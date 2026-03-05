/**
 * NextRate AI — Charts Module
 * Historical price charts and AI prediction charts using Chart.js
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Historical Chart
// ═══════════════════════════════════════════════════════════════════════════════

async function loadHistory(days, btn) {
    // Update active button
    if (btn) {
        document.querySelectorAll('.chart-timeframe-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    if (!currentModalCurrency) return;

    const canvas = document.getElementById('historyChart');
    const ctx = canvas.getContext('2d');

    // Show loading
    if (window.historyChartInstance) {
        window.historyChartInstance.destroy();
    }

    let url;
    if (currentModalType === 'crypto') {
        url = `/api/crypto/${currentModalCurrency.id}/history?days=${days}`;
    } else {
        url = `/api/fiat/history/USD/${currentModalCurrency.code}`;
    }

    try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error('API error');
        const data = await resp.json();

        const labels = data.map(p => {
            const d = new Date(p.date);
            if (days <= 7) return d.toLocaleDateString('en', { weekday: 'short' });
            if (days <= 30) return d.toLocaleDateString('en', { month: 'short', day: 'numeric' });
            return d.toLocaleDateString('en', { month: 'short', year: '2-digit' });
        });
        const prices = data.map(p => p.price);

        const isUp = prices[prices.length - 1] >= prices[0];
        const lineColor = isUp ? '#22c55e' : '#ef4444';

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, isUp ? 'rgba(34, 197, 94, 0.25)' : 'rgba(239, 68, 68, 0.25)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

        window.historyChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: prices,
                    borderColor: lineColor,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: lineColor,
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2,
                }]
            },
            options: getChartOptions('Price')
        });
    } catch (err) {
        console.error('Failed to load history:', err);
    }
}


// ═══════════════════════════════════════════════════════════════════════════════
// AI Prediction Chart
// ═══════════════════════════════════════════════════════════════════════════════

async function loadPrediction() {
    if (!currentModalCurrency) return;

    const canvas = document.getElementById('predictionChart');
    const ctx = canvas.getContext('2d');

    if (window.predictionChartInstance) {
        window.predictionChartInstance.destroy();
    }

    // Show loading state
    document.getElementById('predictionInfo').innerHTML = `
        <div class="prediction-card">
            <div class="pred-label">Loading prediction...</div>
            <div class="pred-value"><span class="loading-spinner"></span></div>
        </div>
    `;
    document.getElementById('predictionAnalysis').style.display = 'none';
    document.getElementById('predictionFactors').style.display = 'none';

    const body = {
        currency: currentModalType === 'crypto' ? currentModalCurrency.name : currentModalCurrency.code,
        type: currentModalType,
        current_price: currentModalType === 'crypto' ? currentModalCurrency.current_price : currentModalCurrency.rate,
        market_data: currentModalType === 'crypto' ? {
            market_cap: currentModalCurrency.market_cap,
            total_volume: currentModalCurrency.total_volume,
            circulating_supply: currentModalCurrency.circulating_supply,
            total_supply: currentModalCurrency.total_supply,
            max_supply: currentModalCurrency.max_supply,
            price_change_24h: currentModalCurrency.price_change_24h,
            ath: currentModalCurrency.ath,
            atl: currentModalCurrency.atl,
        } : {
            price_change_24h: currentModalCurrency.change_24h,
        }
    };

    try {
        const resp = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!resp.ok) throw new Error('Prediction API error');
        const prediction = await resp.json();

        renderPredictionInfo(prediction);
        renderPredictionChart(ctx, prediction);
    } catch (err) {
        console.error('Prediction failed:', err);
        document.getElementById('predictionInfo').innerHTML = `
            <div class="prediction-card" style="grid-column: 1 / -1;">
                <div class="pred-label">Error</div>
                <div class="pred-value text-red">Failed to load prediction. Please try again.</div>
            </div>
        `;
    }
}

function renderPredictionInfo(prediction) {
    const trendClass = prediction.trend || 'neutral';
    const confColor = {
        high: 'text-green',
        medium: 'text-accent',
        low: 'text-red'
    }[prediction.confidence] || 'text-accent';

    document.getElementById('predictionInfo').innerHTML = `
        <div class="prediction-card">
            <div class="pred-label">AI Trend</div>
            <div class="pred-value ${trendClass}">${(prediction.trend || 'N/A').toUpperCase()}</div>
        </div>
        <div class="prediction-card">
            <div class="pred-label">Confidence</div>
            <div class="pred-value ${confColor}">${(prediction.confidence || 'N/A').toUpperCase()}</div>
        </div>
    `;

    // Analysis
    if (prediction.analysis) {
        const analysisEl = document.getElementById('predictionAnalysis');
        analysisEl.innerHTML = `
            <div class="ai-badge">🤖 AI Analysis</div>
            <p>${prediction.analysis}</p>
        `;
        analysisEl.style.display = 'block';
    }

    // Factors
    if (prediction.factors && prediction.factors.length) {
        const factorsEl = document.getElementById('predictionFactors');
        factorsEl.innerHTML = `
            <h4>Key Factors</h4>
            ${prediction.factors.map(f => `
                <div class="factor-item">
                    <div class="factor-dot"></div>
                    <span>${f}</span>
                </div>
            `).join('')}
        `;
        factorsEl.style.display = 'block';
    }
}

function renderPredictionChart(ctx, prediction) {
    const currentPrice = currentModalType === 'crypto'
        ? currentModalCurrency.current_price
        : currentModalCurrency.rate;

    const predictions = prediction.prediction_30d || [];
    if (!predictions.length) return;

    // Build labels: Today + next 30 days
    const labels = [];
    const now = new Date();
    for (let i = 0; i <= predictions.length; i++) {
        const d = new Date(now);
        d.setDate(d.getDate() + i);
        labels.push(d.toLocaleDateString('en', { month: 'short', day: 'numeric' }));
    }

    // Dataset: current price + predictions
    const allPrices = [currentPrice, ...predictions];

    // Upper/lower confidence bands
    const bandWidth = currentPrice * 0.02;
    const upperBand = allPrices.map((p, i) => p + bandWidth * (1 + i * 0.1));
    const lowerBand = allPrices.map((p, i) => Math.max(0, p - bandWidth * (1 + i * 0.1)));

    const isUp = predictions[predictions.length - 1] >= currentPrice;
    const lineColor = isUp ? '#22c55e' : '#ef4444';
    const bandColor = isUp ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)';

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, isUp ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    window.predictionChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Upper Band',
                    data: upperBand,
                    borderColor: 'transparent',
                    backgroundColor: bandColor,
                    fill: '+1',
                    pointRadius: 0,
                    tension: 0.4,
                },
                {
                    label: 'Predicted Price',
                    data: allPrices,
                    borderColor: lineColor,
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    borderDash: [6, 3],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: lineColor,
                },
                {
                    label: 'Lower Band',
                    data: lowerBand,
                    borderColor: 'transparent',
                    backgroundColor: 'transparent',
                    fill: false,
                    pointRadius: 0,
                    tension: 0.4,
                },
            ]
        },
        options: {
            ...getChartOptions('Predicted Price'),
            plugins: {
                ...getChartOptions('Predicted Price').plugins,
                annotation: {
                    annotations: {
                        todayLine: {
                            type: 'line',
                            xMin: 0,
                            xMax: 0,
                            borderColor: 'rgba(168, 85, 247, 0.5)',
                            borderWidth: 2,
                            borderDash: [4, 4],
                            label: {
                                display: true,
                                content: 'Today',
                                position: 'start'
                            }
                        }
                    }
                }
            }
        }
    });
}


// ═══════════════════════════════════════════════════════════════════════════════
// Chart Options (shared dark theme)
// ═══════════════════════════════════════════════════════════════════════════════

function getChartOptions(label) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index',
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 21, 56, 0.95)',
                titleColor: '#e8eaed',
                bodyColor: '#9aa0b8',
                borderColor: 'rgba(108, 92, 231, 0.3)',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 10,
                displayColors: false,
                titleFont: { family: 'Inter', weight: '600' },
                bodyFont: { family: 'JetBrains Mono', size: 13 },
                callbacks: {
                    label: function (ctx) {
                        return `${label}: ${formatPrice(ctx.raw)}`;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(108, 92, 231, 0.05)',
                    drawBorder: false,
                },
                ticks: {
                    color: '#5a6178',
                    font: { family: 'Inter', size: 11 },
                    maxRotation: 0,
                    maxTicksLimit: 8,
                }
            },
            y: {
                grid: {
                    color: 'rgba(108, 92, 231, 0.05)',
                    drawBorder: false,
                },
                ticks: {
                    color: '#5a6178',
                    font: { family: 'JetBrains Mono', size: 11 },
                    callback: function (val) {
                        return formatPrice(val);
                    }
                }
            }
        }
    };
}
