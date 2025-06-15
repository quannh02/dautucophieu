#!/usr/bin/env python3
"""
Quick Crypto Analysis Script
Get instant technical analysis for BTC and ETH
"""

import sys
from crypto_analyzer import CryptoAnalyzer
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print application banner"""
    print(f"{Fore.CYAN + Style.BRIGHT}")
    print("🚀" * 20)
    print("🚀 CRYPTO TRADING ANALYZER 🚀")
    print("🚀" * 20)
    print(f"{Style.RESET_ALL}")

def format_signal_emoji(signal):
    """Get emoji for signal"""
    emoji_map = {
        'STRONG_LONG': '🟢🚀',
        'LONG': '🟢',
        'NEUTRAL': '🟡',
        'SHORT': '🔴',
        'STRONG_SHORT': '🔴💥'
    }
    return emoji_map.get(signal, '⚪')

def print_analysis_summary(symbol, analysis):
    """Print a concise analysis summary"""
    symbol_clean = symbol.replace('USDT', '/USDT')
    emoji = format_signal_emoji(analysis['signal'])
    
    print(f"\n{Fore.YELLOW + Style.BRIGHT}{'='*60}")
    print(f"📊 {symbol_clean} ANALYSIS")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # Signal
    signal_color = Fore.GREEN if 'LONG' in analysis['signal'] else Fore.RED if 'SHORT' in analysis['signal'] else Fore.YELLOW
    print(f"{emoji} {signal_color + Style.BRIGHT}SIGNAL: {analysis['signal']} (Strength: {analysis['strength']}){Style.RESET_ALL}")
    
    # Key metrics
    print(f"💰 Current Price: ${analysis['current_price']:,.4f}")
    print(f"📈 RSI: {analysis['rsi']:.2f} {'(Oversold)' if analysis['rsi'] < 30 else '(Overbought)' if analysis['rsi'] > 70 else '(Neutral)'}")
    print(f"📊 MACD: {analysis['macd']:.6f}")
    
    # Entry/Exit levels
    if analysis['signal'] != 'NEUTRAL':
        print(f"\n🎯 TRADING LEVELS:")
        print(f"   Entry: ${analysis['entry_price']:,.4f}")
        if analysis['stop_loss'] > 0:
            print(f"   Stop Loss: ${analysis['stop_loss']:,.4f}")
        if analysis['take_profit'] > 0:
            print(f"   Take Profit: ${analysis['take_profit']:,.4f}")
    
    # Analysis reasons
    print(f"\n📋 ANALYSIS DETAILS:")
    for i, reason in enumerate(analysis['reasons'], 1):
        print(f"   {i}. {reason}")
    
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")

def get_recommendation(signal, rsi, price, entry_price):
    """Get trading recommendation"""
    if signal in ['STRONG_LONG', 'LONG']:
        risk_level = "HIGH" if signal == "STRONG_LONG" else "MEDIUM"
        return f"""
{Fore.GREEN + Style.BRIGHT}🎯 RECOMMENDATION: BUY/LONG{Style.RESET_ALL}
Risk Level: {risk_level}
Suggested Action: Consider opening a long position
Current Sentiment: Bullish momentum detected
"""
    elif signal in ['STRONG_SHORT', 'SHORT']:
        risk_level = "HIGH" if signal == "STRONG_SHORT" else "MEDIUM"
        return f"""
{Fore.RED + Style.BRIGHT}🎯 RECOMMENDATION: SELL/SHORT{Style.RESET_ALL}
Risk Level: {risk_level}
Suggested Action: Consider opening a short position
Current Sentiment: Bearish momentum detected
"""
    else:
        return f"""
{Fore.YELLOW + Style.BRIGHT}🎯 RECOMMENDATION: HOLD/WAIT{Style.RESET_ALL}
Risk Level: LOW
Suggested Action: Wait for clearer signals
Current Sentiment: Market is consolidating
"""

def main():
    """Main function"""
    print_banner()
    
    # Check for interval argument
    interval = "5m"  # default
    if len(sys.argv) > 1:
        interval = sys.argv[1]
        if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
            print(f"{Fore.RED}Invalid interval. Using default 5m{Style.RESET_ALL}")
            interval = "5m"
    
    print(f"{Fore.CYAN}Analyzing BTC and ETH on {interval} timeframe using Binance API...{Style.RESET_ALL}\n")
    
    try:
        # Initialize analyzer
        analyzer = CryptoAnalyzer()
        
        # Analyze symbols
        print(f"{Fore.BLUE}Fetching market data for {interval} interval...{Style.RESET_ALL}")
        results = analyzer.analyze_all_symbols(interval=interval)
        
        if not results:
            print(f"{Fore.RED}❌ Failed to fetch market data{Style.RESET_ALL}")
            return
        
        # Print analysis for each symbol
        for symbol, data in results.items():
            if 'error' in data:
                print(f"{Fore.RED}❌ Error analyzing {symbol}: {data['error']}{Style.RESET_ALL}")
                continue
            
            analysis = data['analysis']
            print_analysis_summary(symbol, analysis)
            
            # Print recommendation
            print(get_recommendation(
                analysis['signal'], 
                analysis['rsi'], 
                analysis['current_price'], 
                analysis['entry_price']
            ))
        
        # Footer
        print(f"\n{Fore.CYAN + Style.BRIGHT}📊 Analysis completed at {analysis['timestamp']} ({interval} timeframe)")
        print(f"⚠️  This is for educational purposes only. Not financial advice!")
        print(f"🔄 Run again: python quick_analysis.py [interval]")
        print(f"   Available intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M")
        print(f"   Example: python quick_analysis.py 1h")
        print(f"🌐 Web interface: streamlit run streamlit_app.py")
        print(f"🚨 Real-time alerts: python alert_system.py{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Analysis interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure you have internet connection and all dependencies installed{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 