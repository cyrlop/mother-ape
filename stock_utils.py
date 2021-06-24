import yfinance


def get_ticker(ticker_symbol):
    return yfinance.Ticker(ticker_symbol)


def get_last_price(ticker):
    last_price = ticker.history().tail(1)["Close"].iloc[0]
    return round(last_price, 2)
