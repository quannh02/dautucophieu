import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from colorama import Fore, Back, Style, init
from plyer import notification
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from crypto_analyzer import CryptoAnalyzer

# Initialize colorama for colored console output
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSystem:
    """
    Real-time alert system for cryptocurrency trading signals
    """
    
    def __init__(self, check_interval: int = 60, max_duration: int = None):
        self.analyzer = CryptoAnalyzer()
        self.check_interval = check_interval  # seconds
        self.max_duration = max_duration  # seconds (None = run indefinitely)
        self.running = False
        self.start_time = None
        self.previous_signals = {}
        self.alert_history = []
        self.alert_history_file = "alert_history.json"
        
        # Load configuration
        self.load_config()
        
        # Load previous alert history
        self.load_alert_history()
        
    def load_config(self):
        """Load configuration settings"""
        try:
            # Try to import from config.py
            import config
            self.enable_email_alerts = getattr(config, 'ENABLE_EMAIL_ALERTS', False)
            self.email_smtp_server = getattr(config, 'EMAIL_SMTP_SERVER', 'smtp.gmail.com')
            self.email_smtp_port = getattr(config, 'EMAIL_SMTP_PORT', 587)
            self.email_sender = getattr(config, 'EMAIL_SENDER', '')
            self.email_password = getattr(config, 'EMAIL_PASSWORD', '')
            self.email_recipients = getattr(config, 'EMAIL_RECIPIENTS', [])
            self.email_use_tls = getattr(config, 'EMAIL_USE_TLS', True)
            
            # Desktop notification settings
            self.enable_desktop_notifications = getattr(config, 'ENABLE_DESKTOP_NOTIFICATIONS', True)
            
            # Validate email addresses if email alerts are enabled
            if self.enable_email_alerts:
                self.validate_email_config()
                
        except ImportError:
            logger.warning("config.py not found. Email alerts will be disabled. Copy config.example to config.py and configure email settings.")
            self.enable_email_alerts = False
            self.enable_desktop_notifications = True  # Default to enabled
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.enable_email_alerts = False
            self.enable_desktop_notifications = True  # Default to enabled
    
    def validate_email_config(self):
        """Validate email configuration"""
        if not self.email_sender:
            raise ValueError("EMAIL_SENDER is required for email alerts")
        if not self.email_password:
            raise ValueError("EMAIL_PASSWORD is required for email alerts")
        if not self.email_recipients:
            raise ValueError("EMAIL_RECIPIENTS list cannot be empty for email alerts")
        
        # Validate sender email
        try:
            validate_email(self.email_sender)
        except EmailNotValidError:
            raise ValueError(f"Invalid sender email address: {self.email_sender}")
        
        # Validate recipient emails
        for recipient in self.email_recipients:
            try:
                validate_email(recipient)
            except EmailNotValidError:
                raise ValueError(f"Invalid recipient email address: {recipient}")
        
        logger.info(f"Email configuration validated. Alerts will be sent to {len(self.email_recipients)} recipient(s)")
        
    def load_alert_history(self):
        """Load alert history from file"""
        try:
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r') as f:
                    self.alert_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading alert history: {e}")
            self.alert_history = []
    
    def save_alert_history(self):
        """Save alert history to file"""
        try:
            with open(self.alert_history_file, 'w') as f:
                json.dump(self.alert_history[-100:], f, indent=2)  # Keep last 100 alerts
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")
    
    def send_desktop_notification(self, title: str, message: str, timeout: int = 10):
        """Send desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
                app_name="Crypto Trading Alert"
            )
            logger.debug("Desktop notification sent successfully")
        except Exception as e:
            # Desktop notifications are optional - don't spam the logs
            logger.debug(f"Desktop notification not available: {e}")
            # Try alternative notification method for macOS
            self.send_macos_notification(title, message)
    
    def send_macos_notification(self, title: str, message: str):
        """Send notification using macOS osascript (AppleScript)"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                # Escape quotes in the message
                title_escaped = title.replace('"', '\\"')
                message_escaped = message.replace('"', '\\"')
                
                script = f'''
                display notification "{message_escaped}" with title "{title_escaped}" sound name "default"
                '''
                
                subprocess.run(['osascript', '-e', script], 
                             capture_output=True, 
                             timeout=5)
                logger.debug("macOS notification sent successfully")
            else:
                logger.debug("Not on macOS, skipping alternative notification")
                
        except Exception as e:
            logger.debug(f"Alternative notification method failed: {e}")
    
    def send_email_notification(self, subject: str, body: str, html_body: str = None):
        """Send email notification"""
        if not self.enable_email_alerts:
            return
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_sender
            message["To"] = ", ".join(self.email_recipients)
            
            # Add text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Create SMTP session
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
            
            if self.email_use_tls:
                server.starttls()  # Enable TLS encryption
            
            server.login(self.email_sender, self.email_password)
            
            # Send email to all recipients
            for recipient in self.email_recipients:
                server.sendmail(self.email_sender, recipient, message.as_string())
            
            server.quit()
            logger.info(f"Email alert sent successfully to {len(self.email_recipients)} recipient(s)")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def create_email_content(self, alerts: List[Dict]) -> tuple:
        """Create email content for alerts"""
        if not alerts:
            return "", ""
        
        # Email subject
        if len(alerts) == 1:
            alert = alerts[0]
            symbol_clean = alert['symbol'].replace('USDT', '/USDT')
            subject = f"🚨 Crypto Alert: {symbol_clean} - {alert['signal']}"
        else:
            subject = f"🚨 Crypto Alerts: {len(alerts)} New Trading Signals"
        
        # Text body
        text_body = "🚀 CRYPTO TRADING ALERT SYSTEM 🚀\n"
        text_body += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text_body += "=" * 50 + "\n\n"
        
        # HTML body
        html_body = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px; }
                .alert { margin: 20px 0; padding: 15px; border-radius: 8px; border-left: 5px solid; }
                .long { border-left-color: #10b981; background-color: #f0fdf4; }
                .short { border-left-color: #ef4444; background-color: #fef2f2; }
                .neutral { border-left-color: #f59e0b; background-color: #fffbeb; }
                .strong { font-weight: bold; }
                .price { font-size: 1.2em; color: #1f2937; }
                .footer { margin-top: 30px; padding: 15px; background-color: #f9fafb; border-radius: 8px; font-size: 0.9em; color: #6b7280; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 CRYPTO TRADING ALERT SYSTEM 🚀</h1>
                <p>""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
        """
        
        for alert in alerts:
            symbol_clean = alert['symbol'].replace('USDT', '/USDT')
            
            # Determine signal type and styling
            if alert['signal'] in ['STRONG_LONG', 'LONG']:
                signal_emoji = "🟢"
                action = "BUY/LONG"
                css_class = "long"
            elif alert['signal'] in ['STRONG_SHORT', 'SHORT']:
                signal_emoji = "🔴"
                action = "SELL/SHORT"
                css_class = "short"
            else:
                signal_emoji = "🟡"
                action = "NEUTRAL"
                css_class = "neutral"
            
            # Add to text body
            text_body += f"{signal_emoji} {symbol_clean} - {alert['signal']}\n"
            text_body += f"Action: {action}\n"
            text_body += f"Price: ${alert['price']:,.4f}\n"
            text_body += f"Strength: {alert['strength']}\n"
            text_body += f"RSI: {alert['rsi']}\n"
            
            if alert['signal'] != 'NEUTRAL':
                text_body += f"Entry Price: ${alert['entry_price']:,.4f}\n"
                if alert['stop_loss'] > 0:
                    text_body += f"Stop Loss: ${alert['stop_loss']:,.4f}\n"
                if alert['take_profit'] > 0:
                    text_body += f"Take Profit: ${alert['take_profit']:,.4f}\n"
            
            text_body += f"Previous Signal: {alert['previous_signal']} → Current: {alert['signal']}\n"
            text_body += "Reasons:\n"
            for reason in alert['reasons']:
                text_body += f"  • {reason}\n"
            text_body += "\n" + "-" * 50 + "\n\n"
            
            # Add to HTML body
            strong_class = " strong" if "STRONG" in alert['signal'] else ""
            html_body += f"""
            <div class="alert {css_class}{strong_class}">
                <h2>{signal_emoji} {symbol_clean} - {alert['signal']}</h2>
                <p><strong>Action:</strong> {action}</p>
                <p class="price"><strong>Price:</strong> ${alert['price']:,.4f}</p>
                <p><strong>Strength:</strong> {alert['strength']}</p>
                <p><strong>RSI:</strong> {alert['rsi']}</p>
            """
            
            if alert['signal'] != 'NEUTRAL':
                html_body += f"<p><strong>Entry Price:</strong> ${alert['entry_price']:,.4f}</p>"
                if alert['stop_loss'] > 0:
                    html_body += f"<p><strong>Stop Loss:</strong> ${alert['stop_loss']:,.4f}</p>"
                if alert['take_profit'] > 0:
                    html_body += f"<p><strong>Take Profit:</strong> ${alert['take_profit']:,.4f}</p>"
            
            html_body += f"""
                <p><strong>Signal Change:</strong> {alert['previous_signal']} → {alert['signal']}</p>
                <p><strong>Analysis Reasons:</strong></p>
                <ul>
            """
            
            for reason in alert['reasons']:
                html_body += f"<li>{reason}</li>"
            
            html_body += "</ul></div>"
        
        # Add footer
        text_body += "\n🤖 This is an automated alert from your Crypto Trading Alert System"
        html_body += """
            <div class="footer">
                <p>🤖 This is an automated alert from your Crypto Trading Alert System</p>
                <p>Please verify all signals before making trading decisions. This system is for informational purposes only.</p>
            </div>
        </body>
        </html>
        """
        
        return subject, text_body, html_body
    
    def format_signal_color(self, signal: str) -> str:
        """Format signal with appropriate colors"""
        color_map = {
            'STRONG_LONG': Fore.GREEN + Back.BLACK + Style.BRIGHT,
            'LONG': Fore.GREEN,
            'NEUTRAL': Fore.YELLOW,
            'SHORT': Fore.RED,
            'STRONG_SHORT': Fore.RED + Back.BLACK + Style.BRIGHT
        }
        return color_map.get(signal, Fore.WHITE) + signal + Style.RESET_ALL
    
    def print_analysis(self, results: Dict):
        """Print formatted analysis results to console"""
        print("\n" + "="*80)
        print(f"{Fore.CYAN + Style.BRIGHT}🚀 CRYPTO TRADING ALERT SYSTEM 🚀{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print("="*80)
        
        for symbol, data in results.items():
            if 'error' in data:
                print(f"\n{Fore.RED}❌ {symbol}: {data['error']}{Style.RESET_ALL}")
                continue
                
            analysis = data['analysis']
            symbol_clean = symbol.replace('USDT', '/USDT')
            
            print(f"\n{Fore.YELLOW + Style.BRIGHT}📊 {symbol_clean}{Style.RESET_ALL}")
            print("-" * 50)
            
            # Signal and strength
            signal_formatted = self.format_signal_color(analysis['signal'])
            print(f"🎯 Signal: {signal_formatted} (Strength: {analysis['strength']})")
            
            # Current price and key metrics
            print(f"💰 Current Price: ${analysis['current_price']:,.4f}")
            print(f"📈 RSI: {analysis['rsi']} {'(Oversold)' if analysis['rsi'] < 30 else '(Overbought)' if analysis['rsi'] > 70 else '(Neutral)'}")
            print(f"📊 MACD: {analysis['macd']}")
            
            # Entry and exit levels
            if analysis['signal'] != 'NEUTRAL':
                print(f"🎯 Entry Price: ${analysis['entry_price']:,.4f}")
                if analysis['stop_loss'] > 0:
                    print(f"🛑 Stop Loss: ${analysis['stop_loss']:,.4f}")
                if analysis['take_profit'] > 0:
                    print(f"🎯 Take Profit: ${analysis['take_profit']:,.4f}")
            
            # Reasons
            print(f"📋 Analysis Reasons:")
            for reason in analysis['reasons']:
                print(f"   • {reason}")
        
        print("\n" + "="*80)
    
    def check_for_new_signals(self, results: Dict) -> List[Dict]:
        """Check for new or changed signals"""
        new_alerts = []
        
        for symbol, data in results.items():
            if 'error' in data:
                continue
                
            analysis = data['analysis']
            current_signal = analysis['signal']
            
            # Check if signal changed or is strong
            previous_signal = self.previous_signals.get(symbol, 'NEUTRAL')
            
            # Create alert for signal changes or strong signals
            should_alert = (
                current_signal != previous_signal or  # Signal changed
                current_signal in ['STRONG_LONG', 'STRONG_SHORT'] or  # Strong signal
                (current_signal in ['LONG', 'SHORT'] and previous_signal == 'NEUTRAL')  # New signal from neutral
            )
            
            if should_alert:
                alert = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': symbol,
                    'signal': current_signal,
                    'previous_signal': previous_signal,
                    'strength': analysis['strength'],
                    'price': analysis['current_price'],
                    'entry_price': analysis['entry_price'],
                    'stop_loss': analysis['stop_loss'],
                    'take_profit': analysis['take_profit'],
                    'rsi': analysis['rsi'],
                    'reasons': analysis['reasons']
                }
                
                new_alerts.append(alert)
                self.alert_history.append(alert)
            
            # Update previous signals
            self.previous_signals[symbol] = current_signal
        
        return new_alerts
    
    def send_alerts(self, alerts: List[Dict]):
        """Send alerts via various channels"""
        if not alerts:
            return
        
        # Send email notification for all alerts at once
        if self.enable_email_alerts:
            try:
                subject, text_body, html_body = self.create_email_content(alerts)
                self.send_email_notification(subject, text_body, html_body)
            except Exception as e:
                logger.error(f"Error sending email alerts: {e}")
        
        # Send individual desktop notifications and console alerts
        for alert in alerts:
            symbol_clean = alert['symbol'].replace('USDT', '/USDT')
            
            # Desktop notification
            title = f"🚨 {symbol_clean} Trading Alert"
            
            if alert['signal'] in ['STRONG_LONG', 'LONG']:
                emoji = "🟢"
                action = "BUY/LONG"
            elif alert['signal'] in ['STRONG_SHORT', 'SHORT']:
                emoji = "🔴"
                action = "SELL/SHORT"
            else:
                emoji = "🟡"
                action = "NEUTRAL"
            
            message = (
                f"{emoji} {action} Signal\n"
                f"Price: ${alert['price']:,.4f}\n"
                f"Strength: {alert['strength']}\n"
                f"RSI: {alert['rsi']}"
            )
            
            if self.enable_desktop_notifications:
                self.send_desktop_notification(title, message)
            
            # Console alert
            print(f"\n{Fore.YELLOW + Back.RED + Style.BRIGHT}🚨 ALERT: {symbol_clean} - {alert['signal']} 🚨{Style.RESET_ALL}")
            print(f"Previous: {alert['previous_signal']} → Current: {alert['signal']}")
            print(f"Price: ${alert['price']:,.4f} | Strength: {alert['strength']} | RSI: {alert['rsi']}")
            
        # Save alerts to history
        self.save_alert_history()
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring in a separate thread"""
        duration_msg = f" for {self.max_duration // 3600}h {(self.max_duration % 3600) // 60}m" if self.max_duration else ""
        logger.info(f"Starting continuous monitoring{duration_msg} (checking every {self.check_interval} seconds)")
        
        self.start_time = time.time()
        
        while self.running:
            try:
                # Check if max duration has been reached
                if self.max_duration:
                    elapsed_time = time.time() - self.start_time
                    if elapsed_time >= self.max_duration:
                        logger.info(f"Maximum monitoring duration ({self.max_duration // 3600}h {(self.max_duration % 3600) // 60}m) reached. Stopping monitoring.")
                        self.stop_monitoring()
                        break
                
                # Analyze all symbols
                results = self.analyzer.analyze_all_symbols()
                
                # Print analysis with time remaining if duration is set
                if self.max_duration:
                    elapsed_time = time.time() - self.start_time
                    remaining_time = self.max_duration - elapsed_time
                    remaining_hours = int(remaining_time // 3600)
                    remaining_minutes = int((remaining_time % 3600) // 60)
                    print(f"\n⏰ Time remaining: {remaining_hours}h {remaining_minutes}m")
                
                self.print_analysis(results)
                
                # Check for new signals and send alerts
                new_alerts = self.check_for_new_signals(results)
                if new_alerts:
                    self.send_alerts(new_alerts)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.running:
            logger.warning("Monitoring is already running")
            return
        
        self.running = True
        
        # Start monitoring in a separate thread
        monitoring_thread = threading.Thread(target=self.run_continuous_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return monitoring_thread
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        logger.info("Monitoring stopped")
    
    def get_current_analysis(self) -> Dict:
        """Get current analysis for all symbols"""
        return self.analyzer.analyze_all_symbols()
    
    def get_alert_history(self, limit: int = 20) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    duration = None
    if len(sys.argv) > 1:
        try:
            # Parse duration argument (e.g., "1h", "30m", "2h30m")
            duration_str = sys.argv[1].lower()
            duration = 0
            
            # Parse hours
            if 'h' in duration_str:
                hours_part = duration_str.split('h')[0]
                if hours_part:
                    duration += int(hours_part) * 3600
                duration_str = duration_str.split('h')[1] if 'h' in duration_str else ""
            
            # Parse minutes
            if 'm' in duration_str:
                minutes_part = duration_str.split('m')[0]
                if minutes_part:
                    duration += int(minutes_part) * 60
            
            # If just a number, assume it's hours
            elif duration_str.isdigit():
                duration = int(duration_str) * 3600
                
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid duration format. Use: 1h, 30m, 2h30m, or just 1 (hours){Style.RESET_ALL}")
            sys.exit(1)
    
    # Create and start the alert system
    alert_system = AlertSystem(check_interval=300, max_duration=duration)  # Check every 5 minutes
    
    try:
        duration_msg = f" for {duration // 3600}h {(duration % 3600) // 60}m" if duration else ""
        print(f"{Fore.GREEN + Style.BRIGHT}🚀 Starting Crypto Trading Alert System{duration_msg}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Monitoring BTC and ETH every 5 minutes{Style.RESET_ALL}")
        if duration:
            print(f"{Fore.YELLOW}Will automatically stop after {duration // 3600}h {(duration % 3600) // 60}m{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop manually{Style.RESET_ALL}\n")
        
        # Start monitoring
        monitoring_thread = alert_system.start_monitoring()
        
        # Keep the main thread alive
        while alert_system.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Stopping monitoring system...{Style.RESET_ALL}")
        alert_system.stop_monitoring()
        print(f"{Fore.GREEN}System stopped successfully!{Style.RESET_ALL}") 