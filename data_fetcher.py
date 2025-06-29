import yfinance as yf

def get_options_chain(ticker):
    stock = yf.Ticker(ticker)
    expirations = stock.options

    chain = {}
    for expiration in expirations:
        opts = stock.option_chain(expiration)
        chain[expiration] = {
            'calls': opts.calls,
            'puts': opts.puts
        }
    return chain