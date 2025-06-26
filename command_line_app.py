#!/usr/bin/env python3
"""
Level 1: Command-line Black-Scholes Option Pricer
Simple REPL application for calculating European option prices
"""

from black_scholes import black_scholes_price

def get_float_input(prompt, min_val=None):
    """Get float input with validation."""
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be >= {min_val}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

def main():
    """Main REPL loop for the Black-Scholes calculator."""
    print("=" * 50)
    print("Black-Scholes European Option Pricer")
    print("=" * 50)
    
    while True:
        print("\nEnter option parameters:")
        
        try:
            # Get inputs
            S = get_float_input("Current Stock Price ($): ", min_val=0.01)
            K = get_float_input("Strike Price ($): ", min_val=0.01)
            T = get_float_input("Time to Expiry (years): ", min_val=0.01)
            r = get_float_input("Risk-Free Rate (as decimal, e.g., 0.05 for 5%): ", min_val=0)
            sigma = get_float_input("Volatility (as decimal, e.g., 0.2 for 20%): ", min_val=0.01)
            
            # Calculate option prices
            call_price, put_price = black_scholes_price(S, K, T, r, sigma)
            
            # Display results
            print("\n" + "=" * 40)
            print("OPTION PRICES")
            print("=" * 40)
            print(f"European Call Price: ${call_price:.4f}")
            print(f"European Put Price:  ${put_price:.4f}")
            print("=" * 40)
            
            # Ask if user wants to continue
            while True:
                continue_calc = input("\nCalculate another option? (y/n): ").lower().strip()
                if continue_calc in ['y', 'yes', 'n', 'no']:
                    break
                print("Please enter 'y' or 'n'")
            
            if continue_calc.startswith('n'):
                print("\nThank you for using the Black-Scholes calculator!")
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting calculator...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()