import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import time

class PersonalTradingAssistant:
    """
    Personal trading assistant for beginners with automated features
    """
    
    def __init__(self):
        self.initialize_settings()
    
    def initialize_settings(self):
        """Initialize personal settings and preferences"""
        if 'personal_settings' not in st.session_state:
            st.session_state.personal_settings = {
                'account_balance': 1000.0,
                'risk_per_trade': 2.0,
                'experience_level': 'Beginner',
                'preferred_pairs': ['EUR/USD', 'GBP/USD'],
                'trading_hours': 'London/New York',
                'notifications_enabled': True,
                'auto_calculate_position': True
            }
        
        if 'trading_journal' not in st.session_state:
            st.session_state.trading_journal = []
        
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
    
    def show_beginner_setup(self):
        """Show beginner-friendly setup wizard"""
        # Ensure settings are initialized first
        self.initialize_settings()
        
        st.subheader("🎯 Personal Trading Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Basic Information")
            
            # Account balance
            if st.session_state.personal_settings is None:
                st.session_state.personal_settings = {}
            current_balance = st.session_state.personal_settings.get('account_balance', 1000.0)
            new_balance = st.number_input(
                "Your Trading Account Balance ($)",
                min_value=100.0,
                max_value=100000.0,
                value=current_balance,
                step=100.0,
                help="Enter your actual account balance for accurate position sizing"
            )
            
            # Experience level
            if st.session_state.personal_settings is None:
                st.session_state.personal_settings = {}
            current_experience = st.session_state.personal_settings.get('experience_level', 'Complete Beginner')
            experience = st.selectbox(
                "Your Trading Experience",
                ['Complete Beginner', 'Some Experience', 'Experienced'],
                index=['Complete Beginner', 'Some Experience', 'Experienced'].index(current_experience),
                help="This helps me adjust recommendations for your skill level"
            )
            
            # Risk tolerance
            if st.session_state.personal_settings is None:
                st.session_state.personal_settings = {}
            current_risk = st.session_state.personal_settings.get('risk_per_trade', 2.0)
            risk_pct = st.slider(
                "How much of your account to risk per trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=current_risk,
                step=0.1,
                help="Beginners should start with 1-2%. Never risk more than you can afford to lose."
            )
        
        with col2:
            st.markdown("### Trading Preferences")
            
            # Preferred currency pairs
            all_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
            if st.session_state.personal_settings is None:
                st.session_state.personal_settings = {}
            current_pairs = st.session_state.personal_settings.get('preferred_pairs', ['EUR/USD'])
            preferred_pairs = st.multiselect(
                "Which currency pairs interest you?",
                all_pairs,
                default=current_pairs,
                help="Start with EUR/USD - it's the most predictable for beginners"
            )
            
            # Trading session
            trading_session = st.selectbox(
                "When do you plan to trade?",
                ['London Session (7-16 UTC)', 'New York Session (12-21 UTC)', 'Both Sessions', 'Asian Session (23-8 UTC)'],
                help="London and New York sessions have the most activity"
            )
            
            # Notifications
            notifications = st.checkbox(
                "Enable trading alerts",
                value=st.session_state.personal_settings['notifications_enabled'],
                help="Get notified when strong signals appear"
            )
        
        if st.button("💾 Save Personal Settings"):
            st.session_state.personal_settings.update({
                'account_balance': new_balance,
                'risk_per_trade': risk_pct,
                'experience_level': experience,
                'preferred_pairs': preferred_pairs,
                'trading_hours': trading_session,
                'notifications_enabled': notifications
            })
            st.success("Settings saved! Your trading recommendations are now personalized.")
            st.rerun()
    
    def calculate_position_size(self, signal_data: Dict, pair: str) -> Dict:
        """Calculate optimal position size based on personal settings"""
        settings = st.session_state.personal_settings
        account_balance = settings['account_balance']
        risk_percentage = settings['risk_per_trade']
        
        # Risk amount in dollars
        risk_amount = account_balance * (risk_percentage / 100)
        
        # Get stop loss from signal
        stop_loss_pips = signal_data.get('stop_loss_pips', 15)
        
        # Calculate pip value (simplified)
        if 'JPY' in pair:
            pip_value = 0.01  # For JPY pairs
        else:
            pip_value = 0.0001  # For other pairs
        
        # Position size calculation
        pip_value_dollars = pip_value * 10000  # Standard lot
        position_size = risk_amount / (stop_loss_pips * pip_value_dollars)
        
        # Round to appropriate lot size
        if position_size < 0.01:
            position_size = 0.01  # Minimum micro lot
        else:
            position_size = round(position_size, 2)
        
        return {
            'position_size': position_size,
            'risk_amount': risk_amount,
            'potential_profit': risk_amount * signal_data.get('risk_reward_ratio', 2),
            'lot_type': 'Micro' if position_size < 0.1 else 'Mini' if position_size < 1 else 'Standard'
        }
    
    def show_simple_signal_card(self, signal: Dict, pair: str):
        """Show beginner-friendly signal card"""
        
        # Calculate position sizing
        position_info = self.calculate_position_size(signal, pair)
        
        # Create signal card
        if signal['action'] == 'BUY':
            st.success("🟢 **BUY OPPORTUNITY DETECTED**")
        elif signal['action'] == 'SELL':
            st.error("🔴 **SELL OPPORTUNITY DETECTED**")
        else:
            st.info("⚪ **WAIT** - No clear opportunity right now")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Signal Strength", f"{signal['confidence']:.0f}%")
            
        with col2:
            st.metric("Potential Risk", f"${position_info['risk_amount']:.2f}")
            
        with col3:
            st.metric("Potential Profit", f"${position_info['potential_profit']:.2f}")
        
        # Simple explanation
        st.markdown("### What this means:")
        if signal['action'] == 'BUY':
            st.write("📈 The price is likely to go UP. Consider buying this currency pair.")
        else:
            st.write("📉 The price is likely to go DOWN. Consider selling this currency pair.")
        
        # Trade details in simple terms
        with st.expander("📊 Trade Details (Click to expand)"):
            st.write(f"**Currency Pair:** {pair}")
            st.write(f"**Action:** {signal['action']}")
            st.write(f"**Entry Price:** {signal.get('entry_price', 'Market Price')}")
            st.write(f"**Stop Loss:** {signal.get('stop_loss', 'Auto-calculated')}")
            st.write(f"**Take Profit:** {signal.get('take_profit', 'Auto-calculated')}")
            st.write(f"**Position Size:** {position_info['position_size']} {position_info['lot_type']} lots")
            st.write(f"**Maximum Risk:** ${position_info['risk_amount']:.2f} ({st.session_state.personal_settings['risk_per_trade']}% of account)")
    
    def show_beginner_explanation(self, indicators: Dict):
        """Show simple explanations of market conditions"""
        st.subheader("📚 What's Happening in the Market")
        
        # Simplify technical indicators
        explanations = []
        
        if 'rsi' in indicators and not indicators['rsi'].empty:
            rsi_value = indicators['rsi'].iloc[-1]
            if rsi_value > 70:
                explanations.append("🔴 **Market is overheated** - Price might fall soon")
            elif rsi_value < 30:
                explanations.append("🟢 **Market is oversold** - Price might rise soon")
            else:
                explanations.append("🟡 **Market is balanced** - No extreme conditions")
        
        if 'macd' in indicators and 'macd_signal' in indicators:
            if not indicators['macd'].empty and not indicators['macd_signal'].empty:
                macd_current = indicators['macd'].iloc[-1]
                signal_current = indicators['macd_signal'].iloc[-1]
                
                if macd_current > signal_current:
                    explanations.append("🟢 **Upward momentum** - Buyers are in control")
                else:
                    explanations.append("🔴 **Downward momentum** - Sellers are in control")
        
        for explanation in explanations:
            st.write(explanation)
        
        if not explanations:
            st.write("📊 Market data is being analyzed...")
    
    def add_to_journal(self, trade_data: Dict):
        """Add trade to personal journal"""
        trade_data['timestamp'] = datetime.now()
        trade_data['id'] = len(st.session_state.trading_journal) + 1
        st.session_state.trading_journal.append(trade_data)
    
    def show_trading_journal(self):
        """Show personal trading journal"""
        st.subheader("📖 My Trading Journal")
        
        if not st.session_state.trading_journal:
            st.info("No trades recorded yet. Start logging your trades to track performance!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.trading_journal)
        
        # Performance summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(df))
        
        with col2:
            if 'result' in df.columns:
                wins = len(df[df['result'] == 'Win'])
                win_rate = (wins / len(df)) * 100 if len(df) > 0 else 0
                st.metric("Win Rate", f"{win_rate:.1f}%")
            else:
                st.metric("Win Rate", "Track trades to see")
        
        with col3:
            if 'profit_loss' in df.columns:
                total_pnl = df['profit_loss'].sum()
                st.metric("Total P&L", f"${total_pnl:.2f}")
            else:
                st.metric("Total P&L", "$0.00")
        
        with col4:
            if 'profit_loss' in df.columns and len(df) > 0:
                avg_trade = df['profit_loss'].mean()
                st.metric("Avg per Trade", f"${avg_trade:.2f}")
            else:
                st.metric("Avg per Trade", "$0.00")
        
        # Recent trades
        st.write("### Recent Trades")
        display_columns = ['timestamp', 'pair', 'action', 'confidence', 'result', 'profit_loss']
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            recent_df = df[available_columns].tail(10).sort_values('timestamp', ascending=False)
            st.dataframe(recent_df, use_container_width=True)
    
    def show_risk_manager(self):
        """Show personal risk management dashboard"""
        st.subheader("🛡️ Risk Management Dashboard")
        
        settings = st.session_state.personal_settings
        account_balance = settings['account_balance']
        risk_per_trade = settings['risk_per_trade']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Current Risk Settings")
            st.write(f"**Account Balance:** ${account_balance:,.2f}")
            st.write(f"**Risk per Trade:** {risk_per_trade}%")
            st.write(f"**Maximum Risk:** ${account_balance * risk_per_trade / 100:.2f}")
            
            # Risk level assessment
            if risk_per_trade <= 1:
                st.success("✅ Very Conservative Risk Level")
            elif risk_per_trade <= 2:
                st.info("✅ Conservative Risk Level")
            elif risk_per_trade <= 3:
                st.warning("⚠️ Moderate Risk Level")
            else:
                st.error("⚠️ High Risk Level - Consider reducing")
        
        with col2:
            st.write("### Risk Guidelines")
            st.write("**For Beginners:**")
            st.write("• Start with 1% risk per trade")
            st.write("• Never risk more than 2%")
            st.write("• Use stop losses on every trade")
            st.write("• Don't trade when emotional")
            
            st.write("**Red Flags:**")
            st.write("🚨 Risking more than 3% per trade")
            st.write("🚨 Trading without stop losses")
            st.write("🚨 Revenge trading after losses")
    
    def create_alert(self, message: str, alert_type: str = "info"):
        """Create personal trading alert"""
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'type': alert_type,
            'read': False
        }
        st.session_state.alerts.append(alert)
    
    def show_alerts(self):
        """Show personal alerts"""
        if not st.session_state.alerts:
            return
        
        st.subheader("🔔 Your Trading Alerts")
        
        for i, alert in enumerate(reversed(st.session_state.alerts[-5:])):  # Show latest 5
            alert_time = alert['timestamp'].strftime("%H:%M")
            
            if alert['type'] == 'success':
                st.success(f"**{alert_time}** - {alert['message']}")
            elif alert['type'] == 'warning':
                st.warning(f"**{alert_time}** - {alert['message']}")
            elif alert['type'] == 'error':
                st.error(f"**{alert_time}** - {alert['message']}")
            else:
                st.info(f"**{alert_time}** - {alert['message']}")
    
    def get_beginner_recommendations(self, current_signal: Dict, pair: str) -> List[str]:
        """Generate beginner-friendly recommendations"""
        recommendations = []
        settings = st.session_state.personal_settings
        
        # Experience-based recommendations
        if settings['experience_level'] == 'Complete Beginner':
            recommendations.append("💡 Start with demo trading before using real money")
            recommendations.append("📚 Only trade EUR/USD until you gain experience")
            
        # Signal-based recommendations
        if current_signal['confidence'] < 60:
            recommendations.append("⏳ Wait for a stronger signal (60%+ confidence)")
        elif current_signal['confidence'] > 80:
            recommendations.append("🎯 This is a high-confidence signal - good opportunity")
        
        # Risk-based recommendations
        if settings['risk_per_trade'] > 2:
            recommendations.append("⚠️ Consider reducing your risk per trade to 2% or less")
        
        # Time-based recommendations
        current_hour = datetime.now().hour
        if 7 <= current_hour <= 16 or 12 <= current_hour <= 21:
            recommendations.append("✅ Good time to trade - markets are active")
        else:
            recommendations.append("😴 Markets are less active now - be extra cautious")
        
        return recommendations