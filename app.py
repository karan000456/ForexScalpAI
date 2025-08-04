import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import time
import datetime
from forex_data import ForexDataProvider
from technical_indicators import TechnicalIndicators
from enhanced_ml_signals import EnhancedMLSignalGenerator
from utils import format_currency, calculate_profit_loss
from user_guide import show_user_guide
from enhanced_features import PersonalTradingAssistant
from notifications import TradingNotifications, BeginnerGuidance
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Personal AI Forex Trading Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'signal_history' not in st.session_state:
    st.session_state.signal_history = []
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'personal_settings' not in st.session_state:
    st.session_state.personal_settings = None
if 'trading_journal' not in st.session_state:
    st.session_state.trading_journal = []
if 'guidance_progress' not in st.session_state:
    st.session_state.guidance_progress = {'show_guidance': True}
if 'learning_data' not in st.session_state:
    st.session_state.learning_data = {'learning_stats': {'total_feedback': 0, 'successful_predictions': 0, 'adaptation_count': 0}}
if 'show_notifications' not in st.session_state:
    st.session_state.show_notifications = False
if 'show_setup' not in st.session_state:
    st.session_state.show_setup = False

# Initialize components
@st.cache_resource
def initialize_components():
    forex_data = ForexDataProvider()
    tech_indicators = TechnicalIndicators()
    ml_generator = EnhancedMLSignalGenerator()
    assistant = PersonalTradingAssistant()
    notifications = TradingNotifications()
    guidance = BeginnerGuidance()
    return forex_data, tech_indicators, ml_generator, assistant, notifications, guidance

forex_data, tech_indicators, ml_generator, assistant, notifications, guidance = initialize_components()

# Main title
st.title("🤖 Personal AI Forex Trading Assistant")
st.markdown("### Simple, Safe, and Smart Trading that Learns from Every Decision")

# Show AI learning status
if 'learning_data' in st.session_state and st.session_state.learning_data.get('learning_stats'):
    stats = st.session_state.learning_data['learning_stats']
    if stats['total_feedback'] > 0:
        success_rate = (stats['successful_predictions'] / stats['total_feedback']) * 100
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AI Learning Progress", f"{stats['total_feedback']} decisions")
        with col2:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col3:
            st.metric("Model Updates", stats['adaptation_count'])
        st.markdown("---")

# Check if user needs initial setup
if not st.session_state.get('personal_settings'):
    st.warning("👋 Welcome! Let's set up your personal trading profile first.")
    assistant.show_beginner_setup()
    st.stop()

# Main navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Simple Trading", 
    "📊 Advanced Charts", 
    "📖 My Journal", 
    "🛡️ Risk Manager", 
    "🧠 AI Learning",
    "📚 Learn Trading"
])

# Sidebar - Personal Settings
st.sidebar.header("⚙️ Your Trading Profile")
settings = st.session_state.personal_settings

# Ensure settings is not None
if settings is None:
    st.error("Personal settings not found. Please reload the page.")
    st.stop()

# Quick settings display
st.sidebar.write(f"**Account:** ${settings['account_balance']:,.2f}")
st.sidebar.write(f"**Risk Level:** {settings['risk_per_trade']}%")
st.sidebar.write(f"**Experience:** {settings['experience_level']}")

# Currency pair selection (only show preferred pairs)
preferred_pairs = settings.get('preferred_pairs', ['EUR/USD'])
if len(preferred_pairs) == 1:
    selected_pair = preferred_pairs[0]
    st.sidebar.write(f"**Trading:** {selected_pair}")
else:
    selected_pair = st.sidebar.selectbox("Select Pair", preferred_pairs)

# Quick actions
if st.sidebar.button("⚙️ Update Profile"):
    st.session_state.show_setup = True

if st.sidebar.button("🔔 Notifications"):
    st.session_state.show_notifications = True

# Show notifications if requested
if st.session_state.get('show_notifications'):
    with st.sidebar:
        notifications.show_notification_settings()
        if st.button("✅ Close"):
            st.session_state.show_notifications = False
            st.rerun()

# Show setup if requested
if st.session_state.get('show_setup'):
    with st.container():
        assistant.show_beginner_setup()
        if st.button("✅ Done"):
            st.session_state.show_setup = False
            st.rerun()

# Tab 1: Simple Trading (Beginner-friendly)
with tab1:
    # Show beginner guidance if enabled
    if st.session_state.guidance_progress.get('show_guidance', True):
        guidance.show_beginner_guidance()
        st.markdown("---")
    
    # Show notifications
    notifications.show_notifications()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"💹 {selected_pair} - What Should I Do?")
        
        try:
            # Get live data
            price_data = forex_data.get_live_data(selected_pair)
            
            if price_data is not None and not price_data.empty:
                # Calculate indicators
                indicators = tech_indicators.calculate_all_indicators(price_data)
                
                # Generate enhanced signal with adaptive learning
                current_signal = ml_generator.generate_enhanced_signal(price_data, indicators, "Moderate", selected_pair)
                
                # Add some beginner-friendly data to signal
                current_price = price_data['close'].iloc[-1]
                current_signal['entry_price'] = current_price
                current_signal['stop_loss_pips'] = 15
                current_signal['risk_reward_ratio'] = 2
                
                # Show simple signal card
                assistant.show_simple_signal_card(current_signal, selected_pair)
                
                # Check for notifications
                notifications.check_signal_notifications(current_signal, selected_pair)
                notifications.check_market_notifications(indicators, selected_pair)
                
                # Position sizing info
                position_info = assistant.calculate_position_size(current_signal, selected_pair)
                notifications.check_risk_notifications(position_info, settings)
                
                # Simple chart
                st.subheader("📈 Price Chart (Last 24 Hours)")
                
                fig = go.Figure()
                
                # Simple line chart for beginners
                fig.add_trace(go.Scatter(
                    x=price_data.index,
                    y=price_data['close'],
                    mode='lines',
                    name='Price',
                    line=dict(color='blue', width=2)
                ))
                
                # Add current signal marker
                if current_signal['action'] != 'HOLD':
                    color = 'green' if current_signal['action'] == 'BUY' else 'red'
                    symbol = 'triangle-up' if current_signal['action'] == 'BUY' else 'triangle-down'
                    
                    fig.add_trace(go.Scatter(
                        x=[price_data.index[-1]],
                        y=[current_price],
                        mode='markers',
                        marker=dict(symbol=symbol, size=15, color=color),
                        name=f'{current_signal["action"]} Signal'
                    ))
                
                fig.update_layout(
                    height=400,
                    title=f"{selected_pair} Price Movement",
                    showlegend=True,
                    xaxis_title="Time",
                    yaxis_title="Price"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Record trade button
                if current_signal['action'] != 'HOLD':
                    if st.button(f"📝 I want to {current_signal['action']} (Log this idea)", key="log_trade"):
                        trade_data = {
                            'pair': selected_pair,
                            'action': current_signal['action'],
                            'confidence': current_signal['confidence'],
                            'entry_price': current_price,
                            'position_size': position_info['position_size'],
                            'risk_amount': position_info['risk_amount'],
                            'status': 'Planned'
                        }
                        assistant.add_to_journal(trade_data)
                        st.success("Trade idea saved to your journal!")
                        st.rerun()
            
            else:
                st.error("Unable to get market data right now. Please try again in a moment.")
        
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
    
    with col2:
        st.subheader("🎓 What's Happening?")
        
        # Show beginner explanations
        try:
            # Get fresh data for this column
            price_data_col2 = forex_data.get_live_data(selected_pair)
            if price_data_col2 is not None and not price_data_col2.empty:
                indicators = tech_indicators.calculate_all_indicators(price_data_col2)
                assistant.show_beginner_explanation(indicators)
                
                # Recommendations
                current_signal = ml_generator.generate_enhanced_signal(price_data_col2, indicators, "Moderate", selected_pair)
                recommendations = assistant.get_beginner_recommendations(current_signal, selected_pair)
                
                st.subheader("💡 My Recommendations")
                for rec in recommendations:
                    st.write(rec)
        except Exception as e:
            st.info("Market analysis will appear here when data is available.")
        
        # Quick stats
        st.subheader("📊 Your Stats")
        journal = st.session_state.trading_journal
        
        if journal:
            total_trades = len(journal)
            planned_trades = len([t for t in journal if t.get('status') == 'Planned'])
            
            st.metric("Ideas Logged", total_trades)
            st.metric("Planned Trades", planned_trades)
        else:
            st.info("No trades logged yet")

# Tab 2: Advanced Charts (for when user gains experience)
with tab2:
    st.subheader(f"📊 {selected_pair} Advanced Analysis")
    
    if settings['experience_level'] == 'Complete Beginner':
        st.info("🎓 This section will unlock as you gain experience. Focus on the Simple Trading tab for now!")
    else:
        # Show full technical analysis (reuse existing code)
        try:
            price_data = forex_data.get_live_data(selected_pair)
            
            if price_data is not None and not price_data.empty:
                indicators = tech_indicators.calculate_all_indicators(price_data)
                current_signal = ml_generator.generate_enhanced_signal(price_data, indicators, "Moderate", selected_pair)
                
                # Create advanced chart
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    subplot_titles=('Price & Moving Averages', 'RSI', 'MACD'),
                    row_heights=[0.6, 0.2, 0.2]
                )
                
                # Candlestick chart
                fig.add_trace(
                    go.Candlestick(
                        x=price_data.index,
                        open=price_data['open'],
                        high=price_data['high'],
                        low=price_data['low'],
                        close=price_data['close'],
                        name='Price'
                    ),
                    row=1, col=1
                )
                
                # Add technical indicators
                if 'sma_20' in indicators:
                    fig.add_trace(
                        go.Scatter(
                            x=price_data.index,
                            y=indicators['sma_20'],
                            name='SMA 20',
                            line=dict(color='orange', width=1)
                        ),
                        row=1, col=1
                    )
                
                if 'rsi' in indicators:
                    fig.add_trace(
                        go.Scatter(
                            x=price_data.index,
                            y=indicators['rsi'],
                            name='RSI',
                            line=dict(color='purple')
                        ),
                        row=2, col=1
                    )
                
                if 'macd' in indicators:
                    fig.add_trace(
                        go.Scatter(
                            x=price_data.index,
                            y=indicators['macd'],
                            name='MACD',
                            line=dict(color='blue')
                        ),
                        row=3, col=1
                    )
                
                fig.update_layout(height=800, title=f"{selected_pair} Technical Analysis")
                st.plotly_chart(fig, use_container_width=True)
                
                # Signal details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Signal", current_signal['action'])
                with col2:
                    st.metric("Confidence", f"{current_signal['confidence']:.1f}%")
                with col3:
                    st.metric("Current Price", format_currency(price_data['close'].iloc[-1], selected_pair))
        
        except Exception as e:
            st.error(f"Error loading advanced charts: {str(e)}")

# Tab 3: Trading Journal
with tab3:
    assistant.show_trading_journal()
    
    # Add trade outcome tracking
    st.subheader("📝 Update Trade Results")
    
    journal = st.session_state.trading_journal
    pending_trades = [t for t in journal if t.get('status') == 'Planned']
    
    if pending_trades:
        for i, trade in enumerate(pending_trades):
            with st.expander(f"Trade {trade['id']}: {trade['action']} {trade['pair']}"):
                st.write(f"**Entry Price:** {trade.get('entry_price', 'N/A')}")
                st.write(f"**Position Size:** {trade.get('position_size', 'N/A')}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ Won", key=f"win_{i}"):
                        trade['status'] = 'Completed'
                        trade['result'] = 'Win'
                        trade['profit_loss'] = trade.get('risk_amount', 50) * 2  # Assume 2:1 reward
                        st.rerun()
                
                with col2:
                    if st.button("❌ Lost", key=f"loss_{i}"):
                        trade['status'] = 'Completed'
                        trade['result'] = 'Loss'
                        trade['profit_loss'] = -trade.get('risk_amount', 50)
                        st.rerun()
                
                with col3:
                    if st.button("⏹️ Cancelled", key=f"cancel_{i}"):
                        trade['status'] = 'Cancelled'
                        trade['result'] = 'Cancelled'
                        trade['profit_loss'] = 0
                        st.rerun()
    else:
        st.info("No pending trades to update")

# Tab 4: Risk Manager
with tab4:
    assistant.show_risk_manager()
    
    # Add daily/weekly limits
    st.subheader("📅 Trading Limits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        daily_limit = st.number_input(
            "Maximum trades per day",
            min_value=1,
            max_value=10,
            value=3,
            help="Limit yourself to avoid overtrading"
        )
    
    with col2:
        loss_limit = st.number_input(
            "Daily loss limit ($)",
            min_value=10.0,
            max_value=500.0,
            value=100.0,
            help="Stop trading if you lose this much in one day"
        )
    
    # Today's trading activity
    today = datetime.datetime.now().date()
    today_trades = [
        t for t in st.session_state.trading_journal 
        if t.get('timestamp', datetime.datetime.now()).date() == today
    ]
    
    today_losses = sum([
        t.get('profit_loss', 0) for t in today_trades 
        if t.get('profit_loss', 0) < 0
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Trades Today", len(today_trades))
        if len(today_trades) >= daily_limit:
            st.error("Daily trade limit reached!")
    
    with col2:
        st.metric("Losses Today", f"${abs(today_losses):.2f}")
        if abs(today_losses) >= loss_limit:
            st.error("Daily loss limit reached!")

# Tab 5: AI Learning Dashboard
with tab5:
    st.header("🧠 AI Learning Dashboard")
    st.markdown("### See How Your AI Assistant Gets Smarter Every Day")
    
    # Show AI decision insights and learning progress
    ml_generator.show_model_insights()
    
    st.markdown("---")
    
    # Trade outcome feedback section
    st.subheader("📝 Help Your AI Learn")
    st.markdown("**Tell the AI how its recent recommendations worked out so it can improve!**")
    
    # Get recent signals for feedback
    recent_signals = getattr(ml_generator, 'signal_history', [])[-5:]
    
    if recent_signals:
        for i, signal_data in enumerate(reversed(recent_signals)):
            timestamp = signal_data['timestamp'].strftime("%H:%M")
            signal = signal_data['signal']
            
            with st.expander(f"Signal from {timestamp}: {signal['action']} - {signal.get('confidence', 0):.0f}% confidence"):
                st.write(f"**Recommendation:** {signal['action']} {signal_data['pair']}")
                st.write(f"**AI Confidence:** {signal.get('confidence', 0):.0f}%")
                st.write(f"**Method:** {signal.get('method', 'Unknown')}")
                
                # Outcome feedback buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ Good call!", key=f"good_{i}"):
                        # Record positive feedback
                        trade_outcome = {
                            'pair': signal_data['pair'],
                            'action': signal['action'],
                            'confidence': signal.get('confidence', 50),
                            'entry_price': signal.get('entry_price', 1.0000),
                            'result': 'Win',
                            'market_conditions': signal.get('market_conditions', {}),
                            'indicators': signal.get('indicators', {})
                        }
                        ml_generator.record_trade_outcome(trade_outcome)
                        st.success("Thanks! The AI learned from this success.")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Wrong call", key=f"bad_{i}"):
                        # Record negative feedback
                        trade_outcome = {
                            'pair': signal_data['pair'],
                            'action': signal['action'],
                            'confidence': signal.get('confidence', 50),
                            'entry_price': signal.get('entry_price', 1.0000),
                            'result': 'Loss',
                            'market_conditions': signal.get('market_conditions', {}),
                            'indicators': signal.get('indicators', {})
                        }
                        ml_generator.record_trade_outcome(trade_outcome)
                        st.success("Thanks! The AI will learn from this mistake.")
                        st.rerun()
                
                with col3:
                    if st.button("⚪ Unclear", key=f"neutral_{i}"):
                        # Record neutral feedback
                        trade_outcome = {
                            'pair': signal_data['pair'],
                            'action': signal['action'],
                            'confidence': signal.get('confidence', 50),
                            'entry_price': signal.get('entry_price', 1.0000),
                            'result': 'Breakeven',
                            'market_conditions': signal.get('market_conditions', {}),
                            'indicators': signal.get('indicators', {})
                        }
                        ml_generator.record_trade_outcome(trade_outcome)
                        st.success("Thanks for the feedback!")
                        st.rerun()
    else:
        st.info("No recent signals to provide feedback on. Start trading to see AI recommendations here!")
    
    st.markdown("---")
    
    # AI Learning Settings
    st.subheader("⚙️ Learning Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Learning Sensitivity:**")
        learning_sensitivity = st.radio(
            "How quickly should the AI adapt?",
            ["Conservative", "Moderate", "Aggressive"],
            index=1,
            help="Conservative: Slower learning, more stable. Aggressive: Faster learning, may be less stable"
        )
    
    with col2:
        st.write("**Reset Learning:**")
        st.warning("This will erase all learning progress!")
        if st.button("🔄 Reset AI Learning", help="Use only if AI performance becomes worse"):
            if st.session_state.get('confirm_reset'):
                ml_generator.adaptive_engine.reset_learning_system()
                st.success("AI learning system has been reset.")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.error("Click again to confirm reset.")

# Tab 6: Learning Resources  
with tab6:
    show_user_guide()

# Auto-refresh for live data
if st.sidebar.checkbox("🔄 Auto Update", value=False):
    time.sleep(30)  # Update every 30 seconds
    st.rerun()

# Add learning tips periodically
notifications.add_learning_tip()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
        🤖 Personal AI Forex Trading Assistant<br>
        Self-Learning AI that Gets Smarter with Every Decision<br>
        Designed to keep you safe while you learn to trade successfully
    </small>
</div>
""", unsafe_allow_html=True)