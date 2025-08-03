import pandas as pd
import numpy as np
import requests
import os
import time
from datetime import datetime, timedelta
import json

class ForexDataProvider:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.rate_limit_delay = 12  # 5 requests per minute = 12 seconds between requests
        
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _convert_pair_format(self, pair):
        """Convert pair format from EUR/USD to EURUSD"""
        return pair.replace('/', '')
    
    def get_live_data(self, currency_pair, interval='5min', outputsize='compact'):
        """
        Fetch live forex data from Alpha Vantage API
        
        Args:
            currency_pair (str): Currency pair like 'EUR/USD'
            interval (str): Time interval (1min, 5min, 15min, 30min, 60min)
            outputsize (str): 'compact' for last 100 data points, 'full' for full dataset
        
        Returns:
            pd.DataFrame: OHLC data with datetime index
        """
        if not self.api_key:
            # Fallback to demo data when no API key is provided
            return self._generate_demo_data(currency_pair)
        
        try:
            self._rate_limit()
            
            symbol = self._convert_pair_format(currency_pair)
            
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': symbol[:3],
                'to_symbol': symbol[3:],
                'interval': interval,
                'apikey': self.api_key,
                'outputsize': outputsize
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"API Error: {data['Error Message']}")
            
            if 'Note' in data:
                raise Exception(f"API Rate Limit: {data['Note']}")
            
            # Extract time series data
            time_series_key = f'Time Series FX ({interval})'
            if time_series_key not in data:
                raise Exception("No time series data found in API response")
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df_data = []
            for timestamp, ohlc in time_series.items():
                df_data.append({
                    'timestamp': pd.to_datetime(timestamp),
                    'open': float(ohlc['1. open']),
                    'high': float(ohlc['2. high']),
                    'low': float(ohlc['3. low']),
                    'close': float(ohlc['4. close'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return self._generate_demo_data(currency_pair)
        
        except Exception as e:
            print(f"Data fetch error: {e}")
            return self._generate_demo_data(currency_pair)
    
    def _generate_demo_data(self, currency_pair):
        """
        Generate realistic demo forex data for testing purposes
        This is used when API key is not available or API fails
        """
        # Base prices for different currency pairs
        base_prices = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 149.50,
            'USD/CHF': 0.8850,
            'AUD/USD': 0.6650,
            'USD/CAD': 1.3550,
            'NZD/USD': 0.6150
        }
        
        base_price = base_prices.get(currency_pair, 1.0000)
        
        # Generate 100 data points (5-minute intervals for about 8 hours)
        periods = 100
        dates = pd.date_range(
            end=datetime.now(),
            periods=periods,
            freq='5min'
        )
        
        # Generate realistic price movements
        np.random.seed(int(time.time()) % 1000)  # Seed changes over time for variation
        
        # Simulate price movements with trend and volatility
        returns = np.random.normal(0, 0.0002, periods)  # Small random movements
        
        # Add some trend component
        trend = np.sin(np.linspace(0, 4*np.pi, periods)) * 0.0001
        returns += trend
        
        # Calculate prices
        prices = [base_price]
        for i in range(1, periods):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(new_price)
        
        # Generate OHLC data
        df_data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC from the base price
            volatility = base_price * 0.0001  # 1 pip volatility
            
            open_price = price + np.random.normal(0, volatility/2)
            close_price = price + np.random.normal(0, volatility/2)
            
            high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility))
            
            df_data.append({
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5)
            })
        
        df = pd.DataFrame(df_data, index=dates)
        return df
    
    def get_current_price(self, currency_pair):
        """Get the most recent price for a currency pair"""
        try:
            data = self.get_live_data(currency_pair)
            if data is not None and not data.empty:
                return data['close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
    
    def get_historical_data(self, currency_pair, days=30):
        """
        Get historical daily data for backtesting
        
        Args:
            currency_pair (str): Currency pair like 'EUR/USD'
            days (int): Number of days of historical data
        
        Returns:
            pd.DataFrame: Historical OHLC data
        """
        if not self.api_key:
            return self._generate_demo_historical_data(currency_pair, days)
        
        try:
            self._rate_limit()
            
            symbol = self._convert_pair_format(currency_pair)
            
            params = {
                'function': 'FX_DAILY',
                'from_symbol': symbol[:3],
                'to_symbol': symbol[3:],
                'apikey': self.api_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Time Series FX (Daily)' not in data:
                raise Exception("No daily data found")
            
            time_series = data['Time Series FX (Daily)']
            
            # Convert to DataFrame
            df_data = []
            for date, ohlc in time_series.items():
                df_data.append({
                    'date': pd.to_datetime(date),
                    'open': float(ohlc['1. open']),
                    'high': float(ohlc['2. high']),
                    'low': float(ohlc['3. low']),
                    'close': float(ohlc['4. close'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            
            # Return only requested number of days
            return df.tail(days)
            
        except Exception as e:
            print(f"Historical data error: {e}")
            return self._generate_demo_historical_data(currency_pair, days)
    
    def _generate_demo_historical_data(self, currency_pair, days):
        """Generate demo historical data"""
        base_prices = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 149.50,
            'USD/CHF': 0.8850,
            'AUD/USD': 0.6650,
            'USD/CAD': 1.3550,
            'NZD/USD': 0.6150
        }
        
        base_price = base_prices.get(currency_pair, 1.0000)
        
        dates = pd.date_range(
            end=datetime.now().date(),
            periods=days,
            freq='D'
        )
        
        np.random.seed(42)  # Fixed seed for consistent historical data
        
        # Generate price series with random walk
        returns = np.random.normal(0, 0.005, days)
        prices = [base_price]
        
        for i in range(1, days):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(new_price)
        
        # Generate OHLC
        df_data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            volatility = price * 0.01
            
            open_price = price + np.random.normal(0, volatility/4)
            close_price = price + np.random.normal(0, volatility/4)
            
            high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility/2))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility/2))
            
            df_data.append({
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5)
            })
        
        df = pd.DataFrame(df_data, index=dates)
        return df
