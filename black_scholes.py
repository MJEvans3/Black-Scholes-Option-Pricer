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

def calculate_greeks(S, K, T, r, sigma):
    """Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho)"""
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Delta
    call_delta = norm.cdf(d1)
    put_delta = call_delta - 1
    
    # Gamma (same for calls and puts)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Theta
    call_theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T)) 
                  - r*K*np.exp(-r*T)*norm.cdf(d2))
    put_theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T)) 
                 + r*K*np.exp(-r*T)*norm.cdf(-d2))
    
    # Vega (same for calls and puts)
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    # Rho
    call_rho = K * T * np.exp(-r*T) * norm.cdf(d2)
    put_rho = -K * T * np.exp(-r*T) * norm.cdf(-d2)
    
    return {
        'call_delta': call_delta, 'put_delta': put_delta,
        'gamma': gamma, 'call_theta': call_theta/365, 'put_theta': put_theta/365,
        'vega': vega/100, 'call_rho': call_rho/100, 'put_rho': put_rho/100
    }

def generate_greeks_heatmaps(base_S, K, T, r, base_sigma, price_range=0.2, vol_range=0.2, grid_size=20):
    """
    Generate heatmaps for Delta, Gamma, and Vega.
    """
    min_price = base_S * (1 - price_range)
    max_price = base_S * (1 + price_range)
    min_vol = base_sigma * (1 - vol_range)
    max_vol = base_sigma * (1 + vol_range)
    
    stock_prices = np.linspace(min_price, max_price, grid_size)
    volatilities = np.linspace(min_vol, max_vol, grid_size)
    
    # Initialize Greeks arrays
    call_delta_grid = np.zeros((len(volatilities), len(stock_prices)))
    put_delta_grid = np.zeros((len(volatilities), len(stock_prices)))
    gamma_grid = np.zeros((len(volatilities), len(stock_prices)))
    vega_grid = np.zeros((len(volatilities), len(stock_prices)))

    for i, vol in enumerate(volatilities):
        for j, price in enumerate(stock_prices):
            greeks = calculate_greeks(price, K, T, r, vol)
            call_delta_grid[i, j] = greeks['call_delta']
            put_delta_grid[i, j] = greeks['put_delta']
            gamma_grid[i, j] = greeks['gamma']
            vega_grid[i, j] = greeks['vega']
            
    return {
        'stock_prices': stock_prices,
        'volatilities': volatilities,
        'call_delta': call_delta_grid,
        'put_delta': put_delta_grid,
        'gamma': gamma_grid,
        'vega': vega_grid
    }

def implied_volatility(option_price, S, K, T, r, option_type='call'):
    """
    Calculate the implied volatility using the Newton-Raphson method.
    
    Parameters:
    option_price: The market price of the option.
    S: Current stock price.
    K: Strike price.
    T: Time to expiry (in years).
    r: Risk-free rate.
    option_type: 'call' or 'put'.
    
    Returns:
    float: Implied volatility.
    """
    MAX_ITERATIONS = 100
    PRECISION = 1.0e-5
    
    sigma = 0.5 # Initial guess for volatility
    
    for i in range(MAX_ITERATIONS):
        call_price, put_price = black_scholes_price(S, K, T, r, sigma)
        
        if option_type == 'call':
            price = call_price
        else:
            price = put_price
            
        vega = calculate_greeks(S, K, T, r, sigma)['vega'] * 100 # Convert vega back to original scale
        
        price_difference = option_price - price
        
        if abs(price_difference) < PRECISION:
            return sigma
        
        if vega == 0: # Avoid division by zero
            break
            
        sigma = sigma - price_difference / vega
        
        if sigma < 0: # Volatility cannot be negative
            sigma = 0.001
            
    return sigma
