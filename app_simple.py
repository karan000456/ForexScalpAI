import streamlit as st
import pandas as pd
import numpy as np

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
if 'personal_settings' not in st.session_state:
    st.session_state.personal_settings = None

# Main title
st.title("🤖 Personal AI Forex Trading Assistant")
st.markdown("### Simple, Safe, and Smart Trading that Learns from Every Decision")

# Check if user needs initial setup
if not st.session_state.get('personal_settings'):
    st.warning("👋 Welcome! Let's set up your personal trading profile first.")
    
    with st.container():
        st.subheader("🎯 Personal Trading Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Basic Information")
            account_balance = st.number_input(
                "Your Trading Account Balance ($)",
                min_value=100.0,
                max_value=100000.0,
                value=1000.0,
                step=100.0
            )
            
            risk_level = st.selectbox(
                "How much risk per trade?",
                ["1% (Very Safe)", "2% (Safe)", "3% (Moderate)", "5% (Aggressive)"],
                index=1
            )
            
            experience = st.selectbox(
                "Your trading experience:",
                ["Complete Beginner", "Some Experience", "Experienced"],
                index=0
            )
        
        with col2:
            st.markdown("### Trading Preferences")
            preferred_pairs = st.multiselect(
                "Which currency pairs interest you?",
                ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"],
                default=["EUR/USD"]
            )
            
            trading_session = st.selectbox(
                "When do you usually trade?",
                ["London Session", "New York Session", "Asian Session", "All Sessions"],
                index=0
            )
        
        if st.button("💾 Save My Profile", type="primary"):
            # Extract numeric risk value
            risk_value = float(risk_level.split('%')[0])
            
            st.session_state.personal_settings = {
                'account_balance': account_balance,
                'risk_per_trade': risk_value,
                'experience_level': experience,
                'preferred_pairs': preferred_pairs,
                'trading_session': trading_session,
                'setup_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.success("Profile saved! Refreshing app...")
            st.rerun()
    
    st.stop()

# Main app content
settings = st.session_state.personal_settings

# Ensure settings is not None (should not happen due to stop() above, but for type safety)
if settings is None:
    st.error("Settings not found. Please refresh the page.")
    st.stop()

st.sidebar.header("⚙️ Your Trading Profile")
st.sidebar.write(f"**Account:** ${settings['account_balance']:,.2f}")
st.sidebar.write(f"**Risk Level:** {settings['risk_per_trade']}%")
st.sidebar.write(f"**Experience:** {settings['experience_level']}")

# Main content
st.subheader("🎯 Trading Dashboard")

selected_pair = st.selectbox("Select Currency Pair", settings['preferred_pairs'])

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### {selected_pair} Analysis")
    
    # Generate some demo data for now
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    prices = 1.0900 + np.cumsum(np.random.randn(100) * 0.0001)
    
    chart_data = pd.DataFrame({
        'Price': prices
    }, index=dates)
    
    st.line_chart(chart_data)
    
    # Demo signal
    st.info("🎯 **Demo Signal**: BUY EUR/USD - Trend looks strong!")

with col2:
    st.markdown("### 📊 Quick Stats")
    st.metric("Current Price", f"{prices[-1]:.4f}")
    st.metric("24h Change", "+0.0025 (+0.23%)")
    
    st.markdown("### 💡 Next Steps")
    st.write("1. Monitor the current trend")
    st.write("2. Wait for clear signals")
    st.write("3. Manage your risk carefully")

st.success("✅ Basic app is working! The full features will load once all modules are properly configured.")