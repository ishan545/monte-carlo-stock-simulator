import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataFetcher:
    """Fetch stock data using yfinance"""
    
    def __init__(self, period="1y"):
        """Initialize DataFetcher with period"""
        self.period = period
    
    def get_stock_data(self, ticker, period=None):
        """Fetch historical stock data"""
        try:
            period = period or self.period
            data = yf.download(ticker, period=period, progress=False)
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_returns(self, data):
        """Calculate daily returns from price data"""
        if data is None or len(data) < 2:
            return None
        prices = data['Adj Close'].values
        returns = np.diff(prices) / prices[:-1]
        return returns
    
    def get_statistics(self, ticker, period=None):
        """Calculate statistical measures for a stock"""
        data = self.get_stock_data(ticker, period)
        if data is None:
            return None
        
        returns = self.calculate_returns(data)
        if returns is None:
            return None
        
        current_price = data['Adj Close'].values[-1]
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'annual_return': np.mean(returns) * 252,
            'annual_volatility': np.std(returns) * np.sqrt(252),
            'min_price': data['Adj Close'].min(),
            'max_price': data['Adj Close'].max()
        }
