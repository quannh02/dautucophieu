#!/usr/bin/env python3
"""
Standalone Crypto News Analysis Script
Analyze cryptocurrency news sentiment for trading insights
"""

import sys
from news_analyzer import NewsAnalyzer
from colorama import Fore, Back, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print application banner"""
    print(f"{Fore.CYAN + Style.BRIGHT}")
    print("📰" * 20)
    print(f"📰 CRYPTO NEWS SENTIMENT ANALYZER 📰")
    print("📰" * 20)
    print(f"{Style.RESET_ALL}")

def print_news_analysis(analysis: dict, crypto_symbol: str):
    """Print formatted news analysis"""
    print(f"\n{Fore.YELLOW + Style.BRIGHT}📊 {crypto_symbol} News Analysis{Style.RESET_ALL}")
    print("-" * 60)
    
    # Overall sentiment
    sentiment = analysis['overall_sentiment']
    if sentiment == 'VERY_POSITIVE':
        sentiment_color = Fore.GREEN + Back.BLACK + Style.BRIGHT
    elif sentiment == 'POSITIVE':
        sentiment_color = Fore.GREEN
    elif sentiment == 'VERY_NEGATIVE':
        sentiment_color = Fore.RED + Back.BLACK + Style.BRIGHT
    elif sentiment == 'NEGATIVE':
        sentiment_color = Fore.RED
    else:
        sentiment_color = Fore.YELLOW
    
    print(f"📈 Overall Sentiment: {sentiment_color}{sentiment}{Style.RESET_ALL}")
    print(f"📊 Articles Analyzed: {analysis['articles_analyzed']}")
    print(f"📅 Analysis Time: {analysis['analysis_timestamp']}")
    
    if analysis['articles_analyzed'] > 0:
        print(f"📊 Average Sentiment Score: {analysis['average_polarity']}")
        print(f"🎯 Impact Score: {analysis['average_impact']}")
        
        # Trading recommendation
        recommendation = analysis['trading_recommendation']
        action = recommendation['action']
        
        if action in ['STRONG_BUY', 'BUY']:
            action_color = Fore.GREEN + Style.BRIGHT
        elif action in ['STRONG_SELL', 'SELL']:
            action_color = Fore.RED + Style.BRIGHT
        else:
            action_color = Fore.YELLOW
        
        print(f"\n🎯 Trading Recommendation: {action_color}{action}{Style.RESET_ALL}")
        print(f"💡 Reasoning: {recommendation['reasoning']}")
        print(f"📊 Confidence: {recommendation['confidence']}%")
        print(f"⚠️ Risk Level: {recommendation['risk_level']}")
        
        # Sentiment distribution
        dist = analysis['sentiment_distribution']
        print(f"\n📊 Sentiment Distribution:")
        print(f"   🟢 Positive: {dist['positive']} articles")
        print(f"   🔴 Negative: {dist['negative']} articles")
        print(f"   🟡 Neutral: {dist['neutral']} articles")
        
        # Market sentiment distribution
        market_dist = analysis['market_sentiment_distribution']
        print(f"\n📈 Market Sentiment Keywords:")
        print(f"   🐂 Bullish: {market_dist['bullish']} mentions")
        print(f"   🐻 Bearish: {market_dist['bearish']} mentions")
        print(f"   ⚖️ Neutral: {market_dist['neutral']} mentions")
        
        # News sources
        if analysis['news_sources']:
            print(f"\n📰 News Sources: {', '.join(analysis['news_sources'])}")
        
        # Top articles
        if analysis['top_articles']:
            print(f"\n📰 Top Relevant Articles:")
            for i, article in enumerate(analysis['top_articles'][:3], 1):
                article_info = article['article']
                sentiment_info = article['sentiment']
                
                sentiment_emoji = "🟢" if sentiment_info['sentiment'] == 'positive' else "🔴" if sentiment_info['sentiment'] == 'negative' else "🟡"
                
                print(f"\n   {i}. {sentiment_emoji} {article_info['title']}")
                print(f"      📅 {article_info['published_date']}")
                print(f"      📰 {article_info['source']}")
                print(f"      📊 Sentiment: {sentiment_info['sentiment'].title()} (Score: {sentiment_info['polarity']})")
                if article_info['summary']:
                    print(f"      📝 {article_info['summary'][:150]}...")
    else:
        print(f"\n{Fore.YELLOW}⚠️ No relevant articles found for {crypto_symbol} in the specified time period.{Style.RESET_ALL}")
        print(f"📊 Trading Recommendation: {analysis['trading_recommendation']['action']}")

def main():
    """Main function"""
    print_banner()
    
    # Parse command line arguments
    crypto_symbol = 'BTC'  # Default
    hours_back = 24  # Default
    
    if len(sys.argv) > 1:
        crypto_symbol = sys.argv[1].upper()
        if crypto_symbol not in ['BTC', 'ETH', 'CRYPTO']:
            print(f"{Fore.YELLOW}⚠️ Supported symbols: BTC, ETH, CRYPTO. Using BTC as default.{Style.RESET_ALL}")
            crypto_symbol = 'BTC'
    
    if len(sys.argv) > 2:
        try:
            hours_back = int(sys.argv[2])
            if hours_back < 1 or hours_back > 168:  # Max 1 week
                print(f"{Fore.YELLOW}⚠️ Hours must be between 1-168. Using 24 as default.{Style.RESET_ALL}")
                hours_back = 24
        except ValueError:
            print(f"{Fore.YELLOW}⚠️ Invalid hours format. Using 24 as default.{Style.RESET_ALL}")
            hours_back = 24
    
    try:
        print(f"{Fore.BLUE}🔍 Analyzing {crypto_symbol} news from the last {hours_back} hours...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📡 Fetching news from multiple sources...{Style.RESET_ALL}")
        
        # Initialize analyzer
        analyzer = NewsAnalyzer()
        
        # Analyze news
        analysis = analyzer.analyze_crypto_news(crypto_symbol, hours_back=hours_back)
        
        # Print results
        print_news_analysis(analysis, crypto_symbol)
        
        # Footer
        print(f"\n{Fore.CYAN + Style.BRIGHT}📊 Analysis completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️ This analysis is for informational purposes only. Not financial advice!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔄 Run again: python news_analysis.py [BTC|ETH|CRYPTO] [hours]{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📈 Example: python news_analysis.py BTC 12{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚨 Real-time alerts: python alert_system.py{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Analysis interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error during analysis: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure you have internet connection and all dependencies installed{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 