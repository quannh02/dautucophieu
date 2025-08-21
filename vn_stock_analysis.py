#!/usr/bin/env python3
"""
Vietnamese Stock Market Analysis Tool
Standalone script for quick Vietnamese stock analysis
"""

import argparse
import sys
from colorama import Fore, Style, init
from vn_stock_analyzer import VNStockAnalyzer
from translations import get_text

# Initialize colorama for cross-platform colored output
init()

def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.GREEN}╔═══════════════════════════════════════════════════════════════╗
║               🇻🇳 VIETNAMESE STOCK MARKET ANALYZER            ║
║                   Real-time Technical Analysis                ║
║                     HSX • HNX • Major Stocks                 ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.CYAN}📈 Supported Stocks:{Style.RESET_ALL}
  • VNM.VN (Vinamilk)      • VCB.VN (Vietcombank)
  • VIC.VN (Vingroup)      • HPG.VN (Hoa Phat Group)  
  • TCB.VN (Techcombank)   • MSN.VN (Masan Group)
  • FPT.VN (FPT Corp)      • MWG.VN (Mobile World)
  • GAS.VN (PV Gas)        • CTG.VN (VietinBank)
  • NVL.VN (NovaLand)      • TPB.VN (Tien Phong Bank)
  • HHV.VN (Hoa Hao)       • VJC.VN (VietJet Aviation)
  • VND.VN (VN Direct)     • ... (15 total stocks)

{Fore.YELLOW}⏰ Intervals:{Style.RESET_ALL} 5m, 15m, 1h, 4h, 1d
{Fore.YELLOW}🌐 Languages:{Style.RESET_ALL} en (English), vi (Vietnamese)
"""
    print(banner)

def print_analysis_summary(analysis, symbol, lang='en'):
    """Print formatted analysis summary"""
    
    # Get signal color
    signal = analysis['signal']
    if 'LONG' in signal:
        signal_color = Fore.GREEN
        signal_icon = "📈"
    elif 'SHORT' in signal:
        signal_color = Fore.RED  
        signal_icon = "📉"
    else:
        signal_color = Fore.YELLOW
        signal_icon = "➡️"
    
    company_name = analysis.get('company_name', symbol)
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 {company_name} ({symbol}) - Vietnamese Stock Analysis{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    # Main signal
    print(f"\n{signal_color}🎯 Signal: {signal_icon} {signal} (Strength: {analysis['strength']}/10){Style.RESET_ALL}")
    
    # Price information
    print(f"\n{Fore.WHITE}💰 Price Information:{Style.RESET_ALL}")
    print(f"  Current Price: {Fore.CYAN}{analysis['current_price']:,.1f}K VND{Style.RESET_ALL}")
    
    if signal != 'NEUTRAL':
        print(f"  Entry Price:   {Fore.GREEN}{analysis['entry_price']:,.1f}K VND{Style.RESET_ALL}")
        if analysis['stop_loss'] > 0:
            print(f"  Stop Loss:     {Fore.RED}{analysis['stop_loss']:,.1f}K VND{Style.RESET_ALL}")
        if analysis['take_profit'] > 0:
            print(f"  Take Profit:   {Fore.GREEN}{analysis['take_profit']:,.1f}K VND{Style.RESET_ALL}")
    
    # Technical indicators
    print(f"\n{Fore.WHITE}📊 Technical Indicators:{Style.RESET_ALL}")
    
    # RSI with status
    rsi = analysis['rsi']
    if rsi < 30:
        rsi_status = f"{Fore.GREEN}Oversold{Style.RESET_ALL}"
    elif rsi > 70:
        rsi_status = f"{Fore.RED}Overbought{Style.RESET_ALL}"
    else:
        rsi_status = f"{Fore.YELLOW}Neutral{Style.RESET_ALL}"
    
    print(f"  RSI (14):      {rsi:.1f} ({rsi_status})")
    print(f"  MACD:          {analysis['macd']:.4f}")
    print(f"  ATR:           {analysis['atr']:.2f}")
    print(f"  Volume Ratio:  {analysis['volume_ratio']:.2f}x")
    
    if 'mfi' in analysis and analysis['mfi'] > 0:
        print(f"  Money Flow:    {analysis['mfi']:.1f}")
    
    # Analysis reasons
    print(f"\n{Fore.WHITE}🔍 Analysis Details:{Style.RESET_ALL}")
    for i, reason in enumerate(analysis['reasons'][:5], 1):
        print(f"  {i}. {reason}")
    
    # Scoring breakdown
    if 'bullish_score' in analysis and 'bearish_score' in analysis:
        print(f"\n{Fore.WHITE}⚖️  Signal Breakdown:{Style.RESET_ALL}")
        print(f"  Bullish Score: {Fore.GREEN}{analysis['bullish_score']}{Style.RESET_ALL}")
        print(f"  Bearish Score: {Fore.RED}{analysis['bearish_score']}{Style.RESET_ALL}")
        net_score = analysis['bullish_score'] - analysis['bearish_score']
        print(f"  Net Score:     {signal_color}{net_score:+d}{Style.RESET_ALL}")

def get_vietnamese_recommendation(signal, strength, lang='en'):
    """Get Vietnamese stock recommendation"""
    if lang == 'vi':
        if signal == 'STRONG_LONG':
            return f"🟢 {Fore.GREEN}MUA MẠNH{Style.RESET_ALL} - Tín hiệu tăng rất mạnh"
        elif signal == 'LONG':
            return f"🟢 {Fore.GREEN}MUA{Style.RESET_ALL} - Tín hiệu tăng"
        elif signal == 'STRONG_SHORT':
            return f"🔴 {Fore.RED}BÁN MẠNH{Style.RESET_ALL} - Tín hiệu giảm rất mạnh"
        elif signal == 'SHORT':
            return f"🔴 {Fore.RED}BÁN{Style.RESET_ALL} - Tín hiệu giảm"
        else:
            return f"🟡 {Fore.YELLOW}TRUNG TÍNH{Style.RESET_ALL} - Chờ tín hiệu rõ ràng hơn"
    else:
        if signal == 'STRONG_LONG':
            return f"🟢 {Fore.GREEN}STRONG BUY{Style.RESET_ALL} - Very strong bullish signal"
        elif signal == 'LONG':
            return f"🟢 {Fore.GREEN}BUY{Style.RESET_ALL} - Bullish signal"
        elif signal == 'STRONG_SHORT':
            return f"🔴 {Fore.RED}STRONG SELL{Style.RESET_ALL} - Very strong bearish signal"
        elif signal == 'SHORT':
            return f"🔴 {Fore.RED}SELL{Style.RESET_ALL} - Bearish signal"
        else:
            return f"🟡 {Fore.YELLOW}HOLD{Style.RESET_ALL} - Wait for clearer signal"

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vietnamese Stock Market Technical Analysis')
    parser.add_argument('symbol', nargs='?', default='ALL', 
                       help='Stock symbol (e.g., VNM.VN) or ALL for all stocks')
    parser.add_argument('-i', '--interval', default='1h',
                       choices=['5m', '15m', '1h', '4h', '1d'],
                       help='Time interval (default: 1h)')
    parser.add_argument('-l', '--lang', default='en',
                       choices=['en', 'vi'],
                       help='Language: en (English) or vi (Vietnamese)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Limit number of stocks when analyzing all (default: 5)')
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        # Initialize analyzer
        analyzer = VNStockAnalyzer()
        
        if args.symbol.upper() == 'ALL':
            # Analyze all stocks
            print(f"{Fore.CYAN}🔄 Analyzing top {args.limit} Vietnamese stocks ({args.interval} interval)...{Style.RESET_ALL}\n")
            
            results = analyzer.analyze_all_symbols(interval=args.interval, limit=args.limit)
            
            # Sort by signal strength
            sorted_results = sorted(
                [(symbol, data) for symbol, data in results.items() if 'analysis' in data],
                key=lambda x: x[1]['analysis']['strength'],
                reverse=True
            )
            
            # Display results
            for symbol, data in sorted_results:
                if 'error' in data:
                    print(f"{Fore.RED}❌ {symbol}: {data['error']}{Style.RESET_ALL}")
                    continue
                
                analysis = data['analysis']
                print_analysis_summary(analysis, symbol, args.lang)
                
                recommendation = get_vietnamese_recommendation(analysis['signal'], analysis['strength'], args.lang)
                print(f"\n{Fore.WHITE}💡 Recommendation: {recommendation}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'-'*70}{Style.RESET_ALL}")
        
        else:
            # Analyze single stock
            symbol = args.symbol.upper()
            if not symbol.endswith('.VN'):
                symbol += '.VN'
            
            print(f"{Fore.CYAN}🔄 Analyzing {symbol} ({args.interval} interval)...{Style.RESET_ALL}")
            
            result = analyzer.analyze_symbol(symbol, args.interval)
            
            if 'error' in result:
                print(f"{Fore.RED}❌ Error analyzing {symbol}: {result['error']}{Style.RESET_ALL}")
                return
            
            analysis = result['analysis']
            print_analysis_summary(analysis, symbol, args.lang)
            
            recommendation = get_vietnamese_recommendation(analysis['signal'], analysis['strength'], args.lang)
            print(f"\n{Fore.WHITE}💡 Recommendation: {recommendation}{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Analysis interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
