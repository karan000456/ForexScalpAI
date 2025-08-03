import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class MLSignalGenerator:
    """
    Machine Learning-based signal generator for forex trading
    Uses technical indicators to predict buy/sell/hold signals
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        
    def prepare_features(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare feature matrix for ML model
        
        Args:
            ohlc_data: OHLC price data
            indicators: Dictionary of technical indicators
        
        Returns:
            pd.DataFrame: Feature matrix
        """
        features = pd.DataFrame(index=ohlc_data.index)
        
        try:
            # Price-based features
            features['price_change'] = ohlc_data['close'].pct_change()
            features['high_low_ratio'] = (ohlc_data['high'] - ohlc_data['low']) / ohlc_data['close']
            features['open_close_ratio'] = (ohlc_data['close'] - ohlc_data['open']) / ohlc_data['open']
            
            # Volume proxy (using price range)
            features['volume_proxy'] = (ohlc_data['high'] - ohlc_data['low']) * ohlc_data['close']
            
            # Technical indicator features
            if 'rsi' in indicators and not indicators['rsi'].empty:
                features['rsi'] = indicators['rsi']
                features['rsi_oversold'] = (features['rsi'] < 30).astype(int)
                features['rsi_overbought'] = (features['rsi'] > 70).astype(int)
            
            if 'macd' in indicators and not indicators['macd'].empty:
                features['macd'] = indicators['macd']
                features['macd_signal'] = indicators['macd_signal']
                features['macd_histogram'] = indicators['macd_histogram']
                features['macd_bullish'] = (features['macd'] > features['macd_signal']).astype(int)
            
            # Moving averages
            if 'sma_20' in indicators and not indicators['sma_20'].empty:
                features['price_above_sma20'] = (ohlc_data['close'] > indicators['sma_20']).astype(int)
                features['sma20_slope'] = indicators['sma_20'].diff()
            
            if 'ema_12' in indicators and not indicators['ema_12'].empty:
                features['price_above_ema12'] = (ohlc_data['close'] > indicators['ema_12']).astype(int)
                features['ema12_slope'] = indicators['ema_12'].diff()
            
            # Bollinger Bands
            if all(key in indicators for key in ['bb_upper', 'bb_middle', 'bb_lower']):
                if not indicators['bb_upper'].empty:
                    features['bb_position'] = (ohlc_data['close'] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
                    features['bb_squeeze'] = (indicators['bb_upper'] - indicators['bb_lower']) / indicators['bb_middle']
            
            # Stochastic
            if 'stoch_k' in indicators and not indicators['stoch_k'].empty:
                features['stoch_k'] = indicators['stoch_k']
                features['stoch_oversold'] = (features['stoch_k'] < 20).astype(int)
                features['stoch_overbought'] = (features['stoch_k'] > 80).astype(int)
            
            # ATR (volatility)
            if 'atr' in indicators and not indicators['atr'].empty:
                features['atr'] = indicators['atr']
                features['atr_normalized'] = indicators['atr'] / ohlc_data['close']
            
            # Williams %R
            if 'williams_r' in indicators and not indicators['williams_r'].empty:
                features['williams_r'] = indicators['williams_r']
            
            # CCI
            if 'cci' in indicators and not indicators['cci'].empty:
                features['cci'] = indicators['cci']
                features['cci_extreme'] = (abs(features['cci']) > 100).astype(int)
            
            # Momentum
            if 'momentum' in indicators and not indicators['momentum'].empty:
                features['momentum'] = indicators['momentum']
                features['momentum_positive'] = (features['momentum'] > 0).astype(int)
            
            # Lagged features (previous period values)
            for col in ['price_change', 'rsi', 'macd']:
                if col in features:
                    features[f'{col}_lag1'] = features[col].shift(1)
                    features[f'{col}_lag2'] = features[col].shift(2)
            
            # Rolling statistics
            features['price_volatility'] = ohlc_data['close'].rolling(window=10).std()
            features['return_volatility'] = features['price_change'].rolling(window=10).std()
            
            # Trend features
            features['short_trend'] = ohlc_data['close'].rolling(window=5).mean().diff()
            features['medium_trend'] = ohlc_data['close'].rolling(window=20).mean().diff()
            
        except Exception as e:
            print(f"Error preparing features: {e}")
        
        # Remove infinite and NaN values
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def create_labels(self, ohlc_data: pd.DataFrame, lookahead_periods: int = 5, profit_threshold: float = 0.0005) -> pd.Series:
        """
        Create trading labels based on future price movements
        
        Args:
            ohlc_data: OHLC price data
            lookahead_periods: Number of periods to look ahead
            profit_threshold: Minimum profit threshold for signal generation
        
        Returns:
            pd.Series: Labels (0=HOLD, 1=BUY, 2=SELL)
        """
        close_prices = ohlc_data['close']
        labels = pd.Series(index=close_prices.index, data=0)  # Default to HOLD
        
        try:
            # Calculate future returns
            future_max = close_prices.rolling(window=lookahead_periods, min_periods=1).max().shift(-lookahead_periods)
            future_min = close_prices.rolling(window=lookahead_periods, min_periods=1).min().shift(-lookahead_periods)
            
            # Calculate potential profits
            buy_profit = (future_max - close_prices) / close_prices
            sell_profit = (close_prices - future_min) / close_prices
            
            # Create labels based on profit potential
            buy_condition = (buy_profit > profit_threshold) & (buy_profit > sell_profit)
            sell_condition = (sell_profit > profit_threshold) & (sell_profit > buy_profit)
            
            labels[buy_condition] = 1   # BUY
            labels[sell_condition] = 2  # SELL
            # Everything else remains 0 (HOLD)
            
        except Exception as e:
            print(f"Error creating labels: {e}")
        
        return labels
    
    def train_model(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any]) -> bool:
        """
        Train the ML model using historical data
        
        Args:
            ohlc_data: Historical OHLC data
            indicators: Dictionary of technical indicators
        
        Returns:
            bool: True if training successful, False otherwise
        """
        try:
            # Prepare features and labels
            features = self.prepare_features(ohlc_data, indicators)
            labels = self.create_labels(ohlc_data)
            
            # Remove rows with NaN values
            valid_indices = features.dropna().index.intersection(labels.dropna().index)
            if len(valid_indices) < 50:  # Need minimum data for training
                print("Insufficient data for training")
                return False
            
            X = features.loc[valid_indices]
            y = labels.loc[valid_indices]
            
            # Store feature columns for later use
            self.feature_columns = X.columns.tolist()
            
            # Split data for training/validation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            print(f"Model training completed. Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def generate_signal(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any], sensitivity: str = "Moderate") -> Dict[str, Any]:
        """
        Generate trading signal using the trained ML model
        
        Args:
            ohlc_data: Current OHLC data
            indicators: Dictionary of technical indicators
            sensitivity: Signal sensitivity ("Conservative", "Moderate", "Aggressive")
        
        Returns:
            Dict containing signal action, confidence, and reasoning
        """
        # Train model if not already trained
        if not self.is_trained and len(ohlc_data) > 50:
            self.train_model(ohlc_data, indicators)
        
        # If model still not trained, use rule-based approach
        if not self.is_trained:
            return self._rule_based_signal(indicators, sensitivity)
        
        try:
            # Prepare current features
            features = self.prepare_features(ohlc_data, indicators)
            
            if features.empty or len(features) == 0:
                return self._rule_based_signal(indicators, sensitivity)
            
            # Get latest feature vector
            latest_features = features.iloc[-1:][self.feature_columns]
            
            # Handle missing features
            for col in self.feature_columns:
                if col not in latest_features.columns:
                    latest_features[col] = 0
            
            latest_features = latest_features.fillna(0)
            
            # Scale features
            latest_scaled = self.scaler.transform(latest_features)
            
            # Get prediction and probabilities
            prediction = self.model.predict(latest_scaled)[0]
            probabilities = self.model.predict_proba(latest_scaled)[0]
            
            # Adjust confidence thresholds based on sensitivity
            confidence_thresholds = {
                "Conservative": 0.7,
                "Moderate": 0.6,
                "Aggressive": 0.5
            }
            
            threshold = confidence_thresholds.get(sensitivity, 0.6)
            max_prob = max(probabilities)
            
            # Generate signal
            if prediction == 1 and max_prob > threshold:  # BUY
                action = "BUY"
                confidence = max_prob * 100
            elif prediction == 2 and max_prob > threshold:  # SELL
                action = "SELL"
                confidence = max_prob * 100
            else:
                action = "HOLD"
                confidence = max_prob * 100
            
            return {
                'action': action,
                'confidence': confidence,
                'method': 'ML',
                'probabilities': {
                    'hold': probabilities[0] * 100,
                    'buy': probabilities[1] * 100 if len(probabilities) > 1 else 0,
                    'sell': probabilities[2] * 100 if len(probabilities) > 2 else 0
                }
            }
            
        except Exception as e:
            print(f"Error generating ML signal: {e}")
            return self._rule_based_signal(indicators, sensitivity)
    
    def _rule_based_signal(self, indicators: Dict[str, Any], sensitivity: str) -> Dict[str, Any]:
        """
        Fallback rule-based signal generation when ML model is not available
        
        Args:
            indicators: Dictionary of technical indicators
            sensitivity: Signal sensitivity
        
        Returns:
            Dict containing signal information
        """
        try:
            buy_signals = 0
            sell_signals = 0
            total_signals = 0
            
            # RSI signals
            if 'rsi' in indicators and not indicators['rsi'].empty:
                rsi_current = indicators['rsi'].iloc[-1]
                if rsi_current < 30:
                    buy_signals += 1
                elif rsi_current > 70:
                    sell_signals += 1
                total_signals += 1
            
            # MACD signals
            if 'macd' in indicators and 'macd_signal' in indicators:
                if not indicators['macd'].empty and not indicators['macd_signal'].empty:
                    macd_current = indicators['macd'].iloc[-1]
                    signal_current = indicators['macd_signal'].iloc[-1]
                    
                    if len(indicators['macd']) > 1:
                        macd_prev = indicators['macd'].iloc[-2]
                        signal_prev = indicators['macd_signal'].iloc[-2]
                        
                        # MACD crossover
                        if macd_prev <= signal_prev and macd_current > signal_current:
                            buy_signals += 1
                        elif macd_prev >= signal_prev and macd_current < signal_current:
                            sell_signals += 1
                    
                    total_signals += 1
            
            # Moving Average signals
            if 'sma_20' in indicators and not indicators['sma_20'].empty:
                if len(indicators['sma_20']) > 0:
                    # Current price vs SMA
                    current_price = indicators['sma_20'].index.get_loc(indicators['sma_20'].index[-1])
                    # This is a simplified check - in real implementation, you'd compare actual price to SMA
                    total_signals += 1
            
            # Stochastic signals
            if 'stoch_k' in indicators and not indicators['stoch_k'].empty:
                stoch_current = indicators['stoch_k'].iloc[-1]
                if stoch_current < 20:
                    buy_signals += 1
                elif stoch_current > 80:
                    sell_signals += 1
                total_signals += 1
            
            # Calculate signal strength
            if total_signals == 0:
                return {'action': 'HOLD', 'confidence': 50.0, 'method': 'Rule-based'}
            
            buy_strength = buy_signals / total_signals
            sell_strength = sell_signals / total_signals
            
            # Adjust thresholds based on sensitivity
            thresholds = {
                "Conservative": 0.7,
                "Moderate": 0.6,
                "Aggressive": 0.5
            }
            
            threshold = thresholds.get(sensitivity, 0.6)
            
            if buy_strength > threshold:
                return {
                    'action': 'BUY',
                    'confidence': buy_strength * 100,
                    'method': 'Rule-based'
                }
            elif sell_strength > threshold:
                return {
                    'action': 'SELL',
                    'confidence': sell_strength * 100,
                    'method': 'Rule-based'
                }
            else:
                return {
                    'action': 'HOLD',
                    'confidence': max(buy_strength, sell_strength) * 100,
                    'method': 'Rule-based'
                }
                
        except Exception as e:
            print(f"Error in rule-based signal: {e}")
            return {'action': 'HOLD', 'confidence': 50.0, 'method': 'Error'}
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from the trained model
        
        Returns:
            Dict containing feature names and their importance scores
        """
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for feature, importance in zip(self.feature_columns, self.model.feature_importances_):
            importance_dict[feature] = importance
        
        # Sort by importance
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
