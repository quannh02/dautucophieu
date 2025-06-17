#!/usr/bin/env python3
"""
Quick Crypto Analysis Script
Get instant technical analysis for BTC and ETH
"""

import sys
from crypto_analyzer import CryptoAnalyzer
from colorama import Fore, Back, Style, init
from translations import get_text, get_signal_translation, get_analysis_reason_translation

# Initialize colorama
init(autoreset=True)

def print_banner(lang='en'):
    """Print application banner"""
    print(f"{Fore.CYAN + Style.BRIGHT}")
    print("🚀" * 20)
    print(f"🚀 {get_text('crypto_analyzer', lang)} 🚀")
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

def print_analysis_summary(symbol, analysis, lang='en'):
    """Print a concise analysis summary"""
    symbol_clean = symbol.replace('USDT', '/USDT')
    emoji = format_signal_emoji(analysis['signal'])
    
    print(f"\n{Fore.YELLOW + Style.BRIGHT}{'='*60}")
    print(f"📊 {symbol_clean} ANALYSIS")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # Signal
    signal_color = Fore.GREEN if 'LONG' in analysis['signal'] else Fore.RED if 'SHORT' in analysis['signal'] else Fore.YELLOW
    translated_signal = get_signal_translation(analysis['signal'], lang)
    strength_label = get_text('signal_strength_label', lang)
    print(f"{emoji} {signal_color + Style.BRIGHT}SIGNAL: {translated_signal} ({strength_label}: {analysis['strength']}){Style.RESET_ALL}")
    
    # Key metrics
    print(f"{get_text('current_price', lang)}: ${analysis['current_price']:,.4f}")
    rsi_status = get_text('oversold', lang) if analysis['rsi'] < 30 else get_text('overbought', lang) if analysis['rsi'] > 70 else get_text('neutral_rsi', lang)
    print(f"📈 RSI: {analysis['rsi']:.2f} ({rsi_status})")
    print(f"📊 MACD: {analysis['macd']:.6f}")
    
    # Entry/Exit levels
    if analysis['signal'] != 'NEUTRAL':
        print(f"\n{get_text('trading_levels', lang)}:")
        print(f"   {get_text('entry_price', lang)}: ${analysis['entry_price']:,.4f}")
        if analysis['stop_loss'] > 0:
            print(f"   {get_text('stop_loss', lang)}: ${analysis['stop_loss']:,.4f}")
        if analysis['take_profit'] > 0:
            print(f"   {get_text('take_profit', lang)}: ${analysis['take_profit']:,.4f}")
    
    # Analysis reasons
    print(f"\n{get_text('analysis_details', lang)}:")
    for i, reason in enumerate(analysis['reasons'], 1):
        translated_reason = get_analysis_reason_translation(reason, lang)
        print(f"   {i}. {translated_reason}")
    
    print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")

def get_recommendation(signal, rsi, price, entry_price, lang='en'):
    """Get trading recommendation"""
    if signal in ['STRONG_LONG', 'LONG']:
        risk_level = get_text("risk_high", lang) if signal == "STRONG_LONG" else get_text("risk_medium", lang)
        return f"""
{Fore.GREEN + Style.BRIGHT}{get_text('recommendation', lang)}: {get_text('buy_long', lang)}{Style.RESET_ALL}
{get_text('risk_level', lang)}: {risk_level}
{get_text('suggested_action', lang)}: {get_text('consider_long_position', lang)}
{get_text('current_sentiment', lang)}: {get_text('bullish_momentum', lang)}
"""
    elif signal in ['STRONG_SHORT', 'SHORT']:
        risk_level = get_text("risk_high", lang) if signal == "STRONG_SHORT" else get_text("risk_medium", lang)
        return f"""
{Fore.RED + Style.BRIGHT}{get_text('recommendation', lang)}: {get_text('sell_short', lang)}{Style.RESET_ALL}
{get_text('risk_level', lang)}: {risk_level}
{get_text('suggested_action', lang)}: {get_text('consider_short_position', lang)}
{get_text('current_sentiment', lang)}: {get_text('bearish_momentum', lang)}
"""
    else:
        return f"""
{Fore.YELLOW + Style.BRIGHT}{get_text('recommendation', lang)}: {get_text('hold_wait', lang)}{Style.RESET_ALL}
{get_text('risk_level', lang)}: {get_text('risk_low', lang)}
{get_text('suggested_action', lang)}: {get_text('wait_for_signals', lang)}
{get_text('current_sentiment', lang)}: {get_text('market_consolidating', lang)}
"""

def main():
    """Main function"""
    # Check for language argument
    lang = "en"  # default
    interval = "5m"  # default
    
    # Parse command line arguments
    args = sys.argv[1:]
    if args:
        if args[0] in ["vi", "vietnamese", "--vi", "--vietnamese"]:
            lang = "vi"
            args = args[1:]  # Remove language argument
        
        if args:
            interval = args[0]
            if interval not in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
                print(f"{Fore.RED}{get_text('invalid_interval', lang)}{Style.RESET_ALL}")
                interval = "5m"
    
    print_banner(lang)
    print(f"{Fore.CYAN}{get_text('analyzing_symbols', lang, interval=interval)}{Style.RESET_ALL}\n")
    
    try:
        # Initialize analyzer
        analyzer = CryptoAnalyzer()
        
        # Analyze symbols
        print(f"{Fore.BLUE}{get_text('fetching_data', lang, interval=interval)}{Style.RESET_ALL}")
        results = analyzer.analyze_all_symbols(interval=interval)
        
        if not results:
            print(f"{Fore.RED}{get_text('failed_to_fetch', lang)}{Style.RESET_ALL}")
            return
        
        # Print analysis for each symbol
        for symbol, data in results.items():
            if 'error' in data:
                print(f"{Fore.RED}{get_text('error_occurred', lang, error=data['error'])}{Style.RESET_ALL}")
                continue
            
            analysis = data['analysis']
            print_analysis_summary(symbol, analysis, lang)
            
            # Print recommendation
            print(get_recommendation(
                analysis['signal'], 
                analysis['rsi'], 
                analysis['current_price'], 
                analysis['entry_price'],
                lang
            ))
        
        # Footer
        print(f"\n{Fore.CYAN + Style.BRIGHT}{get_text('analysis_completed', lang, timestamp=analysis['timestamp'], interval=interval)}")
        print(f"{get_text('educational_purpose', lang)}")
        print(f"{get_text('run_again', lang)}")
        if lang == 'en':
            print(f"   {get_text('available_intervals', lang)}")
            print(f"   {get_text('example_usage', lang)}")
        else:
            print(f"   {get_text('available_intervals', lang)}")
            print(f"   {get_text('example_usage', lang)}")
        print(f"{get_text('web_interface', lang)}")
        print(f"{get_text('real_time_alerts', lang)}{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{get_text('analysis_interrupted', lang)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{get_text('error_occurred', lang, error=str(e))}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{get_text('check_connection', lang)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 