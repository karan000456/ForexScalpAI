import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

def format_currency(value: float, currency_pair: str) -> str:
    """
    Format currency value based on the currency pair
    
    Args:
        value: Currency value to format
        currency_pair: Currency pair (e.g., 'EUR/USD')
    
    Returns:
        Formatted currency string
    """
    # JPY pairs typically have 3 decimal places, others have 5
    jpy_pairs = ['USD/JPY', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'NZD/JPY']
    
    if currency_pair in jpy_pairs:
        return f"{value:.3f}"
    else:
        return f"{value:.5f}"

def calculate_pip_value(currency_pair: str, trade_size: float = 10000) -> float:
    """
    Calculate pip value for a given currency pair
    
    Args:
        currency_pair: Currency pair (e.g., 'EUR/USD')
        trade_size: Trade size in base currency units
    
    Returns:
        Pip value in account currency
    """
    # Simplified pip value calculation (assuming USD account)
    jpy_pairs = ['USD/JPY', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'NZD/JPY']
    
    if currency_pair in jpy_pairs:
        # For JPY pairs, 1 pip = 0.01
        return (0.01 / 100) * trade_size
    else:
        # For other pairs, 1 pip = 0.0001
        return (0.0001 / 1) * trade_size

def calculate_profit_loss(entry_price: float, exit_price: float, trade_type: str, 
                         trade_size: float, currency_pair: str) -> Dict[str, float]:
    """
    Calculate profit/loss for a trade
    
    Args:
        entry_price: Entry price
        exit_price: Exit price  
        trade_type: 'BUY' or 'SELL'
        trade_size: Trade size in lots
        currency_pair: Currency pair
    
    Returns:
        Dict containing profit/loss information
    """
    # Calculate pip difference
    jpy_pairs = ['USD/JPY', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'NZD/JPY']
    pip_multiplier = 100 if currency_pair in jpy_pairs else 10000
    
    if trade_type == 'BUY':
        pip_difference = (exit_price - entry_price) * pip_multiplier
    else:  # SELL
        pip_difference = (entry_price - exit_price) * pip_multiplier
    
    # Calculate monetary profit/loss
    pip_value = calculate_pip_value(currency_pair, trade_size * 10000)  # Convert lots to units
    profit_loss = pip_difference * pip_value
    
    return {
        'pip_difference': pip_difference,
        'profit_loss_usd': profit_loss,
        'profit_loss_percentage': (profit_loss / (entry_price * trade_size * 10000)) * 100
    }

def calculate_position_size(account_balance: float, risk_percentage: float, 
                           stop_loss_pips: int, currency_pair: str) -> float:
    """
    Calculate position size based on risk management rules
    
    Args:
        account_balance: Account balance in USD
        risk_percentage: Risk percentage per trade
        stop_loss_pips: Stop loss in pips
        currency_pair: Currency pair
    
    Returns:
        Position size in lots
    """
    risk_amount = account_balance * (risk_percentage / 100)
    pip_value = calculate_pip_value(currency_pair, 10000)  # Standard lot pip value
    
    position_size = risk_amount / (stop_loss_pips * pip_value)
    
    # Round to 2 decimal places (mini lots)
    return round(position_size, 2)

def analyze_signal_performance(signal_history: List[Dict]) -> Dict[str, Any]:
    """
    Analyze performance of historical signals
    
    Args:
        signal_history: List of signal dictionaries
    
    Returns:
        Dict containing performance metrics
    """
    if not signal_history:
        return {
            'total_signals': 0,
            'win_rate': 0,
            'avg_confidence': 0,
            'signal_distribution': {}
        }
    
    df = pd.DataFrame(signal_history)
    
    total_signals = len(df)
    
    # Signal distribution
    signal_counts = df['action'].value_counts().to_dict()
    
    # Average confidence
    avg_confidence = df['confidence'].mean()
    
    # Win rate (placeholder - would need actual trade outcomes)
    # For now, using confidence as a proxy
    high_confidence_signals = df[df['confidence'] > 70]
    win_rate = len(high_confidence_signals) / total_signals * 100 if total_signals > 0 else 0
    
    return {
        'total_signals': total_signals,
        'win_rate': win_rate,
        'avg_confidence': avg_confidence,
        'signal_distribution': signal_counts,
        'signals_by_pair': df.groupby('pair')['action'].count().to_dict(),
        'avg_confidence_by_action': df.groupby('action')['confidence'].mean().to_dict()
    }

def validate_trading_hours(currency_pair: str) -> Dict[str, Any]:
    """
    Check if current time is within major trading hours for the currency pair
    
    Args:
        currency_pair: Currency pair to check
    
    Returns:
        Dict containing trading session information
    """
    now = datetime.now()
    current_hour = now.hour
    
    # Major trading sessions (UTC)
    sessions = {
        'Sydney': {'start': 21, 'end': 6},
        'Tokyo': {'start': 23, 'end': 8},
        'London': {'start': 7, 'end': 16},
        'New York': {'start': 12, 'end': 21}
    }
    
    active_sessions = []
    for session, hours in sessions.items():
        if hours['start'] > hours['end']:  # Crosses midnight
            if current_hour >= hours['start'] or current_hour <= hours['end']:
                active_sessions.append(session)
        else:
            if hours['start'] <= current_hour <= hours['end']:
                active_sessions.append(session)
    
    # Determine market activity level
    if len(active_sessions) >= 2:
        activity_level = 'High'
    elif len(active_sessions) == 1:
        activity_level = 'Medium'
    else:
        activity_level = 'Low'
    
    return {
        'active_sessions': active_sessions,
        'activity_level': activity_level,
        'is_weekend': now.weekday() >= 5,
        'recommended_trading': activity_level in ['High', 'Medium'] and now.weekday() < 5
    }

def calculate_drawdown(price_series: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown for a price series
    
    Args:
        price_series: Series of prices or equity curve
    
    Returns:
        Dict containing drawdown statistics
    """
    # Calculate running maximum
    running_max = price_series.expanding().max()
    
    # Calculate drawdown
    drawdown = (price_series - running_max) / running_max
    
    # Find maximum drawdown
    max_drawdown = drawdown.min()
    
    # Find drawdown duration
    drawdown_duration = 0
    current_duration = 0
    max_duration = 0
    
    for dd in drawdown:
        if dd < 0:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0
    
    return {
        'max_drawdown': abs(max_drawdown) * 100,  # Convert to percentage
        'max_drawdown_duration': max_duration,
        'current_drawdown': abs(drawdown.iloc[-1]) * 100 if len(drawdown) > 0 else 0
    }

def generate_risk_warnings(current_signal: Dict, market_conditions: Dict) -> List[str]:
    """
    Generate risk warnings based on current signal and market conditions
    
    Args:
        current_signal: Current trading signal
        market_conditions: Current market conditions
    
    Returns:
        List of risk warning messages
    """
    warnings = []
    
    # Low confidence warning
    if current_signal.get('confidence', 0) < 60:
        warnings.append("⚠️ Low confidence signal - consider waiting for better setup")
    
    # Weekend warning
    if market_conditions.get('is_weekend', False):
        warnings.append("🕒 Weekend trading - markets are closed, signals may be unreliable")
    
    # Low activity warning
    if market_conditions.get('activity_level') == 'Low':
        warnings.append("📉 Low market activity - reduced liquidity may affect execution")
    
    # High volatility warning (placeholder)
    # In real implementation, you'd check actual volatility metrics
    
    return warnings

class TradingJournal:
    """
    Simple trading journal to track trades and performance
    """
    
    def __init__(self):
        self.trades = []
    
    def add_trade(self, trade_data: Dict):
        """Add a new trade to the journal"""
        trade_data['timestamp'] = datetime.now()
        self.trades.append(trade_data)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics"""
        if not self.trades:
            return {}
        
        df = pd.DataFrame(self.trades)
        
        # Basic stats
        total_trades = len(df)
        winning_trades = len(df[df['profit_loss'] > 0]) if 'profit_loss' in df.columns else 0
        losing_trades = len(df[df['profit_loss'] < 0]) if 'profit_loss' in df.columns else 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit/Loss stats
        total_pnl = df['profit_loss'].sum() if 'profit_loss' in df.columns else 0
        avg_win = df[df['profit_loss'] > 0]['profit_loss'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['profit_loss'] < 0]['profit_loss'].mean() if losing_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
    
    def export_to_csv(self, filename: str):
        """Export trades to CSV file"""
        if self.trades:
            df = pd.DataFrame(self.trades)
            df.to_csv(filename, index=False)
            return True
        return False
