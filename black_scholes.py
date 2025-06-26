import numpy as np
from scipy.stats import norm
import math

def black_scholes_price(S, K, T, r, sigma):
    """
    Calculate Black-Scholes option prices for European Call and Put options.
    
    Parameters:
    S: Current stock price
    K: Strike price
    T: Time to expiry (in years)
    r: Risk-free rate
    sigma: Volatility
    
    Returns:
    tuple: (call_price, put_price)
    """
    if T <= 0:
        # Handle expiration case
        call_price = max(S - K, 0)
        put_price = max(K - S, 0)
        return call_price, put_price
    
    # Calculate d1 and d2
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option prices
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return call_price, put_price

def generate_pnl_surface(base_S, K, T, r, base_sigma, call_purchase, put_purchase, 
                        price_range=0.2, vol_range=0.2, grid_size=20):
    """
    Generate P&L surface for different stock prices and volatilities.
    
    Returns:
    dict: Contains 'stock_prices', 'volatilities', 'call_pnl', 'put_pnl'
    """
    # Create ranges
    min_price = base_S * (1 - price_range)
    max_price = base_S * (1 + price_range)
    min_vol = base_sigma * (1 - vol_range)
    max_vol = base_sigma * (1 + vol_range)
    
    stock_prices = np.linspace(min_price, max_price, grid_size)
    volatilities = np.linspace(min_vol, max_vol, grid_size)
    
    # Initialize P&L arrays
    call_pnl = np.zeros((len(volatilities), len(stock_prices)))
    put_pnl = np.zeros((len(volatilities), len(stock_prices)))
    
    # Calculate P&L for each combination
    for i, vol in enumerate(volatilities):
        for j, price in enumerate(stock_prices):
            call_price, put_price = black_scholes_price(price, K, T, r, vol)
            call_pnl[i, j] = call_price - call_purchase
            put_pnl[i, j] = put_price - put_purchase
    
    return {
        'stock_prices': stock_prices,
        'volatilities': volatilities,
        'call_pnl': call_pnl,
        'put_pnl': put_pnl
    }