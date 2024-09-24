import ccxt

exchange = ccxt.binance()  # Выберите нужную биржу
ticker = exchange.fetch_ticker('TRX/USDT')  # Замените 'BTC' на нужную вам криптовалюту

print(ticker)