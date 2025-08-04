import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Personal AI Forex Trading Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.write("Step 1: Basic streamlit works")

try:
    import pandas as pd
    import numpy as np
    st.write("Step 2: Pandas and numpy imported")
except Exception as e:
    st.error(f"Error importing pandas/numpy: {e}")
    st.stop()

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    from plotly.subplots import make_subplots
    st.write("Step 3: Plotly imported")
except Exception as e:
    st.error(f"Error importing plotly: {e}")
    st.stop()

try:
    from forex_data import ForexDataProvider
    st.write("Step 4: ForexDataProvider imported")
except Exception as e:
    st.error(f"Error importing ForexDataProvider: {e}")
    st.stop()

try:
    from technical_indicators import TechnicalIndicators
    st.write("Step 5: TechnicalIndicators imported")
except Exception as e:
    st.error(f"Error importing TechnicalIndicators: {e}")
    st.stop()

try:
    from enhanced_ml_signals import EnhancedMLSignalGenerator
    st.write("Step 6: EnhancedMLSignalGenerator imported")
except Exception as e:
    st.error(f"Error importing EnhancedMLSignalGenerator: {e}")
    st.stop()

try:
    from enhanced_features import PersonalTradingAssistant
    st.write("Step 7: PersonalTradingAssistant imported")
except Exception as e:
    st.error(f"Error importing PersonalTradingAssistant: {e}")
    st.stop()

try:
    from notifications import TradingNotifications, BeginnerGuidance
    st.write("Step 8: Notifications imported")
except Exception as e:
    st.error(f"Error importing notifications: {e}")
    st.stop()

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

st.write("Step 9: Session state initialized")

# Initialize components
try:
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
    st.write("Step 10: Components initialized successfully")
except Exception as e:
    st.error(f"Error initializing components: {e}")
    st.stop()

st.success("All components loaded successfully! App should work.")

# Main title
st.title("🤖 Personal AI Forex Trading Assistant")
st.markdown("### Debug mode - All systems operational")