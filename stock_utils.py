import re

import yfinance


def get_ticker(ticker_symbol):
    return yfinance.Ticker(ticker_symbol)


def get_last_price(ticker):
    last_price = ticker.history().tail(1)["Close"].iloc[0]
    return round(last_price, 2)


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def camel_to_sentence(name):
    snake_name = camel_to_snake(name)
    return snake_name.replace("_", " ").capitalize()
