#!/usr/bin/env python3
"""
Gold Market Analysis Script
Get instant technical analysis for gold markets
Supports Gold Futures (GC=F) and Gold ETF (GOLD)
"""

import sys
from gold_analyzer import GoldAnalyzer
from colorama import Fore, Back, Style, init
from translations import get_text, get_signal_translation, get_analysis_reason_translation

# Initialize colorama
init(autoreset=True)

def print_banner(lang='en'):
    """Print application banner"""
    print(f"{Fore.YELLOW + Style.BRIGHT}")
    print("🥇" * 20)
    print(f"🥇 {get_text('gold_analyzer', lang) if 'gold_analyzer' in get_text.__dict__ else 'GOLD MARKET ANALYZER'} 🥇")
    print("🥇" * 20)
    print(f"{Style.RESET_ALL}")

def format_signal_emoji(signal: str) -> str:
    """Get emoji for signal type"""
    if signal in ['STRONG_LONG', 'LONG']:
        return "🟢"
    elif signal in ['STRONG_SHORT', 'SHORT']:
        return "🔴"
    else:
        return "🟡"

def print_analysis_summary(symbol, analysis, lang='en'):
    """Print a concise analysis summary for gold"""
    symbol_names = {
        'GC=F': 'Gold Futures (COMEX)',
        'GLD': 'Gold ETF (SPDR)'
    }
    
    symbol_display = symbol_names.get(symbol, symbol)
    emoji = format_signal_emoji(analysis['signal'])
    
    print(f"\n{Fore.YELLOW + Style.BRIGHT}{'='*70}")
    print(f"🥇 {symbol_display} ANALYSIS")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    # Signal
    signal_color = Fore.GREEN if 'LONG' in analysis['signal'] else Fore.RED if 'SHORT' in analysis['signal'] else Fore.YELLOW
    translated_signal = get_signal_translation(analysis['signal'], lang)
    strength_label = get_text('signal_strength_label', lang) if 'signal_strength_label' in get_text.__dict__ else 'Strength'
    print(f"{emoji} {signal_color + Style.BRIGHT}SIGNAL: {translated_signal} ({strength_label}: {analysis['strength']}){Style.RESET_ALL}")
    
    # Key metrics
    price_label = get_text('current_price', lang) if 'current_price' in get_text.__dict__ else 'Current Price'
    print(f"{price_label}: ${analysis['current_price']:,.2f}")
    
    rsi_status = get_text('oversold', lang) if analysis['rsi'] < 30 else get_text('overbought', lang) if analysis['rsi'] > 70 else get_text('neutral_rsi', lang)
    if 'oversold' not in get_text.__dict__:
        rsi_status = 'Oversold' if analysis['rsi'] < 30 else 'Overbought' if analysis['rsi'] > 70 else 'Neutral'
    
    print(f"📈 RSI: {analysis['rsi']:.2f} ({rsi_status})")
    print(f"📊 MACD: {analysis['macd']:.6f}")
    
    # Additional gold-specific indicators
    if 'cci' in analysis:
        print(f"📈 CCI: {analysis['cci']:.2f}")
    if 'atr' in analysis:
        print(f"📊 ATR: {analysis['atr']:.2f}")
    
    # Entry/Exit levels
    if analysis['signal'] != 'NEUTRAL':
        trading_levels_label = get_text('trading_levels', lang) if 'trading_levels' in get_text.__dict__ else 'Trading Levels'
        print(f"\n{trading_levels_label}:")
        
        entry_label = get_text('entry_price', lang) if 'entry_price' in get_text.__dict__ else 'Entry Price'
        print(f"   {entry_label}: ${analysis['entry_price']:,.2f}")
        
        if analysis['stop_loss'] > 0:
            stop_label = get_text('stop_loss', lang) if 'stop_loss' in get_text.__dict__ else 'Stop Loss'
            print(f"   {stop_label}: ${analysis['stop_loss']:,.2f}")
        
        if analysis['take_profit'] > 0:
            profit_label = get_text('take_profit', lang) if 'take_profit' in get_text.__dict__ else 'Take Profit'
            print(f"   {profit_label}: ${analysis['take_profit']:,.2f}")
    
    # Analysis reasons
    details_label = get_text('analysis_details', lang) if 'analysis_details' in get_text.__dict__ else 'Analysis Details'
    print(f"\n{details_label}:")
    for i, reason in enumerate(analysis['reasons'], 1):
        translated_reason = get_analysis_reason_translation(reason, lang) if hasattr(get_analysis_reason_translation, '__call__') else reason
        print(f"   {i}. {translated_reason}")
    
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")

def get_gold_recommendation(signal, rsi, price, entry_price, lang='en'):
    """Get trading recommendation for gold"""
    if signal in ['STRONG_LONG', 'LONG']:
        risk_level = "High Risk" if signal == "STRONG_LONG" else "Medium Risk"
        return f"""
{Fore.GREEN + Style.BRIGHT}RECOMMENDATION: BUY/LONG GOLD{Style.RESET_ALL}
Risk Level: {risk_level}
Suggested Action: Consider long position in gold
Current Sentiment: Bullish momentum detected
Gold Analysis: Technical indicators suggest upward price movement
"""
    elif signal in ['STRONG_SHORT', 'SHORT']:
        risk_level = "High Risk" if signal == "STRONG_SHORT" else "Medium Risk"
        return f"""
{Fore.RED + Style.BRIGHT}RECOMMENDATION: SELL/SHORT GOLD{Style.RESET_ALL}
Risk Level: {risk_level}
Suggested Action: Consider short position in gold
Current Sentiment: Bearish momentum detected
Gold Analysis: Technical indicators suggest downward price movement
"""
    else:
        return f"""
{Fore.YELLOW + Style.BRIGHT}RECOMMENDATION: HOLD/WAIT{Style.RESET_ALL}
Risk Level: Low Risk
Suggested Action: Wait for clearer signals
Current Sentiment: Market consolidating
Gold Analysis: No clear directional bias detected
"""

def main():
    """Main function"""
    print_banner()
    
    # Parse command line arguments
    interval = "1h"  # Default interval for gold analysis
    lang = 'en'  # Default language
    
    if len(sys.argv) > 1:
        interval_arg = sys.argv[1].lower()
        valid_intervals = ["5m", "15m", "30m", "1h", "4h", "1d"]
        if interval_arg in valid_intervals:
            interval = interval_arg
        else:
            print(f"{Fore.YELLOW}⚠️ Invalid interval. Using default: 1h{Style.RESET_ALL}")
            print(f"Valid intervals: {', '.join(valid_intervals)}")
            interval = "1h"
    
    if len(sys.argv) > 2:
        lang_arg = sys.argv[2].lower()
        if lang_arg in ['en', 'vi']:
            lang = lang_arg
        else:
            print(f"{Fore.YELLOW}⚠️ Supported languages: en, vi. Using default: en{Style.RESET_ALL}")
            lang = 'en'
    
    try:
        # Initialize analyzer
        analyzer = GoldAnalyzer()
        
        # Analyze gold symbols
        fetching_text = f"Fetching gold market data for {interval} timeframe..."
        print(f"{Fore.BLUE}{fetching_text}{Style.RESET_ALL}")
        
        results = analyzer.analyze_all_symbols(interval=interval)
        
        if not results:
            print(f"{Fore.RED}Failed to fetch gold market data. Please check your internet connection.{Style.RESET_ALL}")
            return
        
        # Print analysis for each symbol
        for symbol, data in results.items():
            if 'error' in data:
                print(f"{Fore.RED}Error analyzing {symbol}: {data['error']}{Style.RESET_ALL}")
                continue
            
            analysis = data['analysis']
            print_analysis_summary(symbol, analysis, lang)
            
            # Print recommendation
            print(get_gold_recommendation(
                analysis['signal'], 
                analysis['rsi'], 
                analysis['current_price'], 
                analysis['entry_price'],
                lang
            ))
        
        # Footer
        timestamp = analysis['timestamp'] if 'analysis' in locals() else "N/A"
        print(f"\n{Fore.CYAN + Style.BRIGHT}📊 Gold market analysis completed at {timestamp} ({interval} timeframe)")
        print(f"⚠️  This is for educational purposes only. Not financial advice!")
        print(f"🔄 Run again: python gold_analysis.py [interval] [language]")
        print(f"   Available intervals: 5m, 15m, 30m, 1h, 4h, 1d")
        print(f"   Available languages: en, vi")
        print(f"   Example: python gold_analysis.py 1h en")
        print(f"🌐 Web interface: streamlit run streamlit_app.py")
        print(f"🚨 Real-time alerts: python alert_system.py{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Gold analysis interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error during analysis: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please ensure you have internet connection and all dependencies installed{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 