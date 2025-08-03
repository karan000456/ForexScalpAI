import streamlit as st

def show_user_guide():
    """Display comprehensive user guide for the forex trading application"""
    
    st.markdown("""
    # 📚 How to Use the AI Forex Trading Signals App
    
    Welcome to your AI-powered forex trading companion! This guide will help you understand how to use all the features effectively.
    
    ## 🚀 Getting Started
    
    ### 1. **Understanding the Dashboard**
    The main screen shows:
    - **Live price charts** with candlestick patterns
    - **Technical indicators** (RSI, MACD, Moving Averages)
    - **Current trading signal** with confidence level
    - **Market sentiment** analysis
    
    ### 2. **Reading the Charts**
    - **Green candles**: Price went up during that time period
    - **Red candles**: Price went down during that time period
    - **Lines on chart**: Moving averages that show price trends
    - **Signal markers**: Green triangles (buy) or red triangles (sell)
    
    ## ⚙️ Configuration Settings (Left Sidebar)
    
    ### **Currency Pair Selection**
    Choose which currency pair to analyze:
    - **EUR/USD**: Euro vs US Dollar (most popular)
    - **GBP/USD**: British Pound vs US Dollar
    - **USD/JPY**: US Dollar vs Japanese Yen
    - And more major pairs
    
    ### **Risk Management Settings**
    Set your trading safety rules:
    - **Risk per Trade**: How much of your account to risk (1-5%)
    - **Stop Loss**: How many pips you're willing to lose (5-50 pips)
    - **Take Profit**: Your profit target in pips (10-100 pips)
    
    ### **Signal Sensitivity**
    Choose how aggressive you want the signals:
    - **Conservative**: Only very strong signals (safer)
    - **Moderate**: Balanced approach (recommended)
    - **Aggressive**: More frequent signals (higher risk)
    
    ## 📊 Understanding Signals
    
    ### **Signal Types**
    - 🟢 **BUY**: Price likely to go up - consider buying
    - 🔴 **SELL**: Price likely to go down - consider selling
    - ⚪ **HOLD**: No clear direction - wait for better opportunity
    
    ### **Confidence Levels**
    - **70%+**: Very strong signal
    - **60-70%**: Good signal
    - **50-60%**: Weak signal (be cautious)
    
    ### **Trade Setup Information**
    When you get a BUY or SELL signal, you'll see:
    - **Entry Price**: Where to enter the trade
    - **Stop Loss**: Where to exit if trade goes wrong
    - **Take Profit**: Where to exit for profit
    - **Risk/Reward Ratio**: How much you can gain vs lose
    
    ## 📈 Market Sentiment Indicators
    
    ### **RSI (Relative Strength Index)**
    - **Overbought**: Price might fall soon
    - **Oversold**: Price might rise soon
    - **Neutral**: No extreme conditions
    
    ### **MACD**
    - **Bullish**: Upward momentum
    - **Bearish**: Downward momentum
    
    ### **Trend Analysis**
    - **Above SMA 20**: Price is in uptrend
    - **Below SMA 20**: Price is in downtrend
    
    ## 📝 Using Signal History
    
    ### **Logging Signals**
    - Click "Log BUY Signal" or "Log SELL Signal" to save promising setups
    - Track your signal accuracy over time
    - Review past signals to improve your trading
    
    ### **Performance Metrics**
    Monitor your signal statistics:
    - **Total Signals**: How many signals you've logged
    - **Buy/Sell Distribution**: Balance of signal types
    - **Average Confidence**: Quality of your signals
    
    ## ⚠️ Important Safety Guidelines
    
    ### **Risk Management Rules**
    1. **Never risk more than 2% per trade**
    2. **Always use stop losses**
    3. **Don't trade during low market activity**
    4. **Start with small position sizes**
    
    ### **When NOT to Trade**
    - Weekend (markets closed)
    - Low confidence signals (under 60%)
    - During major news events
    - When feeling emotional
    
    ### **Best Practices**
    - **Paper trade first**: Practice without real money
    - **Keep a trading journal**: Track all your trades
    - **Review your performance**: Learn from wins and losses
    - **Stay disciplined**: Follow your rules consistently
    
    ## 🔧 Advanced Features
    
    ### **Auto-Refresh**
    - Enable to automatically update charts
    - Choose refresh interval (5-30 seconds)
    - Useful for active monitoring
    
    ### **Multiple Timeframes**
    The app analyzes 5-minute data, which is ideal for:
    - **Scalping**: Quick trades (minutes to hours)
    - **Day trading**: Trades within the same day
    - **Short-term analysis**: Quick market moves
    
    ## 🆘 Troubleshooting
    
    ### **No Data Showing**
    - App uses demo data when API is not available
    - Charts will still show realistic price movements
    - All features work normally with demo data
    
    ### **Signals Not Updating**
    - Check if auto-refresh is enabled
    - Try refreshing the page
    - Ensure good internet connection
    
    ### **Low Confidence Signals**
    - Try different currency pairs
    - Adjust sensitivity settings
    - Wait for better market conditions
    
    ## 💡 Pro Tips
    
    ### **For Beginners**
    1. Start with **Conservative** sensitivity
    2. Focus on **EUR/USD** (most predictable)
    3. Use small risk percentages (1-2%)
    4. Practice reading the charts first
    
    ### **For Experienced Traders**
    1. Combine signals with your own analysis
    2. Use the app for confirmation
    3. Adjust settings based on market conditions
    4. Track performance and optimize
    
    ### **Scalping Strategy**
    1. Look for signals with 65%+ confidence
    2. Use tight stop losses (10-15 pips)
    3. Take quick profits (15-25 pips)
    4. Trade during high activity periods
    
    ## 📞 Remember
    
    - This tool provides **educational signals** only
    - Always do your own research
    - Never trade money you can't afford to lose
    - Consider consulting a financial advisor
    - Practice with demo accounts first
    
    ---
    
    **Happy Trading! 📈**
    
    *Remember: The best traders are disciplined, patient, and always learning.*
    """)

    # Quick reference section
    with st.expander("🔍 Quick Reference Card"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Signal Colors**
            - 🟢 Green = BUY
            - 🔴 Red = SELL  
            - ⚪ White = HOLD
            
            **Confidence Levels**
            - 70%+ = Strong
            - 60-70% = Good
            - 50-60% = Weak
            """)
        
        with col2:
            st.markdown("""
            **Risk Management**
            - Max 2% per trade
            - Always use stop loss
            - 1:2 risk/reward minimum
            
            **Best Times to Trade**
            - London session (7-16 UTC)
            - New York session (12-21 UTC)
            - Avoid weekends
            """)

    # FAQ section
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: Is this real-time data?**
        A: The app can use real forex data with an API key, or realistic demo data for learning.
        
        **Q: How accurate are the signals?**
        A: Signal accuracy varies. Higher confidence signals tend to be more reliable, but no system is 100% accurate.
        
        **Q: Can I use this for live trading?**
        A: This is an educational tool. Always practice with demo accounts first and do your own analysis.
        
        **Q: What's the best currency pair for beginners?**
        A: EUR/USD is recommended as it's the most liquid and predictable major pair.
        
        **Q: How often should I check for signals?**
        A: For scalping, check every 5-15 minutes during active trading hours.
        
        **Q: What if I get conflicting signals?**
        A: When signals conflict, it's often best to wait for clearer market direction.
        """)