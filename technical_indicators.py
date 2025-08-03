import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """
    A comprehensive class for calculating technical indicators used in forex trading
    """
    
    def __init__(self):
        pass
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: Price series (typically close prices)
            period: Period for RSI calculation (default 14)
        
        Returns:
            pd.Series: RSI values
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price series (typically close prices)
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
        
        Returns:
            Dict containing MACD line, signal line, and histogram
        """
        ema_fast = self.calculate_ema(data, fast_period)
        ema_slow = self.calculate_ema(data, slow_period)
        
        macd = ema_fast - ema_slow
        signal = self.calculate_ema(macd, signal_period)
        histogram = macd - signal
        
        return {
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': histogram
        }
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: Price series
            period: Period for moving average and standard deviation
            std_dev: Number of standard deviations for bands
        
        Returns:
            Dict containing upper band, middle band (SMA), and lower band
        """
        sma = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'bb_upper': upper_band,
            'bb_middle': sma,
            'bb_lower': lower_band
        }
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: Period for %K calculation
            d_period: Period for %D (moving average of %K)
        
        Returns:
            Dict containing %K and %D values
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'stoch_k': k_percent,
            'stoch_d': d_percent
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for ATR calculation
        
        Returns:
            pd.Series: ATR values
        """
        # Calculate True Range
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR as moving average of True Range
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
        
        Returns:
            pd.Series: Williams %R values
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI)
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
        
        Returns:
            pd.Series: CCI values
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        
        # Calculate mean absolute deviation
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        return cci
    
    def calculate_momentum(self, data: pd.Series, period: int = 10) -> pd.Series:
        """
        Calculate Price Momentum
        
        Args:
            data: Price series
            period: Period for momentum calculation
        
        Returns:
            pd.Series: Momentum values
        """
        return data - data.shift(period)
    
    def calculate_all_indicators(self, ohlc_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all technical indicators for given OHLC data
        
        Args:
            ohlc_data: DataFrame with columns ['open', 'high', 'low', 'close']
        
        Returns:
            Dict containing all calculated indicators
        """
        if ohlc_data.empty:
            return {}
        
        close = ohlc_data['close']
        high = ohlc_data['high']
        low = ohlc_data['low']
        
        indicators = {}
        
        try:
            # Moving Averages
            indicators['sma_10'] = self.calculate_sma(close, 10)
            indicators['sma_20'] = self.calculate_sma(close, 20)
            indicators['sma_50'] = self.calculate_sma(close, 50)
            indicators['ema_12'] = self.calculate_ema(close, 12)
            indicators['ema_26'] = self.calculate_ema(close, 26)
            
            # RSI
            indicators['rsi'] = self.calculate_rsi(close, 14)
            
            # MACD
            macd_data = self.calculate_macd(close)
            indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self.calculate_bollinger_bands(close)
            indicators.update(bb_data)
            
            # Stochastic
            stoch_data = self.calculate_stochastic(high, low, close)
            indicators.update(stoch_data)
            
            # ATR
            indicators['atr'] = self.calculate_atr(high, low, close)
            
            # Williams %R
            indicators['williams_r'] = self.calculate_williams_r(high, low, close)
            
            # CCI
            indicators['cci'] = self.calculate_cci(high, low, close)
            
            # Momentum
            indicators['momentum'] = self.calculate_momentum(close)
            
            # Price-based indicators
            indicators['price_change'] = close.pct_change()
            indicators['volatility'] = close.rolling(window=20).std()
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators
    
    def get_trend_signals(self, indicators: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate trend signals based on calculated indicators
        
        Args:
            indicators: Dictionary of calculated indicators
        
        Returns:
            Dict containing trend signals for different indicators
        """
        signals = {}
        
        try:
            # RSI signals
            if 'rsi' in indicators and not indicators['rsi'].empty:
                rsi_current = indicators['rsi'].iloc[-1]
                if rsi_current > 70:
                    signals['rsi'] = 'OVERBOUGHT'
                elif rsi_current < 30:
                    signals['rsi'] = 'OVERSOLD'
                else:
                    signals['rsi'] = 'NEUTRAL'
            
            # MACD signals
            if 'macd' in indicators and 'macd_signal' in indicators:
                if not indicators['macd'].empty and not indicators['macd_signal'].empty:
                    macd_current = indicators['macd'].iloc[-1]
                    signal_current = indicators['macd_signal'].iloc[-1]
                    
                    if macd_current > signal_current:
                        signals['macd'] = 'BULLISH'
                    else:
                        signals['macd'] = 'BEARISH'
            
            # Moving Average signals
            if 'sma_20' in indicators and 'ema_12' in indicators:
                if not indicators['sma_20'].empty and not indicators['ema_12'].empty:
                    sma_current = indicators['sma_20'].iloc[-1]
                    ema_current = indicators['ema_12'].iloc[-1]
                    
                    if ema_current > sma_current:
                        signals['ma_trend'] = 'BULLISH'
                    else:
                        signals['ma_trend'] = 'BEARISH'
            
            # Stochastic signals
            if 'stoch_k' in indicators:
                if not indicators['stoch_k'].empty:
                    stoch_k = indicators['stoch_k'].iloc[-1]
                    if stoch_k > 80:
                        signals['stochastic'] = 'OVERBOUGHT'
                    elif stoch_k < 20:
                        signals['stochastic'] = 'OVERSOLD'
                    else:
                        signals['stochastic'] = 'NEUTRAL'
            
        except Exception as e:
            print(f"Error generating trend signals: {e}")
        
        return signals
