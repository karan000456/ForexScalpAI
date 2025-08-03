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
from ml_signals import MLSignalGenerator
from utils import format_currency, calculate_profit_loss
from user_guide import show_user_guide
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="AI Forex Trading Signals",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'signal_history' not in st.session_state:
    st.session_state.signal_history = []
if 'trades' not in st.session_state:
    st.session_state.trades = []

# Initialize components
@st.cache_resource
def initialize_components():
    forex_data = ForexDataProvider()
    tech_indicators = TechnicalIndicators()
    ml_generator = MLSignalGenerator()
    return forex_data, tech_indicators, ml_generator

forex_data, tech_indicators, ml_generator = initialize_components()

# Main title and navigation
st.title("🤖 AI-Powered Forex Trading Signals")
st.markdown("### Real-time Scalping Signals for Major Currency Pairs")

# Add navigation tabs
tab1, tab2 = st.tabs(["📊 Trading Dashboard", "📚 User Guide"])

with tab2:
    show_user_guide()

with tab1:
    # Risk disclaimer
    with st.expander("⚠️ IMPORTANT TRADING DISCLAIMER - READ BEFORE USE"):
        st.error("""
        **HIGH RISK WARNING**: Trading foreign exchange on margin carries a high level of risk and may not be suitable for all investors. 
        Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. 
        Before deciding to trade foreign exchange you should carefully consider your investment objectives, level of experience, and risk appetite.
        
        This tool provides educational signals based on technical analysis and should not be considered as financial advice. 
        Always do your own research and consider consulting with a qualified financial advisor.
        """)

# Sidebar configuration (outside of tabs since sidebar is global)
st.sidebar.header("⚙️ Trading Configuration")

# Currency pair selection
currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
selected_pair = st.sidebar.selectbox("Select Currency Pair", currency_pairs, index=0)

# Risk management settings
st.sidebar.subheader("Risk Management")
risk_percentage = st.sidebar.slider("Risk per Trade (%)", 1.0, 5.0, 2.0, 0.1)
stop_loss_pips = st.sidebar.number_input("Stop Loss (pips)", min_value=5, max_value=50, value=15)
take_profit_pips = st.sidebar.number_input("Take Profit (pips)", min_value=10, max_value=100, value=30)

# Signal sensitivity
st.sidebar.subheader("Signal Settings")
signal_sensitivity = st.sidebar.select_slider(
    "Signal Sensitivity",
    options=["Conservative", "Moderate", "Aggressive"],
    value="Moderate"
)

# Auto-refresh settings
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)
refresh_interval = st.sidebar.selectbox("Refresh Interval", [5, 10, 15, 30], index=1)

with tab1:
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 {selected_pair} Live Analysis")
        
        # Get live data
        try:
            price_data = forex_data.get_live_data(selected_pair)
            
            if price_data is not None and not price_data.empty:
                # Calculate technical indicators
                indicators = tech_indicators.calculate_all_indicators(price_data)
                
                # Generate ML signals
                current_signal = ml_generator.generate_signal(price_data, indicators, signal_sensitivity)
                
                # Create the main chart
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    subplot_titles=('Price & Moving Averages', 'RSI', 'MACD'),
                    row_heights=[0.6, 0.2, 0.2]
                )
            
            # Price chart with moving averages
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
            
            # Moving averages
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=indicators['sma_20'],
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=indicators['ema_12'],
                    name='EMA 12',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
            
            # RSI
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=indicators['rsi'],
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=2, col=1
            )
            
            # RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # MACD
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=indicators['macd'],
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=indicators['macd_signal'],
                    name='MACD Signal',
                    line=dict(color='red')
                ),
                row=3, col=1
            )
            
            # Add signal markers
            if current_signal['action'] != 'HOLD':
                signal_color = 'green' if current_signal['action'] == 'BUY' else 'red'
                signal_symbol = 'triangle-up' if current_signal['action'] == 'BUY' else 'triangle-down'
                
                fig.add_trace(
                    go.Scatter(
                        x=[price_data.index[-1]],
                        y=[price_data['close'].iloc[-1]],
                        mode='markers',
                        marker=dict(
                            symbol=signal_symbol,
                            size=15,
                            color=signal_color
                        ),
                        name=f'{current_signal["action"]} Signal',
                        showlegend=True
                    ),
                    row=1, col=1
                )
            
            fig.update_layout(
                height=800,
                title=f"{selected_pair} - Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}",
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Unable to fetch live forex data. Please check your API configuration.")
            st.info("Make sure your Alpha Vantage API key is set in the environment variables as 'ALPHA_VANTAGE_API_KEY'")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("This might be due to API rate limits or connectivity issues. Please try again in a moment.")

with col2:
    st.subheader("🎯 Current Signal")
    
    try:
        if 'current_signal' in locals() and current_signal:
            # Signal display
            if current_signal['action'] == 'BUY':
                st.success(f"🟢 **BUY SIGNAL**")
                st.metric("Confidence", f"{current_signal['confidence']:.1f}%")
            elif current_signal['action'] == 'SELL':
                st.error(f"🔴 **SELL SIGNAL**")
                st.metric("Confidence", f"{current_signal['confidence']:.1f}%")
            else:
                st.info("⚪ **HOLD** - No clear signal")
                st.metric("Confidence", f"{current_signal['confidence']:.1f}%")
            
            # Current market data
            if 'price_data' in locals() and price_data is not None and not price_data.empty:
                current_price = price_data['close'].iloc[-1]
                price_change = price_data['close'].iloc[-1] - price_data['close'].iloc[-2] if len(price_data) > 1 else 0
                
                st.metric(
                    "Current Price",
                    format_currency(current_price, selected_pair),
                    delta=f"{price_change:+.5f}"
                )
                
                # Entry suggestions
                if current_signal['action'] != 'HOLD':
                    st.subheader("📍 Trade Setup")
                    entry_price = current_price
                    
                    if current_signal['action'] == 'BUY':
                        stop_loss = entry_price - (stop_loss_pips * 0.0001)
                        take_profit = entry_price + (take_profit_pips * 0.0001)
                    else:
                        stop_loss = entry_price + (stop_loss_pips * 0.0001)
                        take_profit = entry_price - (take_profit_pips * 0.0001)
                    
                    st.write(f"**Entry:** {format_currency(entry_price, selected_pair)}")
                    st.write(f"**Stop Loss:** {format_currency(stop_loss, selected_pair)}")
                    st.write(f"**Take Profit:** {format_currency(take_profit, selected_pair)}")
                    
                    # Risk/Reward ratio
                    risk_reward = take_profit_pips / stop_loss_pips
                    st.write(f"**Risk/Reward:** 1:{risk_reward:.1f}")
                    
                    # Store signal in history
                    signal_data = {
                        'timestamp': datetime.datetime.now(),
                        'pair': selected_pair,
                        'action': current_signal['action'],
                        'confidence': current_signal['confidence'],
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit
                    }
                    
                    if st.button(f"📝 Log {current_signal['action']} Signal"):
                        st.session_state.signal_history.append(signal_data)
                        st.success("Signal logged!")
                        time.sleep(1)
                        st.rerun()
    
    except Exception as e:
        st.error(f"Error generating signals: {str(e)}")
    
    # Market sentiment indicators
    st.subheader("📊 Market Sentiment")
    
    try:
        if 'indicators' in locals():
            # RSI interpretation
            rsi_value = indicators['rsi'].iloc[-1]
            if rsi_value > 70:
                st.write("🔴 **RSI:** Overbought")
            elif rsi_value < 30:
                st.write("🟢 **RSI:** Oversold")
            else:
                st.write("🟡 **RSI:** Neutral")
            
            # MACD interpretation
            macd_value = indicators['macd'].iloc[-1]
            macd_signal_value = indicators['macd_signal'].iloc[-1]
            
            if macd_value > macd_signal_value:
                st.write("🟢 **MACD:** Bullish")
            else:
                st.write("🔴 **MACD:** Bearish")
            
            # Moving average trend
            sma_20 = indicators['sma_20'].iloc[-1]
            current_price = price_data['close'].iloc[-1] if 'price_data' in locals() and price_data is not None else 0
            
            if current_price > sma_20:
                st.write("🟢 **Trend:** Above SMA 20")
            else:
                st.write("🔴 **Trend:** Below SMA 20")
    
    except Exception as e:
        st.write("Market sentiment data unavailable")

# Signal History section
st.subheader("📈 Signal History & Performance")

if st.session_state.signal_history:
    history_df = pd.DataFrame(st.session_state.signal_history)
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_signals = len(history_df)
        st.metric("Total Signals", total_signals)
    
    with col2:
        buy_signals = len(history_df[history_df['action'] == 'BUY'])
        st.metric("Buy Signals", buy_signals)
    
    with col3:
        sell_signals = len(history_df[history_df['action'] == 'SELL'])
        st.metric("Sell Signals", sell_signals)
    
    with col4:
        avg_confidence = history_df['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    
    # Recent signals table
    st.subheader("Recent Signals")
    display_df = history_df.copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df = display_df.sort_values('timestamp', ascending=False).head(10)
    
    st.dataframe(
        display_df[['timestamp', 'pair', 'action', 'confidence', 'entry_price']],
        use_container_width=True
    )
    
    # Clear history button
    if st.button("🗑️ Clear Signal History"):
        st.session_state.signal_history = []
        st.rerun()

else:
    st.info("No signals logged yet. Start trading to see your signal history here.")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
        🤖 AI Forex Trading Signals | Built with Streamlit<br>
        Remember: Past performance is not indicative of future results. Trade responsibly.
    </small>
</div>
""", unsafe_allow_html=True)
