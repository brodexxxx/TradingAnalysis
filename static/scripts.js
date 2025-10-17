function analyze(symbol) {
    fetch(`/analyze/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('results').innerHTML = `<p>Error: ${data.error}</p>`;
                return;
            }
            document.getElementById('results').innerHTML = `
                <h2>${data.symbol}</h2>
                <p>Price: ${data.price.toFixed(2)}</p>
                <p>Action: <strong style="color: ${data.action === 'BUY' ? 'green' : data.action === 'SELL' ? 'red' : 'orange'}">${data.action}</strong></p>
                <p>Stop Loss: ${data.stop_loss ? data.stop_loss.toFixed(2) : 'N/A'}</p>
                <p>Take Profit: ${data.take_profit ? data.take_profit.toFixed(2) : 'N/A'}</p>
                <p>RSI: ${data.rsi.toFixed(2)}</p>
                <p>Phase: ${data.phase}</p>
                <p>Reason: ${data.reason}</p>
                <p><small>Analysis includes: RSI, MACD, Stochastic, OBV, Bollinger Bands, Range Filter, Support/Resistance, Market Phases, Patterns, Volume, Moving Averages</small></p>
            `;
            // For chart, assume we have data, but for simplicity, placeholder
            // In real app, fetch chart data separately
        })
        .catch(error => {
            document.getElementById('results').innerHTML = `<p>Error fetching data: ${error.message}</p>`;
        });
}

// Auto-refresh every 5 minutes
setInterval(() => {
    // Refresh all or current symbol
}, 300000);
