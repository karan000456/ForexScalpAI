import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import time

class TradingNotifications:
    """
    Simple notification system for personal trading
    """
    
    def __init__(self):
        self.initialize_notifications()
    
    def initialize_notifications(self):
        """Initialize notification system"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'signal_alerts': True,
                'risk_warnings': True,
                'market_updates': True,
                'learning_tips': True,
                'min_confidence': 65
            }
    
    def add_notification(self, message: str, notification_type: str = "info", priority: str = "normal"):
        """Add a new notification"""
        notification = {
            'id': len(st.session_state.notifications) + 1,
            'timestamp': datetime.now(),
            'message': message,
            'type': notification_type,  # info, success, warning, error
            'priority': priority,  # low, normal, high
            'read': False
        }
        
        st.session_state.notifications.append(notification)
        
        # Keep only last 50 notifications
        if len(st.session_state.notifications) > 50:
            st.session_state.notifications = st.session_state.notifications[-50:]
    
    def check_signal_notifications(self, signal: Dict, pair: str):
        """Check if signal triggers any notifications"""
        settings = st.session_state.notification_settings
        
        if not settings['signal_alerts']:
            return
        
        confidence = signal.get('confidence', 0)
        action = signal.get('action', 'HOLD')
        
        # High confidence signal
        if confidence >= 80 and action != 'HOLD':
            self.add_notification(
                f"🎯 Strong {action} signal for {pair} ({confidence:.0f}% confidence)",
                "success",
                "high"
            )
        
        # Medium confidence signal
        elif confidence >= settings['min_confidence'] and action != 'HOLD':
            self.add_notification(
                f"📊 {action} signal for {pair} ({confidence:.0f}% confidence)",
                "info",
                "normal"
            )
        
        # Low confidence warning
        elif confidence < 50 and action != 'HOLD':
            self.add_notification(
                f"⚠️ Weak {action} signal for {pair} ({confidence:.0f}% confidence) - Be cautious",
                "warning",
                "normal"
            )
    
    def check_risk_notifications(self, position_size: Dict, settings: Dict):
        """Check for risk-related notifications"""
        if not st.session_state.notification_settings['risk_warnings']:
            return
        
        risk_amount = position_size.get('risk_amount', 0)
        account_balance = settings.get('account_balance', 1000)
        risk_pct = settings.get('risk_per_trade', 2)
        
        # High risk warning
        if risk_pct > 3:
            self.add_notification(
                f"🚨 High risk level: {risk_pct}% per trade. Consider reducing to 2% or less",
                "error",
                "high"
            )
        
        # Account balance warning
        if account_balance < 500:
            self.add_notification(
                "⚠️ Low account balance. Consider paper trading or reducing position sizes",
                "warning",
                "normal"
            )
    
    def check_market_notifications(self, indicators: Dict, pair: str):
        """Check for market condition notifications"""
        if not st.session_state.notification_settings['market_updates']:
            return
        
        try:
            # RSI extreme conditions
            if 'rsi' in indicators and not indicators['rsi'].empty:
                rsi_value = indicators['rsi'].iloc[-1]
                
                if rsi_value > 85:
                    self.add_notification(
                        f"📈 {pair} severely overbought (RSI: {rsi_value:.0f}) - Potential reversal coming",
                        "warning",
                        "normal"
                    )
                elif rsi_value < 15:
                    self.add_notification(
                        f"📉 {pair} severely oversold (RSI: {rsi_value:.0f}) - Potential bounce coming",
                        "info",
                        "normal"
                    )
            
            # Volatility warnings
            if 'atr' in indicators and not indicators['atr'].empty:
                current_atr = indicators['atr'].iloc[-1]
                avg_atr = indicators['atr'].tail(20).mean()
                
                if current_atr > avg_atr * 1.5:
                    self.add_notification(
                        f"⚡ High volatility detected in {pair} - Use smaller position sizes",
                        "warning",
                        "normal"
                    )
        
        except Exception as e:
            pass  # Silently handle any indicator calculation errors
    
    def add_learning_tip(self):
        """Add educational tips for beginners"""
        if not st.session_state.notification_settings['learning_tips']:
            return
        
        tips = [
            "💡 Tip: Always use stop losses to protect your capital",
            "📚 Tip: Start with paper trading before using real money",
            "🎯 Tip: Focus on one currency pair until you master it",
            "⏰ Tip: Best trading times are during London and New York sessions",
            "💪 Tip: Successful trading requires patience and discipline",
            "📊 Tip: Never risk more than 2% of your account on a single trade",
            "🧠 Tip: Keep a trading journal to track your progress",
            "🔄 Tip: Review your trades weekly to identify patterns"
        ]
        
        # Add a random tip every hour
        last_tip_time = getattr(self, 'last_tip_time', None)
        current_time = datetime.now()
        
        if last_tip_time is None or (current_time - last_tip_time).seconds > 3600:
            import random
            tip = random.choice(tips)
            self.add_notification(tip, "info", "low")
            self.last_tip_time = current_time
    
    def show_notifications(self):
        """Display notifications in the UI"""
        unread_notifications = [n for n in st.session_state.notifications if not n['read']]
        
        if not unread_notifications:
            return
        
        st.subheader(f"🔔 Notifications ({len(unread_notifications)} new)")
        
        # Show latest 5 notifications
        for notification in reversed(unread_notifications[-5:]):
            time_str = notification['timestamp'].strftime("%H:%M")
            
            col1, col2 = st.columns([1, 0.1])
            
            with col1:
                if notification['type'] == 'success':
                    st.success(f"**{time_str}** - {notification['message']}")
                elif notification['type'] == 'warning':
                    st.warning(f"**{time_str}** - {notification['message']}")
                elif notification['type'] == 'error':
                    st.error(f"**{time_str}** - {notification['message']}")
                else:
                    st.info(f"**{time_str}** - {notification['message']}")
            
            with col2:
                if st.button("✓", key=f"mark_read_{notification['id']}", help="Mark as read"):
                    notification['read'] = True
                    st.rerun()
        
        # Mark all as read button
        if len(unread_notifications) > 1:
            if st.button("✓ Mark All Read"):
                for notification in st.session_state.notifications:
                    notification['read'] = True
                st.rerun()
    
    def show_notification_settings(self):
        """Show notification preferences"""
        st.subheader("🔔 Notification Settings")
        
        settings = st.session_state.notification_settings
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Alert Types**")
            
            signal_alerts = st.checkbox(
                "Trading Signal Alerts",
                value=settings['signal_alerts'],
                help="Get notified when trading signals appear"
            )
            
            risk_warnings = st.checkbox(
                "Risk Management Warnings",
                value=settings['risk_warnings'],
                help="Get warnings about high risk trades"
            )
        
        with col2:
            st.write("**Educational Content**")
            
            market_updates = st.checkbox(
                "Market Condition Updates",
                value=settings['market_updates'],
                help="Get notified about important market conditions"
            )
            
            learning_tips = st.checkbox(
                "Learning Tips",
                value=settings['learning_tips'],
                help="Receive educational trading tips"
            )
        
        # Signal threshold
        min_confidence = st.slider(
            "Minimum Signal Confidence for Alerts (%)",
            min_value=50,
            max_value=90,
            value=settings['min_confidence'],
            help="Only get alerts for signals above this confidence level"
        )
        
        if st.button("💾 Save Notification Settings"):
            st.session_state.notification_settings.update({
                'signal_alerts': signal_alerts,
                'risk_warnings': risk_warnings,
                'market_updates': market_updates,
                'learning_tips': learning_tips,
                'min_confidence': min_confidence
            })
            st.success("Notification settings saved!")
            st.rerun()
    
    def get_notification_summary(self):
        """Get summary of recent notifications"""
        recent_notifications = [
            n for n in st.session_state.notifications 
            if (datetime.now() - n['timestamp']).days < 1
        ]
        
        return {
            'total_today': len(recent_notifications),
            'unread': len([n for n in recent_notifications if not n['read']]),
            'high_priority': len([n for n in recent_notifications if n['priority'] == 'high']),
            'alerts': len([n for n in recent_notifications if n['type'] in ['warning', 'error']])
        }

class BeginnerGuidance:
    """
    Provides step-by-step guidance for complete beginners
    """
    
    def __init__(self):
        self.initialize_guidance()
    
    def initialize_guidance(self):
        """Initialize guidance system"""
        if 'guidance_progress' not in st.session_state:
            st.session_state.guidance_progress = {
                'current_step': 1,
                'completed_steps': [],
                'show_guidance': True
            }
    
    def show_beginner_guidance(self):
        """Show step-by-step guidance for beginners"""
        if not st.session_state.guidance_progress['show_guidance']:
            return
        
        progress = st.session_state.guidance_progress
        current_step = progress['current_step']
        
        st.subheader("🎓 Beginner's Trading Guide")
        
        # Progress bar
        total_steps = 6
        progress_pct = len(progress['completed_steps']) / total_steps
        st.progress(progress_pct)
        st.write(f"Progress: {len(progress['completed_steps'])}/{total_steps} steps completed")
        
        # Current step guidance
        if current_step == 1:
            self.show_step_1()
        elif current_step == 2:
            self.show_step_2()
        elif current_step == 3:
            self.show_step_3()
        elif current_step == 4:
            self.show_step_4()
        elif current_step == 5:
            self.show_step_5()
        elif current_step == 6:
            self.show_step_6()
        else:
            self.show_completion()
    
    def show_step_1(self):
        """Step 1: Setup personal information"""
        st.info("**Step 1: Set up your personal trading profile**")
        st.write("Before you start trading, I need to know about your situation to give you the best advice.")
        
        if st.button("✅ I've set up my profile", key="step1"):
            self.complete_step(1)
    
    def show_step_2(self):
        """Step 2: Understand the dashboard"""
        st.info("**Step 2: Learn to read the trading dashboard**")
        st.write("The main screen shows charts and signals. Green means 'buy opportunity', red means 'sell opportunity', and white means 'wait'.")
        
        if st.button("✅ I understand the dashboard", key="step2"):
            self.complete_step(2)
    
    def show_step_3(self):
        """Step 3: Practice with demo mode"""
        st.info("**Step 3: Practice without real money**")
        st.write("Before using real money, practice by writing down trades you would make. Track if they would be profitable.")
        
        if st.button("✅ I've practiced with paper trading", key="step3"):
            self.complete_step(3)
    
    def show_step_4(self):
        """Step 4: Learn risk management"""
        st.info("**Step 4: Master risk management**")
        st.write("Never risk more than 2% of your account on any single trade. This is the most important rule in trading.")
        
        if st.button("✅ I understand risk management", key="step4"):
            self.complete_step(4)
    
    def show_step_5(self):
        """Step 5: Start with small trades"""
        st.info("**Step 5: Make your first small trades**")
        st.write("When you're ready for real money, start with the smallest position sizes possible. Focus on learning, not profits.")
        
        if st.button("✅ I've made my first trades", key="step5"):
            self.complete_step(5)
    
    def show_step_6(self):
        """Step 6: Build consistency"""
        st.info("**Step 6: Develop consistent habits**")
        st.write("Keep a trading journal, review your performance weekly, and always follow your risk management rules.")
        
        if st.button("✅ I'm trading consistently", key="step6"):
            self.complete_step(6)
    
    def show_completion(self):
        """Show completion message"""
        st.success("🎉 **Congratulations! You've completed the beginner's guide!**")
        st.write("You now have the foundation for successful trading. Remember: patience and discipline are key.")
        
        if st.button("🎓 Graduate to Advanced Mode"):
            st.session_state.guidance_progress['show_guidance'] = False
            st.rerun()
    
    def complete_step(self, step_number):
        """Mark a step as completed"""
        progress = st.session_state.guidance_progress
        
        if step_number not in progress['completed_steps']:
            progress['completed_steps'].append(step_number)
        
        progress['current_step'] = step_number + 1
        st.rerun()
    
    def reset_guidance(self):
        """Reset guidance progress"""
        st.session_state.guidance_progress = {
            'current_step': 1,
            'completed_steps': [],
            'show_guidance': True
        }