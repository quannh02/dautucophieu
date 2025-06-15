import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from colorama import Fore, Back, Style, init
from plyer import notification
import logging
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
    
    def __init__(self, check_interval: int = 60):
        self.analyzer = CryptoAnalyzer()
        self.check_interval = check_interval  # seconds
        self.running = False
        self.previous_signals = {}
        self.alert_history = []
        self.alert_history_file = "alert_history.json"
        
        # Load previous alert history
        self.load_alert_history()
        
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
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
    
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
            
            self.send_desktop_notification(title, message)
            
            # Console alert
            print(f"\n{Fore.YELLOW + Back.RED + Style.BRIGHT}🚨 ALERT: {symbol_clean} - {alert['signal']} 🚨{Style.RESET_ALL}")
            print(f"Previous: {alert['previous_signal']} → Current: {alert['signal']}")
            print(f"Price: ${alert['price']:,.4f} | Strength: {alert['strength']} | RSI: {alert['rsi']}")
            
        # Save alerts to history
        if alerts:
            self.save_alert_history()
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring in a separate thread"""
        logger.info(f"Starting continuous monitoring (checking every {self.check_interval} seconds)")
        
        while self.running:
            try:
                # Analyze all symbols
                results = self.analyzer.analyze_all_symbols()
                
                # Print analysis
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
    # Create and start the alert system
    alert_system = AlertSystem(check_interval=300)  # Check every 5 minutes
    
    try:
        print(f"{Fore.GREEN + Style.BRIGHT}🚀 Starting Crypto Trading Alert System...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Monitoring BTC and ETH every 5 minutes{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")
        
        # Start monitoring
        monitoring_thread = alert_system.start_monitoring()
        
        # Keep the main thread alive
        while alert_system.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Stopping monitoring system...{Style.RESET_ALL}")
        alert_system.stop_monitoring()
        print(f"{Fore.GREEN}System stopped successfully!{Style.RESET_ALL}") 