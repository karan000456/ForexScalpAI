# Personal AI Forex Trading Assistant

## Overview

This is an enhanced Streamlit-based web application designed as a personal AI forex trading assistant specifically for beginners with little to no trading experience. The system provides simple, safe, and smart trading guidance through AI-powered signals, comprehensive risk management, and step-by-step learning features. The application combines technical analysis with machine learning models to generate beginner-friendly buy/sell/hold recommendations, while featuring automated notifications, personal trading journal, risk management tools, and a progressive learning system that adapts to the user's experience level.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- Built with Streamlit framework for beginner-friendly web interface
- Multi-tab application with Simple Trading, Advanced Charts, Trading Journal, Risk Manager, and Learning sections
- Progressive difficulty system that adapts interface complexity to user experience level
- Interactive charts using Plotly with both simple line charts and advanced technical analysis
- Session state management for personal settings, trading journal, notifications, and learning progress
- Cached resource initialization for performance optimization

**Data Processing Pipeline**
- Modular architecture with separate components for data fetching, technical analysis, and ML predictions
- ForexDataProvider class handles API communication with Alpha Vantage for live market data
- Fallback to demo data generation when API access is unavailable
- Rate limiting implementation to comply with API usage restrictions
- Support for multiple timeframes (1min, 5min, 15min, 30min, 60min) for different trading strategies

**Technical Analysis Engine**
- TechnicalIndicators class calculates standard forex indicators including SMA, EMA, RSI, MACD, Bollinger Bands, and Stochastic Oscillator
- Comprehensive indicator suite designed for scalping and short-term trading strategies
- Configurable periods and parameters for different market conditions
- Support for both trend-following and momentum-based indicators

**Machine Learning Signal Generation**
- MLSignalGenerator uses Random Forest classifier for signal prediction
- Feature engineering combines price action data with technical indicators
- Standardized feature scaling for improved model performance
- Multi-class classification (Buy/Sell/Hold) with balanced class weights
- Model confidence scoring and signal strength assessment

**Personal Trading Assistant Features**
- Beginner-friendly setup wizard for personal trading profile configuration
- Automated position sizing calculator based on account balance and risk tolerance
- Smart notifications system with signal alerts, risk warnings, and educational tips
- Progressive learning guidance with step-by-step beginner tutorials
- Personal trading journal with trade tracking and performance analytics
- Risk management dashboard with daily limits and safety controls

**Enhanced Utility Functions**
- Currency formatting based on pair types (JPY vs non-JPY pairs)
- Pip value calculations for different currency pairs and trade sizes
- Profit/loss calculation engine for trade performance tracking
- Risk management utilities for position sizing and stop-loss calculations
- Beginner-friendly explanations of market conditions and trading signals

## External Dependencies

**Data Providers**
- Alpha Vantage API for real-time forex market data
- Requires API key configuration via environment variables
- Supports major currency pairs with configurable intervals and data ranges

**Python Libraries**
- Streamlit for web application framework and user interface
- Pandas and NumPy for data manipulation and numerical computations
- Plotly for interactive charting and technical analysis visualization
- Scikit-learn for machine learning model implementation and preprocessing
- Requests library for HTTP API communication

**Machine Learning Stack**
- Random Forest classifier from scikit-learn for signal generation
- StandardScaler for feature normalization
- Train-test split functionality for model validation
- Support for model persistence and retraining capabilities