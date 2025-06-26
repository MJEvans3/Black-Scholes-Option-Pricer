import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from black_scholes import black_scholes_price, generate_pnl_surface
from database_manager import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Black-Scholes P&L Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()

# Title
st.title("📈 Black-Scholes Option Pricer with P&L Analysis")
st.markdown("Interactive tool for pricing European options and analyzing P&L scenarios")

# Sidebar for inputs
st.sidebar.header("Option Parameters")

# Core Black-Scholes inputs
stock_price = st.sidebar.number_input("Current Stock Price ($)", value=100.0, min_value=0.01, step=1.0)
strike_price = st.sidebar.number_input("Strike Price ($)", value=100.0, min_value=0.01, step=1.0)
time_to_expiry = st.sidebar.number_input("Time to Expiry (years)", value=0.25, min_value=0.01, max_value=5.0, step=0.01)
volatility = st.sidebar.number_input("Volatility (σ)", value=0.2, min_value=0.01, max_value=2.0, step=0.01)
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (r)", value=0.05, min_value=0.0, max_value=0.5, step=0.01)

st.sidebar.divider()
st.sidebar.header("Purchase Prices for P&L")

call_purchase_price = st.sidebar.number_input("Call Purchase Price ($)", value=5.0, min_value=0.0, step=0.1)
put_purchase_price = st.sidebar.number_input("Put Purchase Price ($)", value=3.0, min_value=0.0, step=0.1)

st.sidebar.divider()
st.sidebar.header("Heat Map Configuration")

price_range = st.sidebar.slider("Stock Price Range (±%)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)
vol_range = st.sidebar.slider("Volatility Range (±%)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)
grid_size = st.sidebar.selectbox("Grid Resolution", [15, 20, 25, 30], index=1)

# Calculate button
calculate_button = st.sidebar.button("🔄 Calculate P&L", type="primary", use_container_width=True)

if calculate_button:
    # Calculate base option prices
    call_price, put_price = black_scholes_price(stock_price, strike_price, time_to_expiry, risk_free_rate, volatility)
    
    # Calculate base P&L
    base_call_pnl = call_price - call_purchase_price
    base_put_pnl = put_price - put_purchase_price
    
    # Generate P&L surface
    pnl_data = generate_pnl_surface(
        stock_price, strike_price, time_to_expiry, risk_free_rate, volatility,
        call_purchase_price, put_purchase_price, price_range, vol_range, grid_size
    )
    
    # Display results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Call Option Price", f"${call_price:.2f}")
    with col2:
        st.metric("Put Option Price", f"${put_price:.2f}")
    with col3:
        color = "normal" if base_call_pnl >= 0 else "inverse"
        st.metric("Call P&L", f"${base_call_pnl:.2f}", delta=f"{base_call_pnl:.2f}")
    with col4:
        color = "normal" if base_put_pnl >= 0 else "inverse"
        st.metric("Put P&L", f"${base_put_pnl:.2f}", delta=f"{base_put_pnl:.2f}")
    
    # Create heat maps
    st.subheader("P&L Heat Maps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Call Option P&L**")
        fig_call = go.Figure(data=go.Heatmap(
            z=pnl_data['call_pnl'],
            x=pnl_data['stock_prices'],
            y=pnl_data['volatilities'],
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="P&L ($)")
        ))
        fig_call.update_layout(
            title="Call Option P&L",
            xaxis_title="Stock Price ($)",
            yaxis_title="Volatility",
            height=400
        )
        st.plotly_chart(fig_call, use_container_width=True)
    
    with col2:
        st.write("**Put Option P&L**")
        fig_put = go.Figure(data=go.Heatmap(
            z=pnl_data['put_pnl'],
            x=pnl_data['stock_prices'],
            y=pnl_data['volatilities'],
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="P&L ($)")
        ))
        fig_put.update_layout(
            title="Put Option P&L",
            xaxis_title="Stock Price ($)",
            yaxis_title="Volatility",
            height=400
        )
        st.plotly_chart(fig_put, use_container_width=True)
    
    # Save to database
    inputs = {
        'stock_price': stock_price,
        'strike_price': strike_price,
        'time_to_expiry': time_to_expiry,
        'volatility': volatility,
        'risk_free_rate': risk_free_rate,
        'call_purchase_price': call_purchase_price,
        'put_purchase_price': put_purchase_price
    }
    
    calculation_id = db.save_calculation(inputs, pnl_data)
    st.success(f"✅ Calculation saved! ID: {calculation_id[:8]}...")

# Show calculation history
st.subheader("📊 Recent Calculations")
history = db.get_calculation_history(limit=5)

if not history.empty:
    # Format the history for display
    history['timestamp'] = pd.to_datetime(history['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    display_history = history[[
        'timestamp', 'base_stock_price', 'strike_price', 
        'volatility', 'call_purchase_price', 'put_purchase_price'
    ]].copy()
    display_history.columns = [
        'Time', 'Stock Price', 'Strike', 'Volatility', 'Call Purchase', 'Put Purchase'
    ]
    st.dataframe(display_history, use_container_width=True)
else:
    st.info("No calculations yet. Click 'Calculate P&L' to get started!")

# Instructions
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    **Black-Scholes Parameters:**
    - **Stock Price**: Current market price of the underlying asset
    - **Strike Price**: Exercise price of the option
    - **Time to Expiry**: Time remaining until option expiration (in years)
    - **Volatility**: Expected volatility of the underlying asset (as decimal, e.g., 0.2 = 20%)
    - **Risk-Free Rate**: Risk-free interest rate (as decimal, e.g., 0.05 = 5%)
    
    **P&L Analysis:**
    - **Purchase Prices**: The prices you paid for the call and put options
    - **Heat Maps**: Show profit/loss across different stock prices and volatilities
    - **Green**: Profitable scenarios
    - **Red**: Loss scenarios
    
    **Heat Map Configuration:**
    - **Price Range**: How much the stock price varies (±% from current price)
    - **Volatility Range**: How much volatility varies (±% from current volatility)
    - **Grid Resolution**: Number of points in each dimension (higher = more detailed)
    """)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Black-Scholes Model • Real-time P&L Analysis")