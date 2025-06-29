# Black-Scholes Option Pricer with P&L Analysis

A comprehensive Black-Scholes option pricing tool that evolves from a simple command-line calculator to a full-featured web application with P&L analysis and database storage.

## Features

### ✨ Core Functionality
- **Black-Scholes Pricing**: Accurate European call and put option pricing
- **Greeks Calculation**: Real-time calculation of Delta, Gamma, Theta, Vega, and Rho
- **Interactive Web Interface**: User-friendly Streamlit application
- **P&L Analysis**: Real-time profit/loss calculations with visual heat maps
- **Database Integration**: Persistent storage of calculations and results
- **Historical Tracking**: View past calculations and analysis
- **Options Chain Analysis**: Fetch real-time options data, calculate theoretical prices and implied volatilities.
- **Simple AI Chat Function**: Interact with an AI to get insights on options, P&L, and Greeks.

### 📊 Visualization
- **Interactive Heat Maps**: Visualize P&L and Greeks (Delta, Gamma, Vega) across different stock prices and volatilities
- **Color-coded Results**: Green for profits, red for losses
- **Configurable Ranges**: Customize analysis parameters
- **Real-time Updates**: Instant recalculation and visualization

## Project Structure

```
├── black_scholes.py      # Core Black-Scholes calculations
├── database_manager.py   # Database operations and management
├── streamlit_app.py      # Main Streamlit web application
├── command_line_app.py   # Simple CLI version (Level 1)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   **Web Interface (Recommended):**
   ```bash
   streamlit run streamlit_app.py
   ```

   **Command Line Interface:**
   ```bash
   python command_line_app.py
   ```

## Usage

### Web Application

1. **Launch the app:** `streamlit run streamlit_app.py`
2. **Set Parameters:** Use the sidebar to input:
   - Current stock price
   - Strike price
   - Time to expiry
   - Volatility
   - Risk-free rate
   - Purchase prices for P&L analysis
3. **Configure Analysis:** Adjust heat map ranges and resolution
4. **Calculate:** Click "Calculate P&L" to generate results
5. **Analyze:** View option prices, P&L metrics, and interactive heat maps

### Command Line Interface

1. **Launch:** `python command_line_app.py`
2. **Input Parameters:** Enter the five Black-Scholes parameters when prompted
3. **View Results:** See calculated call and put option prices
4. **Repeat:** Calculate multiple options or exit

## Black-Scholes Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Stock Price (S)** | Current market price of the underlying asset | $100.00 |
| **Strike Price (K)** | Exercise price of the option | $105.00 |
| **Time to Expiry (T)** | Time remaining until expiration (years) | 0.25 (3 months) |
| **Volatility (σ)** | Expected volatility (decimal form) | 0.20 (20%) |
| **Risk-Free Rate (r)** | Risk-free interest rate (decimal form) | 0.05 (5%) |

## P&L Analysis Features

### Heat Map Visualization
- **X-axis:** Range of stock prices (configurable ±% from current)
- **Y-axis:** Range of volatilities (configurable ±% from current)
- **Color Scale:** Red-Yellow-Green divergent scale (losses to profits)
- **Interactive:** Hover for exact values, zoom, and pan

### Database Storage
- **SQLite Backend:** Automatic database creation and management
- **Calculation History:** Track all past analyses
- **Detailed Results:** Store complete P&L surfaces for future reference

## Technical Architecture

### Modular Design
- **Presentation Layer:** Streamlit UI (`streamlit_app.py`)
- **Business Logic:** Core calculations (`black_scholes.py`)
- **Data Layer:** Database operations (`database_manager.py`)

### Key Components
1. **Black-Scholes Engine:** Pure functions for option pricing
2. **P&L Surface Generator:** Creates 2D profit/loss landscapes
3. **Database Manager:** Handles data persistence and retrieval
4. **Interactive Interface:** Real-time parameter adjustment and visualization

## Dependencies

- **streamlit**: Web application framework
- **numpy**: Numerical computations
- **scipy**: Statistical functions (normal distribution)
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive plotting and visualization
- **sqlite3**: Database operations (built-in)

## Mathematical Background

The Black-Scholes formula for European options:

**Call Option:**
```
C = S₀N(d₁) - Ke⁻ʳᵀN(d₂)
```

**Put Option:**
```
P = Ke⁻ʳᵀN(-d₂) - S₀N(-d₁)
```

Where:
```
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

Feel free to fork, modify, and enhance this project. Key areas for expansion:
- Additional option types (American, exotic options)
- More sophisticated Greeks calculations
- Enhanced visualization options
- Advanced P&L scenarios and stress testing