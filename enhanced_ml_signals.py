import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any
from datetime import datetime, timedelta
from adaptive_learning import AdaptiveLearningEngine

class EnhancedMLSignalGenerator:
    """
    Enhanced ML Signal Generator with adaptive learning capabilities
    """
    
    def __init__(self):
        self.adaptive_engine = AdaptiveLearningEngine()
        self.base_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        self.signal_history = []
        
    def generate_enhanced_signal(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any], 
                               sensitivity: str = "Moderate", pair: str = "EUR/USD") -> Dict[str, Any]:
        """Generate trading signal using both base model and adaptive learning"""
        
        # First, try to get adaptive prediction
        adaptive_signal = self.adaptive_engine.get_adaptive_prediction(indicators, pair)
        
        # Get base model prediction
        base_signal = self.generate_base_signal(ohlc_data, indicators, sensitivity)
        
        # Combine predictions intelligently
        final_signal = self.combine_predictions(base_signal, adaptive_signal, indicators, pair)
        
        # Analyze market patterns for learning
        market_pattern = self.adaptive_engine.analyze_market_patterns(ohlc_data, indicators)
        final_signal['market_conditions'] = market_pattern
        final_signal['indicators'] = self.extract_indicator_values(indicators)
        
        # Store signal for future learning
        self.signal_history.append({
            'timestamp': datetime.now(),
            'pair': pair,
            'signal': final_signal,
            'market_conditions': market_pattern,
            'indicators': indicators
        })
        
        return final_signal
    
    def generate_base_signal(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any], 
                           sensitivity: str) -> Dict[str, Any]:
        """Generate signal using the base model"""
        try:
            # Use the original ML signal generation logic
            features = self.prepare_features(ohlc_data, indicators)
            
            if features.empty or len(features) == 0:
                return self._rule_based_signal(indicators, sensitivity)
            
            # Train model if not already trained
            if not self.is_trained and len(ohlc_data) > 50:
                self.train_base_model(ohlc_data, indicators)
            
            if not self.is_trained:
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
            prediction = self.base_model.predict(latest_scaled)[0]
            probabilities = self.base_model.predict_proba(latest_scaled)[0]
            
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
                'method': 'Base ML',
                'probabilities': {
                    'hold': probabilities[0] * 100,
                    'buy': probabilities[1] * 100 if len(probabilities) > 1 else 0,
                    'sell': probabilities[2] * 100 if len(probabilities) > 2 else 0
                }
            }
            
        except Exception as e:
            return self._rule_based_signal(indicators, sensitivity)
    
    def combine_predictions(self, base_signal: Dict, adaptive_signal: Dict, 
                          indicators: Dict, pair: str) -> Dict[str, Any]:
        """Intelligently combine base model and adaptive model predictions"""
        
        if not adaptive_signal:
            # No adaptive model available, use base signal
            final_signal = base_signal.copy()
            final_signal['source'] = 'Base Model Only'
            return final_signal
        
        # Both models available - combine intelligently
        base_confidence = base_signal.get('confidence', 0)
        adaptive_confidence = adaptive_signal.get('confidence', 0)
        adaptive_accuracy = adaptive_signal.get('model_accuracy', 0.5)
        
        # Weight the predictions based on model performance
        if adaptive_accuracy > 0.7:  # Adaptive model is performing well
            # Give more weight to adaptive model
            adaptive_weight = 0.7
            base_weight = 0.3
        elif adaptive_accuracy > 0.6:  # Moderate performance
            # Equal weight
            adaptive_weight = 0.5
            base_weight = 0.5
        else:  # Poor performance
            # Favor base model
            adaptive_weight = 0.3
            base_weight = 0.7
        
        # Combine confidence scores
        combined_confidence = (base_confidence * base_weight + adaptive_confidence * adaptive_weight)
        
        # Determine final action
        base_action = base_signal.get('action', 'HOLD')
        adaptive_action = adaptive_signal.get('action', 'HOLD')
        
        if base_action == adaptive_action:
            # Both models agree
            final_action = base_action
            combined_confidence = min(combined_confidence * 1.1, 100)  # Boost confidence when models agree
        else:
            # Models disagree - use the one with higher confidence
            if adaptive_confidence > base_confidence and adaptive_accuracy > 0.6:
                final_action = adaptive_action
            else:
                final_action = base_action
            
            combined_confidence = combined_confidence * 0.8  # Reduce confidence when models disagree
        
        return {
            'action': final_action,
            'confidence': combined_confidence,
            'method': 'Enhanced ML (Base + Adaptive)',
            'base_prediction': {
                'action': base_action,
                'confidence': base_confidence
            },
            'adaptive_prediction': {
                'action': adaptive_action,
                'confidence': adaptive_confidence,
                'model_accuracy': adaptive_accuracy
            },
            'model_agreement': base_action == adaptive_action,
            'source': 'Combined Models'
        }
    
    def extract_indicator_values(self, indicators: Dict) -> Dict:
        """Extract current indicator values for learning"""
        current_values = {}
        
        try:
            for key, series in indicators.items():
                if hasattr(series, 'iloc') and len(series) > 0:
                    current_values[key] = float(series.iloc[-1])
                else:
                    current_values[key] = 0.0
        except Exception:
            pass
        
        return current_values
    
    def prepare_features(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any]) -> pd.DataFrame:
        """Prepare feature matrix for ML model (reusing existing logic)"""
        features = pd.DataFrame(index=ohlc_data.index)
        
        try:
            # Price-based features
            features['price_change'] = ohlc_data['close'].pct_change()
            features['high_low_ratio'] = (ohlc_data['high'] - ohlc_data['low']) / ohlc_data['close']
            features['open_close_ratio'] = (ohlc_data['close'] - ohlc_data['open']) / ohlc_data['open']
            
            # Volume proxy
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
            
            # Additional features for enhanced model
            if 'atr' in indicators and not indicators['atr'].empty:
                features['atr'] = indicators['atr']
                features['atr_normalized'] = indicators['atr'] / ohlc_data['close']
            
            if 'stoch_k' in indicators and not indicators['stoch_k'].empty:
                features['stoch_k'] = indicators['stoch_k']
                features['stoch_oversold'] = (features['stoch_k'] < 20).astype(int)
                features['stoch_overbought'] = (features['stoch_k'] > 80).astype(int)
            
            # Lagged features
            for col in ['price_change', 'rsi', 'macd']:
                if col in features:
                    features[f'{col}_lag1'] = features[col].shift(1)
                    features[f'{col}_lag2'] = features[col].shift(2)
            
            # Rolling statistics
            features['price_volatility'] = ohlc_data['close'].rolling(window=10).std()
            features['return_volatility'] = features['price_change'].rolling(window=10).std()
            
        except Exception as e:
            pass
        
        # Remove infinite and NaN values
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def train_base_model(self, ohlc_data: pd.DataFrame, indicators: Dict[str, Any]) -> bool:
        """Train the base ML model"""
        try:
            # Prepare features and labels
            features = self.prepare_features(ohlc_data, indicators)
            labels = self.create_labels(ohlc_data)
            
            # Remove rows with NaN values
            valid_indices = features.dropna().index.intersection(labels.dropna().index)
            if len(valid_indices) < 50:  # Need minimum data for training
                return False
            
            X = features.loc[valid_indices]
            y = labels.loc[valid_indices]
            
            # Store feature columns for later use
            self.feature_columns = X.columns.tolist()
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.base_model.fit(X_scaled, y)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            return False
    
    def create_labels(self, ohlc_data: pd.DataFrame, lookahead_periods: int = 5, 
                     profit_threshold: float = 0.0005) -> pd.Series:
        """Create trading labels based on future price movements"""
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
            pass
        
        return labels
    
    def _rule_based_signal(self, indicators: Dict[str, Any], sensitivity: str) -> Dict[str, Any]:
        """Fallback rule-based signal generation"""
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
            return {'action': 'HOLD', 'confidence': 50.0, 'method': 'Rule-based (Error)'}
    
    def provide_signal_feedback(self, signal_id: str, actual_outcome: str):
        """Provide feedback on signal accuracy for learning"""
        # Find the signal in history
        for signal_data in self.signal_history:
            if signal_data.get('id') == signal_id:
                # Collect feedback for adaptive learning
                self.adaptive_engine.collect_signal_feedback(
                    signal_data['signal'],
                    actual_outcome
                )
                break
    
    def record_trade_outcome(self, trade_data: Dict):
        """Record trade outcome for learning"""
        self.adaptive_engine.collect_trade_feedback(trade_data)
    
    def show_model_insights(self):
        """Show insights about the model's decision making"""
        st.subheader("🔍 AI Decision Insights")
        
        # Show recent signal performance
        if self.signal_history:
            recent_signals = self.signal_history[-5:]
            
            st.write("**Recent AI Decisions:**")
            for signal_data in reversed(recent_signals):
                timestamp = signal_data['timestamp'].strftime("%H:%M")
                signal = signal_data['signal']
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.write(f"**{timestamp}**")
                
                with col2:
                    action_color = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "⚪"
                    st.write(f"{action_color} {signal['action']} - {signal.get('method', 'Unknown')}")
                
                with col3:
                    st.write(f"{signal['confidence']:.0f}%")
        
        # Show adaptive learning dashboard
        self.adaptive_engine.show_learning_dashboard()