import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import json

class DatabaseManager:
    def __init__(self, db_path="blackscholes.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create calculations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calculations (
                    calculation_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    base_stock_price REAL,
                    strike_price REAL,
                    time_to_expiry REAL,
                    volatility REAL,
                    risk_free_rate REAL,
                    call_purchase_price REAL,
                    put_purchase_price REAL
                )
            ''')
            
            # Create pnl_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pnl_results (
                    result_id TEXT PRIMARY KEY,
                    calculation_id TEXT,
                    shocked_stock_price REAL,
                    shocked_volatility REAL,
                    call_pnl REAL,
                    put_pnl REAL,
                    FOREIGN KEY (calculation_id) REFERENCES calculations (calculation_id)
                )
            ''')
            
            conn.commit()
    
    def save_calculation(self, inputs, pnl_data):
        """Save calculation inputs and P&L results to database."""
        calculation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert calculation record
            cursor.execute('''
                INSERT INTO calculations 
                (calculation_id, timestamp, base_stock_price, strike_price, 
                 time_to_expiry, volatility, risk_free_rate, 
                 call_purchase_price, put_purchase_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                calculation_id, timestamp, inputs['stock_price'], inputs['strike_price'],
                inputs['time_to_expiry'], inputs['volatility'], inputs['risk_free_rate'],
                inputs['call_purchase_price'], inputs['put_purchase_price']
            ))
            
            # Insert P&L results
            stock_prices = pnl_data['stock_prices']
            volatilities = pnl_data['volatilities']
            call_pnl = pnl_data['call_pnl']
            put_pnl = pnl_data['put_pnl']
            
            for i, vol in enumerate(volatilities):
                for j, price in enumerate(stock_prices):
                    result_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO pnl_results 
                        (result_id, calculation_id, shocked_stock_price, 
                         shocked_volatility, call_pnl, put_pnl)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        result_id, calculation_id, price, vol,
                        call_pnl[i, j], put_pnl[i, j]
                    ))
            
            conn.commit()
        
        return calculation_id
    
    def get_calculation_history(self, limit=10):
        """Get recent calculation history."""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT calculation_id, timestamp, base_stock_price, strike_price,
                       time_to_expiry, volatility, risk_free_rate,
                       call_purchase_price, put_purchase_price
                FROM calculations 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df
    
    def get_pnl_results(self, calculation_id):
        """Get P&L results for a specific calculation."""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT shocked_stock_price, shocked_volatility, call_pnl, put_pnl
                FROM pnl_results 
                WHERE calculation_id = ?
            '''
            df = pd.read_sql_query(query, conn, params=(calculation_id,))
            return df