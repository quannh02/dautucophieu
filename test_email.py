#!/usr/bin/env python3
"""
Test Email Configuration Script
This script helps you test your email configuration for the crypto alert system.
"""

import sys
import os
from datetime import datetime
from alert_system import AlertSystem

def test_email_configuration():
    """Test email configuration by sending a test email"""
    print("🧪 Testing Email Configuration...")
    print("=" * 50)
    
    try:
        # Initialize alert system
        alert_system = AlertSystem()
        
        # Check if email alerts are enabled
        if not alert_system.enable_email_alerts:
            print("❌ Email alerts are disabled.")
            print("💡 To enable email alerts:")
            print("   1. Copy config.example to config.py")
            print("   2. Set ENABLE_EMAIL_ALERTS = True")
            print("   3. Configure your email settings")
            return False
        
        print(f"✅ Email alerts are enabled")
        print(f"📧 SMTP Server: {alert_system.email_smtp_server}:{alert_system.email_smtp_port}")
        print(f"👤 Sender: {alert_system.email_sender}")
        print(f"📬 Recipients: {', '.join(alert_system.email_recipients)}")
        print(f"🔒 TLS: {'Enabled' if alert_system.email_use_tls else 'Disabled'}")
        print()
        
        # Create a test alert
        test_alert = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': 'BTCUSDT',
            'signal': 'STRONG_LONG',
            'previous_signal': 'NEUTRAL',
            'strength': 85,
            'price': 45000.00,
            'entry_price': 45050.00,
            'stop_loss': 43500.00,
            'take_profit': 47000.00,
            'rsi': 35,
            'reasons': [
                'RSI indicates oversold condition',
                'MACD bullish crossover detected',
                'Price broke above resistance level',
                'Volume spike confirms breakout'
            ]
        }
        
        print("📤 Sending test email...")
        
        # Create email content
        subject, text_body, html_body = alert_system.create_email_content([test_alert])
        
        # Add test indicator to subject
        subject = "[TEST] " + subject
        
        # Send test email
        alert_system.send_email_notification(subject, text_body, html_body)
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your inbox at: {', '.join(alert_system.email_recipients)}")
        print()
        print("💡 If you don't receive the email, check:")
        print("   • Spam/junk folder")
        print("   • Email credentials are correct")
        print("   • SMTP server settings are correct")
        print("   • Firewall/antivirus isn't blocking the connection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing email configuration: {e}")
        print()
        print("🔧 Common issues and solutions:")
        print("   • Gmail: Use App Password instead of regular password")
        print("   • Outlook: Enable 'Less secure app access' or use App Password")
        print("   • Check SMTP server and port settings")
        print("   • Verify email addresses are correct")
        print("   • Ensure internet connection is stable")
        
        return False

def main():
    """Main function"""
    print("🚀 Crypto Trading Alert System - Email Test")
    print("=" * 50)
    print()
    
    # Check if config.py exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found!")
        print("💡 Please copy config.example to config.py and configure your settings:")
        print("   cp config.example config.py")
        print()
        return
    
    # Test email configuration
    success = test_email_configuration()
    
    print()
    if success:
        print("🎉 Email configuration test completed successfully!")
        print("🚀 You can now run the alert system with email notifications enabled.")
    else:
        print("⚠️  Email configuration test failed.")
        print("🔧 Please check your configuration and try again.")

if __name__ == "__main__":
    main() 