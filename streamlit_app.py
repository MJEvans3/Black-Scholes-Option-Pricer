import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import json
from black_scholes import black_scholes_price, generate_pnl_surface, calculate_greeks, generate_greeks_heatmaps, implied_volatility
from database_manager import DatabaseManager
from data_fetcher import get_options_chain
from ai_chat import get_ai_response

# --- Page Configuration ---
st.set_page_config(
    page_title="Black-Scholes P&L Analyzer",
    page_icon="📈",
    layout="wide"
)

# --- Initialization ---
@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()

# Initialize session state for calculations
def init_session_state():
    if 'calculations_done' not in st.session_state:
        st.session_state.calculations_done = False
    if 'positions' not in st.session_state:
        st.session_state.positions = []
    if 'individual_pnl' not in st.session_state:
        st.session_state.individual_pnl = []
    if 'total_pnl' not in st.session_state:
        st.session_state.total_pnl = {'call': 0, 'put': 0}
    if 'total_greeks' not in st.session_state:
        st.session_state.total_greeks = {
            'call_delta': 0, 'put_delta': 0, 'gamma': 0, 
            'call_theta': 0, 'put_theta': 0, 'vega': 0, 
            'call_rho': 0, 'put_rho': 0
        }
    if 'heatmap_data' not in st.session_state:
        st.session_state.heatmap_data = {}

init_session_state()

# --- Sidebar ---
st.sidebar.header("Portfolio Positions")

if st.sidebar.button("Add Position"):
    st.session_state.positions.append({
        'stock_price': 100.0,
        'strike_price': 100.0,
        'time_to_expiry': 0.25,
        'volatility': 0.2,
        'risk_free_rate': 0.05,
        'quantity': 1
    })

for i, position in enumerate(st.session_state.positions):
    with st.sidebar.expander(f"Position {i+1}", expanded=True):
        st.session_state.positions[i]['stock_price'] = st.number_input(f"Stock Price ($)##{i}", value=position['stock_price'], min_value=0.01, step=1.0)
        st.session_state.positions[i]['strike_price'] = st.number_input(f"Strike Price ($)##{i}", value=position['strike_price'], min_value=0.01, step=1.0)
        st.session_state.positions[i]['time_to_expiry'] = st.number_input(f"Time to Expiry (years)##{i}", value=position['time_to_expiry'], min_value=0.01, max_value=5.0, step=0.01)
        st.session_state.positions[i]['volatility'] = st.number_input(f"Volatility (σ)##{i}", value=position['volatility'], min_value=0.01, max_value=2.0, step=0.01)
        st.session_state.positions[i]['risk_free_rate'] = st.number_input(f"Risk-Free Rate (r)##{i}", value=position['risk_free_rate'], min_value=0.0, max_value=0.5, step=0.01)
        st.session_state.positions[i]['quantity'] = st.number_input(f"Quantity##{i}", value=position['quantity'], min_value=1, step=1)
        if st.button(f"Remove Position {i+1}", key=f"remove_{i}"):
            st.session_state.positions.pop(i)
            st.experimental_rerun()

st.sidebar.divider()
st.sidebar.header("Purchase Prices for P&L")
call_purchase_price = st.sidebar.number_input("Call Purchase Price ($)", value=5.0, min_value=0.0, step=0.1)
put_purchase_price = st.sidebar.number_input("Put Purchase Price ($)", value=3.0, min_value=0.0, step=0.1)

st.sidebar.divider()
st.sidebar.header("Heat Map Configuration")
price_range = st.sidebar.slider("Stock Price Range (±%)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)
vol_range = st.sidebar.slider("Volatility Range (±%)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)
grid_size = st.sidebar.selectbox("Grid Resolution", [15, 20, 25, 30], index=1)

# --- Calculation Logic ---
def perform_calculations():
    if st.session_state.positions:
        st.session_state.individual_pnl = []
        st.session_state.total_pnl = {'call': 0, 'put': 0}
        st.session_state.total_greeks = {key: 0 for key in st.session_state.total_greeks}

        for i, position in enumerate(st.session_state.positions):
            call_price, put_price = black_scholes_price(position['stock_price'], position['strike_price'], position['time_to_expiry'], position['risk_free_rate'], position['volatility'])
            base_call_pnl = call_price - call_purchase_price
            base_put_pnl = put_price - put_purchase_price
            
            st.session_state.individual_pnl.append({
                'position': i + 1,
                'quantity': position['quantity'],
                'call_price': call_price,
                'put_price': put_price,
                'call_pnl': base_call_pnl,
                'put_pnl': base_put_pnl
            })

            greeks = calculate_greeks(position['stock_price'], position['strike_price'], position['time_to_expiry'], position['risk_free_rate'], position['volatility'])
            for key in st.session_state.total_greeks:
                st.session_state.total_greeks[key] += greeks[key] * position['quantity']

            st.session_state.total_pnl['call'] += base_call_pnl * position['quantity']
            st.session_state.total_pnl['put'] += base_put_pnl * position['quantity']

        first_pos = st.session_state.positions[0]
        pnl_surface_data = generate_pnl_surface(
            first_pos['stock_price'], first_pos['strike_price'], first_pos['time_to_expiry'],
            first_pos['risk_free_rate'], first_pos['volatility'],
            call_purchase_price, put_purchase_price, price_range, vol_range, grid_size
        )
        greeks_heatmap_data = generate_greeks_heatmaps(
            first_pos['stock_price'], first_pos['strike_price'], first_pos['time_to_expiry'],
            first_pos['risk_free_rate'], first_pos['volatility'],
            price_range, vol_range, grid_size
        )
        st.session_state.heatmap_data = {
            'pnl': pnl_surface_data,
            'greeks': greeks_heatmap_data,
            'greeks_first_pos': calculate_greeks(first_pos['stock_price'], first_pos['strike_price'], first_pos['time_to_expiry'], first_pos['risk_free_rate'], first_pos['volatility'])
        }
        
        st.session_state.calculations_done = True
    else:
        st.warning("Please add at least one position to calculate P&L and Greeks.")
        st.session_state.calculations_done = False

if st.sidebar.button("🔄 Calculate P&L", type="primary", use_container_width=True):
    perform_calculations()

# --- Main Page Display ---
st.title("📈 Black-Scholes Option Pricer with P&L Analysis")

if st.session_state.calculations_done:
    st.subheader("Individual Position Prices & P&L")
    for pnl in st.session_state.individual_pnl:
        st.write(f"**Position {pnl['position']} (Quantity: {pnl['quantity']})**")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Call Price", f"${pnl['call_price']:.2f}")
        col2.metric("Put Price", f"${pnl['put_price']:.2f}")
        col3.metric("Call P&L", f"${pnl['call_pnl']:.2f}", delta=f"{pnl['call_pnl']:.2f}")
        col4.metric("Put P&L", f"${pnl['put_pnl']:.2f}", delta=f"{pnl['put_pnl']:.2f}")
    st.divider()

    st.subheader("Total Portfolio P&L")
    col1, col2 = st.columns(2)
    col1.metric("Total Call P&L", f"${st.session_state.total_pnl['call']:.2f}")
    col2.metric("Total Put P&L", f"${st.session_state.total_pnl['put']:.2f}")
    st.divider()

    st.subheader("Portfolio Greeks")
    greeks = st.session_state.total_greeks
    g_col1, g_col2, g_col3, g_col4, g_col5 = st.columns(5)
    g_col1.metric("Call Delta", f"{greeks['call_delta']:.4f}")
    g_col1.metric("Put Delta", f"{greeks['put_delta']:.4f}")
    g_col2.metric("Gamma", f"{greeks['gamma']:.4f}")
    g_col3.metric("Call Theta", f"{greeks['call_theta']:.4f}")
    g_col3.metric("Put Theta", f"{greeks['put_theta']:.4f}")
    g_col4.metric("Vega", f"{greeks['vega']:.4f}")
    g_col5.metric("Call Rho", f"{greeks['call_rho']:.4f}")
    g_col5.metric("Put Rho", f"{greeks['put_rho']:.4f}")
    st.divider()

    st.subheader("P&L Heat Maps (First Position)")
    pnl_data = st.session_state.heatmap_data['pnl']
    h_col1, h_col2 = st.columns(2)
    fig_call = go.Figure(data=go.Heatmap(z=pnl_data['call_pnl'], x=pnl_data['stock_prices'], y=pnl_data['volatilities'], colorscale='RdYlGn', zmid=0, colorbar=dict(title="P&L ($)")))
    fig_call.update_layout(title="Call P&L", xaxis_title="Stock Price ($)", yaxis_title="Volatility")
    h_col1.plotly_chart(fig_call, use_container_width=True)
    fig_put = go.Figure(data=go.Heatmap(z=pnl_data['put_pnl'], x=pnl_data['stock_prices'], y=pnl_data['volatilities'], colorscale='RdYlGn', zmid=0, colorbar=dict(title="P&L ($)")))
    fig_put.update_layout(title="Put P&L", xaxis_title="Stock Price ($)", yaxis_title="Volatility")
    h_col2.plotly_chart(fig_put, use_container_width=True)
    st.divider()

    st.subheader("Greeks Heatmaps (First Position)")
    greek_data = st.session_state.heatmap_data['greeks']
    greeks_first_pos = st.session_state.heatmap_data['greeks_first_pos']
    for greek in ['call_delta', 'put_delta', 'gamma', 'vega']:
        st.metric(label=f"{greek.replace('_', ' ').title()}", value=f"{greeks_first_pos[greek]:.4f}")
        fig = go.Figure(data=go.Heatmap(z=greek_data[greek], x=greek_data['stock_prices'], y=greek_data['volatilities'], colorscale='Viridis', colorbar=dict(title=greek.replace('_', ' ').title())))
        fig.update_layout(title=f"{greek.replace('_', ' ').title()} Heatmap", xaxis_title="Stock Price ($)", yaxis_title="Volatility")
        st.plotly_chart(fig, use_container_width=True, key=f"greek_heatmap_{greek}")

# --- AI Chat ---
st.divider()
st.subheader("💬 AI Chat")
user_question = st.text_input("Ask a question about your portfolio:")

if st.button("Get AI Response"):
    if user_question and st.session_state.calculations_done:
        financial_data_for_ai = {
            "positions": st.session_state.positions,
            "total_greeks": st.session_state.total_greeks,
            "total_pnl": st.session_state.total_pnl
        }
        ai_response = get_ai_response(user_question, json.dumps(financial_data_for_ai, indent=2))
        st.markdown(ai_response)
    elif not st.session_state.calculations_done:
        st.warning("Please calculate P&L first to provide context to the AI.")
    else:
        st.warning("Please enter a question.")

# --- Options Chain Analysis ---
st.divider()
st.subheader("📊 Options Chain Analysis")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
if st.button("Fetch Options Chain"):
    if ticker:
        try:
            chain = get_options_chain(ticker)
            if chain:
                st.write(f"Options Chain for {ticker.upper()}")
                for expiry, data in chain.items():
                    st.write(f"**Expiration: {expiry}**")
                    
                    current_stock_price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
                    risk_free_rate_for_iv = 0.05 # Default risk-free rate

                    if not data['calls'].empty:
                        calls_df = data['calls'].copy()
                        default_volatility = 0.2 # Default volatility
                        calls_df['theoreticalPrice'] = calls_df.apply(
                            lambda row: black_scholes_price(current_stock_price, row['strike'], (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365, risk_free_rate_for_iv, default_volatility)[0],
                            axis=1
                        )
                        calls_df['impliedVolatility'] = calls_df.apply(
                            lambda row: implied_volatility(row['lastPrice'], current_stock_price, row['strike'], (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365, risk_free_rate_for_iv, 'call'),
                            axis=1
                        )
                        st.write("Calls:")
                        st.dataframe(calls_df[['strike', 'lastPrice', 'theoreticalPrice', 'impliedVolatility', 'bid', 'ask', 'volume', 'openInterest']], use_container_width=True)
                    
                    if not data['puts'].empty:
                        puts_df = data['puts'].copy()
                        default_volatility = 0.2 # Default volatility
                        puts_df['theoreticalPrice'] = puts_df.apply(
                            lambda row: black_scholes_price(current_stock_price, row['strike'], (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365, risk_free_rate_for_iv, default_volatility)[1],
                            axis=1
                        )
                        puts_df['impliedVolatility'] = puts_df.apply(
                            lambda row: implied_volatility(row['lastPrice'], current_stock_price, row['strike'], (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365, risk_free_rate_for_iv, 'put'),
                            axis=1
                        )
                        st.write("Puts:")
                        st.dataframe(puts_df[['strike', 'lastPrice', 'theoreticalPrice', 'impliedVolatility', 'bid', 'ask', 'volume', 'openInterest']], use_container_width=True)
            else:
                st.warning(f"No options chain found for {ticker.upper()}.")
        except Exception as e:
            st.error(f"Error fetching options chain: {e}")
    else:
        st.warning("Please enter a stock ticker.")
