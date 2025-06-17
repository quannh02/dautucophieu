#!/usr/bin/env python3
"""
Crypto News Analyzer
Fetches and analyzes cryptocurrency news for market sentiment
"""

import requests
import feedparser
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from textblob import TextBlob
import re
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    Cryptocurrency news analyzer with sentiment analysis
    """
    
    def __init__(self):
        self.news_sources = {
            'coindesk': {
                'rss': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'name': 'CoinDesk'
            },
            'cointelegraph': {
                'rss': 'https://cointelegraph.com/rss',
                'name': 'Cointelegraph'
            },
            'decrypt': {
                'rss': 'https://decrypt.co/feed',
                'name': 'Decrypt'
            },
            'bitcoinist': {
                'rss': 'https://bitcoinist.com/feed/',
                'name': 'Bitcoinist'
            }
        }
        
        # Keywords for different cryptocurrencies
        self.crypto_keywords = {
            'BTC': ['bitcoin', 'btc', 'bitcoin price', 'bitcoin market'],
            'ETH': ['ethereum', 'eth', 'ethereum price', 'ethereum market', 'vitalik'],
            'CRYPTO': ['cryptocurrency', 'crypto', 'digital currency', 'blockchain', 'defi', 'nft']
        }
        
        # Market sentiment keywords
        self.bullish_keywords = [
            'bullish', 'bull market', 'surge', 'rally', 'pump', 'moon', 'breakout',
            'all-time high', 'ath', 'gains', 'rise', 'soar', 'spike', 'boom',
            'adoption', 'institutional', 'investment', 'positive', 'optimistic',
            'upgrade', 'partnership', 'breakthrough', 'milestone'
        ]
        
        self.bearish_keywords = [
            'bearish', 'bear market', 'crash', 'dump', 'fall', 'decline', 'drop',
            'correction', 'sell-off', 'liquidation', 'fear', 'panic', 'recession',
            'regulation', 'ban', 'crackdown', 'negative', 'pessimistic',
            'hack', 'scam', 'fraud', 'bubble', 'overvalued'
        ]
        
    def fetch_rss_news(self, source_key: str, max_articles: int = 20) -> List[Dict]:
        """Fetch news from RSS feed"""
        try:
            source = self.news_sources.get(source_key)
            if not source:
                logger.error(f"Unknown news source: {source_key}")
                return []
            
            logger.info(f"Fetching news from {source['name']}...")
            feed = feedparser.parse(source['rss'])
            
            articles = []
            for entry in feed.entries[:max_articles]:
                article = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': source['name'],
                    'source_key': source_key
                }
                
                # Parse published date
                try:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        article['published_date'] = datetime(*entry.published_parsed[:6])
                    else:
                        article['published_date'] = datetime.now()
                except:
                    article['published_date'] = datetime.now()
                
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {source['name']}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS news from {source_key}: {e}")
            return []
    
    def fetch_all_news(self, max_articles_per_source: int = 15) -> List[Dict]:
        """Fetch news from all configured sources"""
        all_articles = []
        
        for source_key in self.news_sources.keys():
            articles = self.fetch_rss_news(source_key, max_articles_per_source)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful to APIs
        
        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x['published_date'], reverse=True)
        
        # Remove duplicates based on title similarity
        unique_articles = self.remove_duplicate_articles(all_articles)
        
        logger.info(f"Total unique articles fetched: {len(unique_articles)}")
        return unique_articles
    
    def remove_duplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_lower = article['title'].lower()
            # Simple deduplication based on first 50 characters
            title_key = title_lower[:50]
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
            subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'confidence': 0.0
            }
    
    def analyze_crypto_relevance(self, article: Dict, crypto_symbol: str = 'CRYPTO') -> Dict:
        """Analyze how relevant an article is to a specific cryptocurrency"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # Get keywords for the crypto
        keywords = self.crypto_keywords.get(crypto_symbol, self.crypto_keywords['CRYPTO'])
        
        # Count keyword matches
        relevance_score = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in content:
                relevance_score += 1
                matched_keywords.append(keyword)
        
        # Calculate relevance percentage
        relevance_percentage = min(100, (relevance_score / len(keywords)) * 100)
        
        return {
            'relevance_score': relevance_score,
            'relevance_percentage': round(relevance_percentage, 1),
            'matched_keywords': matched_keywords,
            'is_relevant': relevance_score > 0
        }
    
    def analyze_market_sentiment_keywords(self, text: str) -> Dict:
        """Analyze market sentiment based on specific keywords"""
        text_lower = text.lower()
        
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
        
        total_sentiment_keywords = bullish_count + bearish_count
        
        if total_sentiment_keywords == 0:
            market_sentiment = 'neutral'
            sentiment_score = 0
        elif bullish_count > bearish_count:
            market_sentiment = 'bullish'
            sentiment_score = (bullish_count - bearish_count) / total_sentiment_keywords
        elif bearish_count > bullish_count:
            market_sentiment = 'bearish'
            sentiment_score = -(bearish_count - bullish_count) / total_sentiment_keywords
        else:
            market_sentiment = 'neutral'
            sentiment_score = 0
        
        return {
            'market_sentiment': market_sentiment,
            'sentiment_score': round(sentiment_score, 3),
            'bullish_keywords': bullish_count,
            'bearish_keywords': bearish_count,
            'total_sentiment_keywords': total_sentiment_keywords
        }
    
    def analyze_article(self, article: Dict, crypto_symbol: str = 'CRYPTO') -> Dict:
        """Perform comprehensive analysis on a single article"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = f"{title}. {summary}"
        
        # Basic sentiment analysis
        sentiment_analysis = self.analyze_sentiment(content)
        
        # Crypto relevance analysis
        relevance_analysis = self.analyze_crypto_relevance(article, crypto_symbol)
        
        # Market sentiment keyword analysis
        market_sentiment = self.analyze_market_sentiment_keywords(content)
        
        # Combine all analysis
        analysis = {
            'article': {
                'title': title,
                'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                'link': article.get('link', ''),
                'source': article.get('source', ''),
                'published_date': article.get('published_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
            },
            'sentiment': sentiment_analysis,
            'relevance': relevance_analysis,
            'market_sentiment': market_sentiment,
            'overall_impact': self.calculate_overall_impact(sentiment_analysis, relevance_analysis, market_sentiment)
        }
        
        return analysis
    
    def calculate_overall_impact(self, sentiment: Dict, relevance: Dict, market_sentiment: Dict) -> Dict:
        """Calculate overall impact score for trading decisions"""
        # Base impact from sentiment polarity
        impact_score = sentiment['polarity']
        
        # Adjust based on relevance
        relevance_multiplier = relevance['relevance_percentage'] / 100
        impact_score *= relevance_multiplier
        
        # Adjust based on market sentiment keywords
        if market_sentiment['market_sentiment'] == 'bullish':
            impact_score += 0.2
        elif market_sentiment['market_sentiment'] == 'bearish':
            impact_score -= 0.2
        
        # Determine impact level
        if impact_score > 0.3:
            impact_level = 'very_positive'
        elif impact_score > 0.1:
            impact_level = 'positive'
        elif impact_score < -0.3:
            impact_level = 'very_negative'
        elif impact_score < -0.1:
            impact_level = 'negative'
        else:
            impact_level = 'neutral'
        
        return {
            'impact_score': round(impact_score, 3),
            'impact_level': impact_level,
            'trading_signal': self.get_trading_signal_from_impact(impact_level),
            'confidence': round(abs(impact_score), 3)
        }
    
    def get_trading_signal_from_impact(self, impact_level: str) -> str:
        """Convert impact level to trading signal"""
        signal_map = {
            'very_positive': 'STRONG_BULLISH',
            'positive': 'BULLISH',
            'neutral': 'NEUTRAL',
            'negative': 'BEARISH',
            'very_negative': 'STRONG_BEARISH'
        }
        return signal_map.get(impact_level, 'NEUTRAL')
    
    def analyze_crypto_news(self, crypto_symbol: str = 'CRYPTO', hours_back: int = 24, max_articles: int = 50) -> Dict:
        """Analyze recent crypto news for a specific cryptocurrency"""
        logger.info(f"Analyzing {crypto_symbol} news from the last {hours_back} hours...")
        
        # Fetch all news
        all_articles = self.fetch_all_news()
        
        # Filter by time
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_articles = [
            article for article in all_articles 
            if article['published_date'] >= cutoff_time
        ][:max_articles]
        
        if not recent_articles:
            logger.warning("No recent articles found")
            return self.get_empty_analysis(crypto_symbol)
        
        # Analyze each article
        analyzed_articles = []
        for article in recent_articles:
            analysis = self.analyze_article(article, crypto_symbol)
            if analysis['relevance']['is_relevant']:  # Only include relevant articles
                analyzed_articles.append(analysis)
        
        if not analyzed_articles:
            logger.warning(f"No relevant articles found for {crypto_symbol}")
            return self.get_empty_analysis(crypto_symbol)
        
        # Calculate overall sentiment
        overall_analysis = self.calculate_overall_sentiment(analyzed_articles, crypto_symbol)
        
        return overall_analysis
    
    def calculate_overall_sentiment(self, analyzed_articles: List[Dict], crypto_symbol: str) -> Dict:
        """Calculate overall sentiment from analyzed articles"""
        if not analyzed_articles:
            return self.get_empty_analysis(crypto_symbol)
        
        # Aggregate sentiment scores
        total_polarity = sum(article['sentiment']['polarity'] for article in analyzed_articles)
        total_impact = sum(article['overall_impact']['impact_score'] for article in analyzed_articles)
        
        avg_polarity = total_polarity / len(analyzed_articles)
        avg_impact = total_impact / len(analyzed_articles)
        
        # Count sentiment types
        positive_count = sum(1 for article in analyzed_articles if article['sentiment']['sentiment'] == 'positive')
        negative_count = sum(1 for article in analyzed_articles if article['sentiment']['sentiment'] == 'negative')
        neutral_count = len(analyzed_articles) - positive_count - negative_count
        
        # Count market sentiment
        bullish_count = sum(1 for article in analyzed_articles if article['market_sentiment']['market_sentiment'] == 'bullish')
        bearish_count = sum(1 for article in analyzed_articles if article['market_sentiment']['market_sentiment'] == 'bearish')
        
        # Determine overall sentiment
        if avg_impact > 0.2:
            overall_sentiment = 'VERY_POSITIVE'
        elif avg_impact > 0.05:
            overall_sentiment = 'POSITIVE'
        elif avg_impact < -0.2:
            overall_sentiment = 'VERY_NEGATIVE'
        elif avg_impact < -0.05:
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
        
        # Generate trading recommendation
        trading_recommendation = self.generate_trading_recommendation(overall_sentiment, avg_impact, len(analyzed_articles))
        
        return {
            'crypto_symbol': crypto_symbol,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'articles_analyzed': len(analyzed_articles),
            'overall_sentiment': overall_sentiment,
            'average_polarity': round(avg_polarity, 3),
            'average_impact': round(avg_impact, 3),
            'sentiment_distribution': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            'market_sentiment_distribution': {
                'bullish': bullish_count,
                'bearish': bearish_count,
                'neutral': len(analyzed_articles) - bullish_count - bearish_count
            },
            'trading_recommendation': trading_recommendation,
            'top_articles': analyzed_articles[:5],  # Top 5 most relevant articles
            'news_sources': list(set(article['article']['source'] for article in analyzed_articles))
        }
    
    def generate_trading_recommendation(self, sentiment: str, impact: float, article_count: int) -> Dict:
        """Generate trading recommendation based on news sentiment"""
        confidence = min(100, (abs(impact) * 100) + (article_count * 2))
        
        recommendation_map = {
            'VERY_POSITIVE': {
                'action': 'STRONG_BUY',
                'reasoning': 'Very positive news sentiment suggests strong bullish momentum',
                'risk_level': 'MEDIUM'
            },
            'POSITIVE': {
                'action': 'BUY',
                'reasoning': 'Positive news sentiment supports bullish outlook',
                'risk_level': 'MEDIUM'
            },
            'NEUTRAL': {
                'action': 'HOLD',
                'reasoning': 'Neutral news sentiment, no clear directional bias',
                'risk_level': 'LOW'
            },
            'NEGATIVE': {
                'action': 'SELL',
                'reasoning': 'Negative news sentiment suggests bearish pressure',
                'risk_level': 'MEDIUM'
            },
            'VERY_NEGATIVE': {
                'action': 'STRONG_SELL',
                'reasoning': 'Very negative news sentiment indicates strong bearish momentum',
                'risk_level': 'HIGH'
            }
        }
        
        recommendation = recommendation_map.get(sentiment, recommendation_map['NEUTRAL'])
        recommendation['confidence'] = round(confidence, 1)
        recommendation['impact_score'] = round(impact, 3)
        
        return recommendation
    
    def get_empty_analysis(self, crypto_symbol: str) -> Dict:
        """Return empty analysis when no articles are found"""
        return {
            'crypto_symbol': crypto_symbol,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'articles_analyzed': 0,
            'overall_sentiment': 'NEUTRAL',
            'average_polarity': 0.0,
            'average_impact': 0.0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'market_sentiment_distribution': {'bullish': 0, 'bearish': 0, 'neutral': 0},
            'trading_recommendation': {
                'action': 'HOLD',
                'reasoning': 'No recent news available for analysis',
                'risk_level': 'LOW',
                'confidence': 0.0,
                'impact_score': 0.0
            },
            'top_articles': [],
            'news_sources': []
        }

if __name__ == "__main__":
    # Test the news analyzer
    analyzer = NewsAnalyzer()
    
    print("🗞️ Testing Crypto News Analyzer...")
    print("=" * 50)
    
    # Test BTC news analysis
    btc_analysis = analyzer.analyze_crypto_news('BTC', hours_back=24)
    
    print(f"📊 BTC News Analysis:")
    print(f"Articles analyzed: {btc_analysis['articles_analyzed']}")
    print(f"Overall sentiment: {btc_analysis['overall_sentiment']}")
    print(f"Trading recommendation: {btc_analysis['trading_recommendation']['action']}")
    print(f"Confidence: {btc_analysis['trading_recommendation']['confidence']}%")
    
    if btc_analysis['top_articles']:
        print(f"\n📰 Top Article: {btc_analysis['top_articles'][0]['article']['title']}")
    
    print("\n✅ News analyzer test completed!") 