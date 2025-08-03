# AI Forex Trading Signals

## Overview

This is a Streamlit-based web application that provides AI-powered forex trading signals for major currency pairs. The system combines technical analysis indicators with machine learning models to generate real-time buy/sell/hold signals for scalping strategies. The application fetches live forex data from Alpha Vantage API, processes it through various technical indicators, and uses a Random Forest classifier to predict trading signals. It includes comprehensive risk management features, profit/loss calculations, and an interactive dashboard for traders to monitor market conditions and trading opportunities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- Built with Streamlit framework for web-based dashboard interface
- Single-page application with expandable sections and real-time updates
- Interactive charts using Plotly for technical analysis visualization
- Session state management for maintaining signal history and trade tracking
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

**Utility Functions**
- Currency formatting based on pair types (JPY vs non-JPY pairs)
- Pip value calculations for different currency pairs and trade sizes
- Profit/loss calculation engine for trade performance tracking
- Risk management utilities for position sizing and stop-loss calculations

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