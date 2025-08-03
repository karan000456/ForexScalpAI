import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

class AdaptiveLearningEngine:
    """
    Self-improving AI system that learns from trading outcomes and market feedback
    """
    
    def __init__(self):
        self.initialize_learning_system()
        self.setup_logging()
    
    def initialize_learning_system(self):
        """Initialize the adaptive learning components"""
        if 'learning_data' not in st.session_state:
            st.session_state.learning_data = {
                'trade_outcomes': [],
                'signal_feedback': [],
                'market_patterns': [],
                'model_performance': [],
                'learning_stats': {
                    'total_feedback': 0,
                    'successful_predictions': 0,
                    'failed_predictions': 0,
                    'adaptation_count': 0,
                    'last_model_update': None
                }
            }
        
        if 'adaptive_models' not in st.session_state:
            st.session_state.adaptive_models = {}
        
        if 'learning_config' not in st.session_state:
            st.session_state.learning_config = {
                'min_feedback_for_adaptation': 10,
                'adaptation_threshold': 0.6,  # Retrain if accuracy drops below this
                'feature_importance_threshold': 0.05,
                'max_historical_data': 1000,
                'learning_rate': 0.1
            }
    
    def setup_logging(self):
        """Setup logging for learning system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('AdaptiveLearning')
    
    def collect_trade_feedback(self, trade_data: Dict):
        """Collect feedback from completed trades"""
        feedback_entry = {
            'timestamp': datetime.now(),
            'pair': trade_data.get('pair'),
            'action': trade_data.get('action'),
            'confidence': trade_data.get('confidence'),
            'entry_price': trade_data.get('entry_price'),
            'exit_price': trade_data.get('exit_price'),
            'result': trade_data.get('result'),  # 'Win', 'Loss', 'Breakeven'
            'profit_loss': trade_data.get('profit_loss', 0),
            'market_conditions': trade_data.get('market_conditions', {}),
            'technical_indicators': trade_data.get('indicators', {}),
            'trade_duration': trade_data.get('duration_minutes', 0)
        }
        
        st.session_state.learning_data['trade_outcomes'].append(feedback_entry)
        
        # Update learning statistics
        stats = st.session_state.learning_data['learning_stats']
        stats['total_feedback'] += 1
        
        if trade_data.get('result') == 'Win':
            stats['successful_predictions'] += 1
        elif trade_data.get('result') == 'Loss':
            stats['failed_predictions'] += 1
        
        self.logger.info(f"Collected trade feedback: {trade_data.get('result')} for {trade_data.get('pair')}")
        
        # Trigger adaptation if enough feedback is collected
        self.check_adaptation_trigger()
    
    def collect_signal_feedback(self, signal_data: Dict, market_outcome: str):
        """Collect feedback on signal accuracy"""
        feedback_entry = {
            'timestamp': datetime.now(),
            'pair': signal_data.get('pair'),
            'predicted_action': signal_data.get('action'),
            'confidence': signal_data.get('confidence'),
            'actual_outcome': market_outcome,  # 'correct', 'incorrect', 'neutral'
            'market_conditions': signal_data.get('market_conditions', {}),
            'indicators_used': signal_data.get('indicators', {}),
            'signal_strength': signal_data.get('signal_strength', 0)
        }
        
        st.session_state.learning_data['signal_feedback'].append(feedback_entry)
        self.logger.info(f"Collected signal feedback: {market_outcome} for {signal_data.get('pair')}")
    
    def analyze_market_patterns(self, price_data: pd.DataFrame, indicators: Dict) -> Dict:
        """Analyze current market patterns and store learning data"""
        try:
            current_price = price_data['close'].iloc[-1]
            price_change_1h = (current_price - price_data['close'].iloc[-12]) / price_data['close'].iloc[-12] * 100
            price_change_4h = (current_price - price_data['close'].iloc[-48]) / price_data['close'].iloc[-48] * 100
            
            volatility = price_data['close'].rolling(window=20).std().iloc[-1]
            avg_volume_proxy = (price_data['high'] - price_data['low']).rolling(window=20).mean().iloc[-1]
            
            pattern_data = {
                'timestamp': datetime.now(),
                'price_change_1h': price_change_1h,
                'price_change_4h': price_change_4h,
                'volatility': volatility,
                'volume_proxy': avg_volume_proxy,
                'rsi': indicators.get('rsi', pd.Series()).iloc[-1] if 'rsi' in indicators else 50,
                'macd': indicators.get('macd', pd.Series()).iloc[-1] if 'macd' in indicators else 0,
                'trend_strength': self.calculate_trend_strength(price_data),
                'market_session': self.get_market_session()
            }
            
            st.session_state.learning_data['market_patterns'].append(pattern_data)
            return pattern_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing market patterns: {e}")
            return {}
    
    def calculate_trend_strength(self, price_data: pd.DataFrame) -> float:
        """Calculate trend strength indicator"""
        try:
            sma_20 = price_data['close'].rolling(window=20).mean()
            sma_50 = price_data['close'].rolling(window=50).mean()
            
            if len(sma_20) < 50 or len(sma_50) < 50:
                return 0.5
            
            trend_strength = abs(sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1]
            return min(trend_strength * 10, 1.0)  # Normalize to 0-1
            
        except Exception:
            return 0.5
    
    def get_market_session(self) -> str:
        """Determine current market session"""
        current_hour = datetime.now().hour
        
        if 23 <= current_hour or current_hour < 8:
            return 'Asian'
        elif 7 <= current_hour < 16:
            return 'London'
        elif 12 <= current_hour < 21:
            return 'NewYork'
        else:
            return 'Overlap'
    
    def check_adaptation_trigger(self):
        """Check if model needs to be retrained based on performance"""
        stats = st.session_state.learning_data['learning_stats']
        config = st.session_state.learning_config
        
        total_feedback = stats['total_feedback']
        
        if total_feedback < config['min_feedback_for_adaptation']:
            return
        
        # Calculate recent accuracy
        recent_trades = st.session_state.learning_data['trade_outcomes'][-20:]
        if len(recent_trades) < 10:
            return
        
        recent_wins = len([t for t in recent_trades if t['result'] == 'Win'])
        recent_accuracy = recent_wins / len(recent_trades)
        
        if recent_accuracy < config['adaptation_threshold']:
            self.logger.info(f"Triggering model adaptation. Recent accuracy: {recent_accuracy:.2f}")
            self.adapt_model()
    
    def adapt_model(self):
        """Retrain and adapt the model based on collected feedback"""
        try:
            # Prepare training data from feedback
            training_data = self.prepare_adaptive_training_data()
            
            if len(training_data) < 20:  # Need minimum data for retraining
                self.logger.warning("Insufficient data for model adaptation")
                return
            
            # Create adaptive model
            X, y = self.extract_features_and_labels(training_data)
            
            if len(X) == 0 or len(y) == 0:
                return
            
            # Train improved model
            improved_model = self.train_adaptive_model(X, y)
            
            if improved_model:
                # Store the improved model
                model_key = f"adaptive_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.adaptive_models[model_key] = improved_model
                
                # Update statistics
                stats = st.session_state.learning_data['learning_stats']
                stats['adaptation_count'] += 1
                stats['last_model_update'] = datetime.now()
                
                self.logger.info("Model successfully adapted with new feedback")
                
                # Store performance metrics
                self.store_model_performance(improved_model, X, y)
            
        except Exception as e:
            self.logger.error(f"Error during model adaptation: {e}")
    
    def prepare_adaptive_training_data(self) -> List[Dict]:
        """Prepare training data from collected feedback"""
        training_data = []
        
        # Use trade outcomes as primary training data
        for trade in st.session_state.learning_data['trade_outcomes']:
            if trade.get('technical_indicators') and trade.get('result'):
                training_entry = {
                    'indicators': trade['technical_indicators'],
                    'market_conditions': trade.get('market_conditions', {}),
                    'outcome': 1 if trade['result'] == 'Win' else 0,
                    'confidence': trade.get('confidence', 50),
                    'pair': trade.get('pair', 'EUR/USD')
                }
                training_data.append(training_entry)
        
        return training_data
    
    def extract_features_and_labels(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features and labels from training data"""
        features = []
        labels = []
        
        for entry in training_data:
            try:
                feature_vector = []
                indicators = entry.get('indicators', {})
                
                # Extract key technical indicators
                feature_vector.append(indicators.get('rsi', 50))
                feature_vector.append(indicators.get('macd', 0))
                feature_vector.append(indicators.get('sma_20', 1))
                feature_vector.append(indicators.get('ema_12', 1))
                feature_vector.append(indicators.get('atr', 0.001))
                feature_vector.append(indicators.get('stoch_k', 50))
                feature_vector.append(entry.get('confidence', 50))
                
                # Add market conditions
                market_conditions = entry.get('market_conditions', {})
                feature_vector.append(market_conditions.get('volatility', 0.001))
                feature_vector.append(market_conditions.get('trend_strength', 0.5))
                
                # Only add if we have valid data
                if len(feature_vector) == 9 and all(isinstance(x, (int, float)) for x in feature_vector):
                    features.append(feature_vector)
                    labels.append(entry['outcome'])
                    
            except Exception as e:
                continue
        
        if not features:
            return np.array([]), np.array([])
        
        return np.array(features), np.array(labels)
    
    def train_adaptive_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train an improved model with feedback data"""
        if len(X) < 10:
            return None
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest with adaptive parameters
            n_estimators = min(100 + len(X_train) // 10, 200)  # Adaptive forest size
            
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=8,
                min_samples_split=max(2, len(X_train) // 20),
                min_samples_leaf=max(1, len(X_train) // 50),
                random_state=42,
                class_weight='balanced'
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_accuracy = model.score(X_train_scaled, y_train)
            test_accuracy = model.score(X_test_scaled, y_test)
            
            self.logger.info(f"Adaptive model trained - Train: {train_accuracy:.3f}, Test: {test_accuracy:.3f}")
            
            return {
                'model': model,
                'scaler': scaler,
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'feature_names': ['rsi', 'macd', 'sma_20', 'ema_12', 'atr', 'stoch_k', 'confidence', 'volatility', 'trend_strength'],
                'created_at': datetime.now(),
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            self.logger.error(f"Error training adaptive model: {e}")
            return None
    
    def store_model_performance(self, model_data: Dict, X: np.ndarray, y: np.ndarray):
        """Store model performance metrics"""
        performance_entry = {
            'timestamp': datetime.now(),
            'train_accuracy': model_data['train_accuracy'],
            'test_accuracy': model_data['test_accuracy'],
            'training_samples': len(X),
            'feature_importance': dict(zip(
                model_data['feature_names'],
                model_data['model'].feature_importances_
            )),
            'model_id': f"adaptive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        st.session_state.learning_data['model_performance'].append(performance_entry)
    
    def get_adaptive_prediction(self, current_indicators: Dict, pair: str) -> Dict:
        """Get prediction using the latest adaptive model"""
        if not st.session_state.adaptive_models:
            return None
        
        try:
            # Get the latest model
            latest_model_key = max(st.session_state.adaptive_models.keys())
            model_data = st.session_state.adaptive_models[latest_model_key]
            
            # Prepare feature vector
            feature_vector = [
                current_indicators.get('rsi', 50),
                current_indicators.get('macd', 0),
                current_indicators.get('sma_20', 1),
                current_indicators.get('ema_12', 1),
                current_indicators.get('atr', 0.001),
                current_indicators.get('stoch_k', 50),
                70,  # Default confidence
                current_indicators.get('volatility', 0.001),
                0.5  # Default trend strength
            ]
            
            # Make prediction
            X = np.array([feature_vector])
            X_scaled = model_data['scaler'].transform(X)
            
            prediction = model_data['model'].predict(X_scaled)[0]
            probabilities = model_data['model'].predict_proba(X_scaled)[0]
            
            confidence = max(probabilities) * 100
            action = 'BUY' if prediction == 1 else 'SELL' if prediction == 0 and confidence > 60 else 'HOLD'
            
            return {
                'action': action,
                'confidence': confidence,
                'method': 'Adaptive ML',
                'model_accuracy': model_data['test_accuracy'],
                'training_samples': model_data['training_samples'],
                'probabilities': probabilities.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting adaptive prediction: {e}")
            return None
    
    def show_learning_dashboard(self):
        """Display learning system dashboard"""
        st.subheader("🧠 AI Learning Dashboard")
        
        stats = st.session_state.learning_data['learning_stats']
        
        # Learning Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feedback", stats['total_feedback'])
        
        with col2:
            success_rate = (stats['successful_predictions'] / max(stats['total_feedback'], 1)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            st.metric("Model Updates", stats['adaptation_count'])
        
        with col4:
            last_update = stats.get('last_model_update')
            if last_update:
                days_ago = (datetime.now() - last_update).days
                st.metric("Last Update", f"{days_ago} days ago")
            else:
                st.metric("Last Update", "Never")
        
        # Model Performance Over Time
        if st.session_state.learning_data['model_performance']:
            st.subheader("📈 Model Performance History")
            
            performance_df = pd.DataFrame(st.session_state.learning_data['model_performance'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                latest_performance = performance_df.iloc[-1]
                st.write("**Latest Model Performance:**")
                st.write(f"Training Accuracy: {latest_performance['train_accuracy']:.3f}")
                st.write(f"Test Accuracy: {latest_performance['test_accuracy']:.3f}")
                st.write(f"Training Samples: {latest_performance['training_samples']}")
            
            with col2:
                if len(performance_df) > 1:
                    st.write("**Performance Trend:**")
                    accuracy_trend = performance_df['test_accuracy'].diff().iloc[-1]
                    if accuracy_trend > 0:
                        st.success(f"Improving (+{accuracy_trend:.3f})")
                    elif accuracy_trend < 0:
                        st.warning(f"Declining ({accuracy_trend:.3f})")
                    else:
                        st.info("Stable performance")
        
        # Feature Importance
        if st.session_state.learning_data['model_performance']:
            latest_model = st.session_state.learning_data['model_performance'][-1]
            importance = latest_model.get('feature_importance', {})
            
            if importance:
                st.subheader("🎯 What the AI Focuses On")
                
                # Sort by importance
                sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
                
                for feature, importance_score in sorted_importance[:5]:
                    st.write(f"**{feature.upper()}:** {importance_score:.3f}")
        
        # Recent Learning Activity
        st.subheader("📊 Recent Learning Activity") 
        
        recent_trades = st.session_state.learning_data['trade_outcomes'][-10:]
        if recent_trades:
            for trade in reversed(recent_trades):
                time_str = trade['timestamp'].strftime("%H:%M")
                result_color = "🟢" if trade['result'] == 'Win' else "🔴" if trade['result'] == 'Loss' else "🟡"
                st.write(f"{result_color} **{time_str}** - {trade['action']} {trade['pair']} → {trade['result']}")
        else:
            st.info("No learning data available yet. Complete some trades to see AI learning progress.")
    
    def export_learning_data(self) -> str:
        """Export learning data for analysis"""
        try:
            learning_export = {
                'export_timestamp': datetime.now().isoformat(),
                'learning_stats': st.session_state.learning_data['learning_stats'],
                'trade_outcomes': [
                    {**trade, 'timestamp': trade['timestamp'].isoformat()}
                    for trade in st.session_state.learning_data['trade_outcomes']
                ],
                'model_performance': [
                    {**perf, 'timestamp': perf['timestamp'].isoformat()}
                    for perf in st.session_state.learning_data['model_performance']
                ]
            }
            
            return json.dumps(learning_export, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error exporting learning data: {e}")
            return "{}"
    
    def reset_learning_system(self):
        """Reset the learning system (use with caution)"""
        st.session_state.learning_data = {
            'trade_outcomes': [],
            'signal_feedback': [],
            'market_patterns': [],
            'model_performance': [],
            'learning_stats': {
                'total_feedback': 0,
                'successful_predictions': 0,
                'failed_predictions': 0,
                'adaptation_count': 0,
                'last_model_update': None
            }
        }
        st.session_state.adaptive_models = {}
        self.logger.info("Learning system reset")