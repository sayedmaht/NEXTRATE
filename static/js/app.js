/**
 * NextRate AI — Main Application Logic
 * Handles navigation, data fetching, currency grids, converter, and modal
 */

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════

let cryptoData = [];
let fiatData = [];
let currentPage = 'dashboard';
let currentModalCurrency = null;
let currentModalType = null;

// Region mapping for fiat filtering
const REGIONS = {
    americas: ['USD', 'CAD', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN'],
    europe: ['EUR', 'GBP', 'CHF', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'ISK', 'UAH', 'RUB', 'TRY'],
    asia: ['JPY', 'CNY', 'INR', 'KRW', 'SGD', 'HKD', 'TWD', 'THB', 'IDR', 'MYR', 'PHP', 'VND', 'PKR', 'BDT', 'LKR'],
    other: ['AUD', 'NZD', 'ZAR', 'SAR', 'AED', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'ILS', 'EGP', 'NGN', 'KES', 'GHS', 'MAD', 'TND']
};

// ═══════════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    // Hide loader after 1.5s
    setTimeout(() => {
        const loader = document.getElementById('pageLoader');
        loader.classList.add('fade-out');
        setTimeout(() => loader.style.display = 'none', 500);
    }, 1500);
});

async function loadData() {
    try {
        const [cryptoRes, fiatRes] = await Promise.all([
            fetch('/api/crypto/list'),
            fetch('/api/fiat/rates')
        ]);

        if (cryptoRes.ok) {
            cryptoData = await cryptoRes.json();
        }
        if (fiatRes.ok) {
            fiatData = await fiatRes.json();
        }

        updateApiStatus(true);
        renderDashboard();
        renderFiatGrid(fiatData);
        renderCryptoGrid(cryptoData);
        populateConverterSelects();
    } catch (err) {
        console.error('Failed to load data:', err);
        updateApiStatus(false);
    }
}

function updateApiStatus(online) {
    const dot = document.getElementById('apiStatusDot');
    const text = document.getElementById('apiStatusText');
    if (online) {
        dot.classList.remove('offline');
        text.textContent = 'APIs Connected';
    } else {
        dot.classList.add('offline');
        text.textContent = 'API Error — Retrying...';
        // Retry after 10s
        setTimeout(loadData, 10000);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Navigation
// ═══════════════════════════════════════════════════════════════════════════════

function navigateTo(page) {
    currentPage = page;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Show/hide sections
    document.querySelectorAll('.page-section').forEach(sec => {
        sec.classList.remove('active');
    });
    const target = document.getElementById(`page-${page}`);
    if (target) target.classList.add('active');

    // Update title
    const titles = {
        dashboard: 'Dashboard',
        converter: 'Currency Converter',
        fiat: 'Fiat Currencies',
        crypto: 'Cryptocurrencies'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard
// ═══════════════════════════════════════════════════════════════════════════════

function renderDashboard() {
    // Stats
    document.getElementById('statTotalCryptos').textContent = cryptoData.length || '--';

    if (cryptoData.length > 0) {
        const totalMcap = cryptoData.reduce((sum, c) => sum + (c.market_cap || 0), 0);
        document.getElementById('statMarketCap').textContent = formatLargeNumber(totalMcap);
        
        // Find top gainer
        const sorted = [...cryptoData].sort((a, b) => (b.price_change_24h || 0) - (a.price_change_24h || 0));
        if (sorted.length) {
            document.getElementById('statTopMover').textContent = sorted[0].symbol;
            const ch = sorted[0].price_change_24h || 0;
            const el = document.getElementById('statTopMoverChange');
            el.textContent = `${ch >= 0 ? '↑' : '↓'} ${Math.abs(ch).toFixed(2)}%`;
            el.className = `stat-change ${ch >= 0 ? 'positive' : 'negative'}`;
        }

        // Average change for market
        const avgChange = cryptoData.reduce((s, c) => s + (c.price_change_24h || 0), 0) / cryptoData.length;
        const mEl = document.getElementById('statMarketChange');
        mEl.textContent = `${avgChange >= 0 ? '↑' : '↓'} ${Math.abs(avgChange).toFixed(2)}%`;
        mEl.className = `stat-change ${avgChange >= 0 ? 'positive' : 'negative'}`;
    }

    // Top 8 crypto cards
    const topCrypto = cryptoData.slice(0, 8);
    const cryptoGrid = document.getElementById('dashboardCryptoGrid');
    cryptoGrid.innerHTML = topCrypto.map(coin => createCryptoCard(coin)).join('');

    // Top 8 fiat cards
    const topFiat = fiatData.slice(0, 8);
    const fiatGrid = document.getElementById('dashboardFiatGrid');
    fiatGrid.innerHTML = topFiat.map(cur => createFiatCard(cur)).join('');
}

// ═══════════════════════════════════════════════════════════════════════════════
// Currency Cards
// ═══════════════════════════════════════════════════════════════════════════════

function createCryptoCard(coin) {
    const change = coin.price_change_24h || 0;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeIcon = change >= 0 ? '▲' : '▼';
    const sparkId = `spark-${coin.id}`;

    return `
        <div class="currency-card" onclick="openModal('${coin.id}', 'crypto')">
            <div class="currency-card-header">
                <div class="currency-info">
                    <div class="currency-icon">
                        <img src="${coin.image}" alt="${coin.name}" loading="lazy" onerror="this.parentElement.textContent='🪙'">
                    </div>
                    <div>
                        <div class="currency-name">${coin.name}</div>
                        <div class="currency-symbol">${coin.symbol}</div>
                    </div>
                </div>
                <span class="currency-rank">#${coin.market_cap_rank || '--'}</span>
            </div>
            <div class="currency-card-body">
                <div class="currency-price">${formatPrice(coin.current_price)}</div>
                <div class="currency-change ${changeClass}">
                    ${changeIcon} ${Math.abs(change).toFixed(2)}%
                </div>
            </div>
            <div class="currency-sparkline">
                <canvas id="${sparkId}" data-spark='${JSON.stringify((coin.sparkline || []).slice(-24))}'></canvas>
            </div>
        </div>
    `;
}

function createFiatCard(cur) {
    const change = cur.change_24h || 0;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeIcon = change >= 0 ? '▲' : '▼';

    return `
        <div class="currency-card" onclick="openModal('${cur.code}', 'fiat')">
            <div class="currency-card-header">
                <div class="currency-info">
                    <div class="currency-icon">${cur.flag}</div>
                    <div>
                        <div class="currency-name">${cur.name}</div>
                        <div class="currency-symbol">${cur.code}</div>
                    </div>
                </div>
            </div>
            <div class="currency-card-body">
                <div class="currency-price">${cur.symbol}${cur.rate ? cur.rate.toFixed(4) : '--'}</div>
                <div class="currency-change ${changeClass}">
                    ${changeIcon} ${Math.abs(change).toFixed(2)}%
                </div>
            </div>
        </div>
    `;
}

// After rendering, draw sparklines
function drawAllSparklines() {
    document.querySelectorAll('.currency-sparkline canvas').forEach(canvas => {
        const data = JSON.parse(canvas.dataset.spark || '[]');
        if (data.length > 2) {
            drawMiniSparkline(canvas, data);
        }
    });
}

function drawMiniSparkline(canvas, data) {
    const ctx = canvas.getContext('2d');
    const w = canvas.parentElement.offsetWidth;
    const h = 40;
    canvas.width = w * 2;
    canvas.height = h * 2;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.scale(2, 2);

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    const isUp = data[data.length - 1] >= data[0];
    const color = isUp ? '#22c55e' : '#ef4444';

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';

    data.forEach((val, i) => {
        const x = (i / (data.length - 1)) * w;
        const y = h - ((val - min) / range) * (h - 4) - 2;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Gradient fill
    const grd = ctx.createLinearGradient(0, 0, 0, h);
    grd.addColorStop(0, isUp ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)');
    grd.addColorStop(1, 'rgba(0,0,0,0)');

    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fillStyle = grd;
    ctx.fill();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Render Grids
// ═══════════════════════════════════════════════════════════════════════════════

function renderCryptoGrid(data) {
    const grid = document.getElementById('cryptoGrid');
    if (!data.length) {
        grid.innerHTML = '<div class="no-results"><div class="emoji">🔍</div><p>No cryptocurrencies found</p></div>';
        return;
    }
    grid.innerHTML = data.map(coin => createCryptoCard(coin)).join('');
    setTimeout(drawAllSparklines, 100);
}

function renderFiatGrid(data) {
    const grid = document.getElementById('fiatGrid');
    if (!data.length) {
        grid.innerHTML = '<div class="no-results"><div class="emoji">🔍</div><p>No currencies found</p></div>';
        return;
    }
    grid.innerHTML = data.map(cur => createFiatCard(cur)).join('');
}

// Filters
function filterCrypto(filter, btn) {
    btn.parentElement.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    let filtered = [...cryptoData];
    switch (filter) {
        case 'top20': filtered = filtered.slice(0, 20); break;
        case 'gainers': filtered = filtered.filter(c => (c.price_change_24h || 0) > 0).sort((a, b) => b.price_change_24h - a.price_change_24h); break;
        case 'losers': filtered = filtered.filter(c => (c.price_change_24h || 0) < 0).sort((a, b) => a.price_change_24h - b.price_change_24h); break;
    }
    renderCryptoGrid(filtered);
}

function filterFiat(filter, btn) {
    btn.parentElement.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    let filtered = [...fiatData];
    if (filter !== 'all') {
        const codes = REGIONS[filter] || [];
        filtered = filtered.filter(c => codes.includes(c.code));
    }
    renderFiatGrid(filtered);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Search
// ═══════════════════════════════════════════════════════════════════════════════

function handleGlobalSearch(query) {
    const q = query.trim().toLowerCase();
    if (!q) {
        renderCryptoGrid(cryptoData);
        renderFiatGrid(fiatData);
        return;
    }

    if (currentPage === 'crypto' || currentPage === 'dashboard') {
        const filtered = cryptoData.filter(c =>
            c.name.toLowerCase().includes(q) || c.symbol.toLowerCase().includes(q)
        );
        renderCryptoGrid(filtered);
    }

    if (currentPage === 'fiat' || currentPage === 'dashboard') {
        const filtered = fiatData.filter(c =>
            c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q) || c.country.toLowerCase().includes(q)
        );
        renderFiatGrid(filtered);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Converter
// ═══════════════════════════════════════════════════════════════════════════════

function populateConverterSelects() {
    const fromFiat = document.getElementById('convertFromFiat');
    const fromCrypto = document.getElementById('convertFromCrypto');
    const toFiat = document.getElementById('convertToFiat');
    const toCrypto = document.getElementById('convertToCrypto');

    // Fiat options
    const fiatOpts = fiatData.map(c => `<option value="${c.code}">${c.flag} ${c.code} — ${c.name}</option>`).join('');
    fromFiat.innerHTML = fiatOpts;
    toFiat.innerHTML = fiatOpts;

    // Crypto options
    const cryptoOpts = cryptoData.map(c => `<option value="${c.symbol}">${c.symbol} — ${c.name}</option>`).join('');
    fromCrypto.innerHTML = cryptoOpts;
    toCrypto.innerHTML = cryptoOpts;

    // Default: USD -> EUR
    document.getElementById('convertFrom').value = 'USD';
    document.getElementById('convertTo').value = 'EUR';
}

async function performConversion() {
    const amount = parseFloat(document.getElementById('convertAmount').value) || 0;
    const from = document.getElementById('convertFrom').value;
    const to = document.getElementById('convertTo').value;

    if (amount <= 0 || !from || !to) return;

    try {
        const resp = await fetch(`/api/convert?from=${from}&to=${to}&amount=${amount}`);
        if (resp.ok) {
            const data = await resp.json();
            document.getElementById('convertResult').value = data.result;
            document.getElementById('resultDisplay').textContent = `${data.result.toLocaleString()} ${to}`;
            document.getElementById('resultRate').textContent = `1 ${from} = ${data.rate} ${to}`;
            document.getElementById('converterResultBox').style.display = 'block';
        }
    } catch (err) {
        console.error('Conversion failed:', err);
    }
}

function swapCurrencies() {
    const fromEl = document.getElementById('convertFrom');
    const toEl = document.getElementById('convertTo');
    const temp = fromEl.value;
    fromEl.value = toEl.value;
    toEl.value = temp;
    performConversion();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Modal
// ═══════════════════════════════════════════════════════════════════════════════

function openModal(id, type) {
    currentModalType = type;
    const modal = document.getElementById('currencyModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    if (type === 'crypto') {
        currentModalCurrency = cryptoData.find(c => c.id === id);
        if (!currentModalCurrency) return;

        document.getElementById('modalIcon').innerHTML = `<img src="${currentModalCurrency.image}" alt="${currentModalCurrency.name}">`;
        document.getElementById('modalName').textContent = currentModalCurrency.name;
        document.getElementById('modalSymbol').textContent = currentModalCurrency.symbol;

        // Overview
        const grid = document.getElementById('overviewGrid');
        grid.innerHTML = `
            <div class="overview-item"><div class="label">Price</div><div class="value">${formatPrice(currentModalCurrency.current_price)}</div></div>
            <div class="overview-item"><div class="label">Market Cap</div><div class="value">${formatLargeNumber(currentModalCurrency.market_cap)}</div></div>
            <div class="overview-item"><div class="label">24h Volume</div><div class="value">${formatLargeNumber(currentModalCurrency.total_volume)}</div></div>
            <div class="overview-item"><div class="label">24h Change</div><div class="value ${(currentModalCurrency.price_change_24h || 0) >= 0 ? 'text-green' : 'text-red'}">${(currentModalCurrency.price_change_24h || 0).toFixed(2)}%</div></div>
            <div class="overview-item"><div class="label">Circulating Supply</div><div class="value">${formatLargeNumber(currentModalCurrency.circulating_supply)}</div></div>
            <div class="overview-item"><div class="label">Total Supply</div><div class="value">${currentModalCurrency.total_supply ? formatLargeNumber(currentModalCurrency.total_supply) : '∞'}</div></div>
            <div class="overview-item"><div class="label">All-Time High</div><div class="value">${formatPrice(currentModalCurrency.ath)}</div></div>
            <div class="overview-item"><div class="label">All-Time Low</div><div class="value">${formatPrice(currentModalCurrency.atl)}</div></div>
            <div class="overview-item"><div class="label">Rank</div><div class="value">#${currentModalCurrency.market_cap_rank || '--'}</div></div>
        `;
    } else {
        currentModalCurrency = fiatData.find(c => c.code === id);
        if (!currentModalCurrency) return;

        document.getElementById('modalIcon').innerHTML = currentModalCurrency.flag;
        document.getElementById('modalName').textContent = currentModalCurrency.name;
        document.getElementById('modalSymbol').textContent = `${currentModalCurrency.code} — ${currentModalCurrency.country}`;

        const grid = document.getElementById('overviewGrid');
        grid.innerHTML = `
            <div class="overview-item"><div class="label">Exchange Rate (vs USD)</div><div class="value">${currentModalCurrency.rate ? currentModalCurrency.rate.toFixed(6) : '--'}</div></div>
            <div class="overview-item"><div class="label">Price in USD</div><div class="value">$${currentModalCurrency.price_usd ? currentModalCurrency.price_usd.toFixed(6) : '--'}</div></div>
            <div class="overview-item"><div class="label">24h Change</div><div class="value ${(currentModalCurrency.change_24h || 0) >= 0 ? 'text-green' : 'text-red'}">${(currentModalCurrency.change_24h || 0).toFixed(2)}%</div></div>
            <div class="overview-item"><div class="label">Country</div><div class="value">${currentModalCurrency.country}</div></div>
            <div class="overview-item"><div class="label">Symbol</div><div class="value">${currentModalCurrency.symbol}</div></div>
            <div class="overview-item"><div class="label">Currency Code</div><div class="value">${currentModalCurrency.code}</div></div>
        `;
    }

    // Reset to overview tab
    switchModalTab('overview', document.querySelector('.modal-tab'));
}

function closeModal() {
    document.getElementById('currencyModal').classList.remove('active');
    document.body.style.overflow = '';
    currentModalCurrency = null;
    currentModalType = null;
    // Destroy charts
    if (window.historyChartInstance) {
        window.historyChartInstance.destroy();
        window.historyChartInstance = null;
    }
    if (window.predictionChartInstance) {
        window.predictionChartInstance.destroy();
        window.predictionChartInstance = null;
    }
}

function switchModalTab(tab, btn) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');

    if (tab === 'history' && currentModalCurrency) {
        loadHistory(30, document.querySelector('.chart-timeframe-btn.active'));
    }
    if (tab === 'prediction' && currentModalCurrency) {
        loadPrediction();
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utility
// ═══════════════════════════════════════════════════════════════════════════════

function formatPrice(price) {
    if (price == null) return '--';
    if (price >= 1) return '$' + price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 0.01) return '$' + price.toFixed(4);
    return '$' + price.toFixed(8);
}

function formatLargeNumber(num) {
    if (num == null) return '--';
    if (num >= 1e12) return '$' + (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return '$' + (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return '$' + (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return '$' + (num / 1e3).toFixed(2) + 'K';
    return '$' + num.toFixed(2);
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'currencyModal') closeModal();
});

// Escape key closes modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});
