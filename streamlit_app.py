import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from crypto_analyzer import CryptoAnalyzer
from gold_analyzer import GoldAnalyzer
from vn_stock_analyzer import VNStockAnalyzer
from alert_system import AlertSystem
from news_analyzer import NewsAnalyzer
import threading
from translations import get_text, get_signal_translation, get_analysis_reason_translation

# Configure Streamlit page
st.set_page_config(
    page_title="🚀 Multi-Market Trading Alert System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .signal-long {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-short {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-neutral {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = CryptoAnalyzer()
    st.session_state.gold_analyzer = GoldAnalyzer()
    st.session_state.vn_stock_analyzer = VNStockAnalyzer()
    st.session_state.alert_system = AlertSystem()
    st.session_state.news_analyzer = NewsAnalyzer()
    st.session_state.monitoring = False
    st.session_state.last_update = None
    st.session_state.previous_interval = "5m"
    st.session_state.current_interval = "5m"
    st.session_state.analysis_cache = {}
    st.session_state.news_cache = {}
    st.session_state.language = "en"

def get_signal_color(signal):
    """Get color for signal display"""
    if 'LONG' in signal:
        return "#28a745"  # Green
    elif 'SHORT' in signal:
        return "#dc3545"  # Red
    else:
        return "#ffc107"  # Yellow

def format_signal_display(signal, strength=0, lang='en'):
    """Format signal for display with emojis"""
    emoji_map = {
        'STRONG_LONG': '🟢',
        'LONG': '🟢',
        'NEUTRAL': '🟡',
        'SHORT': '🔴',
        'STRONG_SHORT': '🔴'
    }
    translated_signal = get_signal_translation(signal, lang)
    strength_label = get_text('signal_strength_label', lang)
    return f"{emoji_map.get(signal, '⚪')} {translated_signal} ({strength_label}: {strength})"

def create_price_chart(df, symbol, interval="5m"):
    """Create interactive price chart with technical indicators"""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price & Moving Averages', 'RSI', 'MACD', 'Volume'),
        row_heights=[0.5, 0.2, 0.2, 0.1]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Moving averages
    if 'sma_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['sma_20'], name='SMA 20', line=dict(color='orange')),
            row=1, col=1
        )
    
    if 'ema_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['ema_20'], name='EMA 20', line=dict(color='red', width=2)),
            row=1, col=1
        )
    
    if 'sma_50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['sma_50'], name='SMA 50', line=dict(color='purple')),
            row=1, col=1
        )
    
    # Bollinger Bands
    if all(col in df.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_upper'], name='BB Upper',
                      line=dict(color='gray', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_lower'], name='BB Lower',
                      line=dict(color='gray', dash='dash'), fill='tonexty'),
            row=1, col=1
        )
    
    # RSI
    if 'rsi' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['rsi'], name='RSI', line=dict(color='blue')),
            row=2, col=1
        )
        # RSI overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    if all(col in df.columns for col in ['macd', 'macd_signal']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['macd_signal'], name='MACD Signal', line=dict(color='red')),
            row=3, col=1
        )
        if 'macd_histogram' in df.columns:
            fig.add_trace(
                go.Bar(x=df.index, y=df['macd_histogram'], name='MACD Histogram', opacity=0.3),
                row=3, col=1
            )
    
    # Volume
    fig.add_trace(
        go.Bar(x=df.index, y=df['volume'], name='Volume', opacity=0.5),
        row=4, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Technical Analysis ({interval})",
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=False
    )
    
    # Update y-axis for RSI
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    
    return fig

def get_news_sentiment_color(sentiment):
    """Get color for news sentiment display"""
    color_map = {
        'VERY_POSITIVE': '#28a745',
        'POSITIVE': '#28a745',
        'NEUTRAL': '#6c757d',
        'NEGATIVE': '#dc3545',
        'VERY_NEGATIVE': '#dc3545'
    }
    return color_map.get(sentiment, '#6c757d')

def get_news_sentiment_emoji(sentiment):
    """Get emoji for news sentiment"""
    emoji_map = {
        'VERY_POSITIVE': '🚀',
        'POSITIVE': '📈',
        'NEUTRAL': '⚖️',
        'NEGATIVE': '📉',
        'VERY_NEGATIVE': '💥'
    }
    return emoji_map.get(sentiment, '⚖️')

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_news_analysis(crypto_symbol, hours_back=12):
    """Get news analysis for crypto symbol with caching"""
    try:
        analyzer = NewsAnalyzer()
        return analyzer.analyze_crypto_news(crypto_symbol, hours_back=hours_back)
    except Exception as e:
        st.error(f"Error fetching news for {crypto_symbol}: {e}")
        return None

def display_news_analysis(crypto_symbol, lang='en'):
    """Display news analysis in the sidebar"""
    st.subheader(f"📰 {crypto_symbol} News Sentiment")
    
    with st.spinner("Fetching news..."):
        news_analysis = get_news_analysis(crypto_symbol, hours_back=12)
    
    if news_analysis and news_analysis['articles_analyzed'] > 0:
        sentiment = news_analysis['overall_sentiment']
        sentiment_color = get_news_sentiment_color(sentiment)
        sentiment_emoji = get_news_sentiment_emoji(sentiment)
        
        # Overall sentiment
        st.markdown(
            f"""
            <div style="background-color: {sentiment_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {sentiment_color}; margin-bottom: 1rem;">
                <h4 style="color: {sentiment_color}; margin: 0;">
                    {sentiment_emoji} {sentiment}
                </h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Key metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Articles", news_analysis['articles_analyzed'])
        with col2:
            st.metric("🎯 Confidence", f"{news_analysis['trading_recommendation']['confidence']:.1f}%")
        
        # Trading recommendation
        recommendation = news_analysis['trading_recommendation']
        action_color = '#28a745' if 'BUY' in recommendation['action'] else '#dc3545' if 'SELL' in recommendation['action'] else '#ffc107'
        
        st.markdown(
            f"""
            <div style="background-color: {action_color}20; padding: 0.5rem; border-radius: 0.25rem; margin: 0.5rem 0;">
                <strong style="color: {action_color};">🎯 {recommendation['action']}</strong><br>
                <small>{recommendation['reasoning']}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Sentiment distribution
        dist = news_analysis['sentiment_distribution']
        st.write("**📊 Sentiment Distribution:**")
        st.write(f"🟢 Positive: {dist['positive']} | 🔴 Negative: {dist['negative']} | 🟡 Neutral: {dist['neutral']}")
        
        # Top articles
        if news_analysis['top_articles']:
            st.write("**📰 Top Headlines:**")
            for i, article in enumerate(news_analysis['top_articles'][:3], 1):
                article_info = article['article']
                sentiment_info = article['sentiment']
                
                sentiment_emoji = "🟢" if sentiment_info['sentiment'] == 'positive' else "🔴" if sentiment_info['sentiment'] == 'negative' else "🟡"
                
                with st.expander(f"{sentiment_emoji} {article_info['title'][:60]}..."):
                    st.write(f"**Source:** {article_info['source']}")
                    st.write(f"**Published:** {article_info['published_date']}")
                    st.write(f"**Sentiment:** {sentiment_info['sentiment'].title()} (Score: {sentiment_info['polarity']})")
                    if article_info['summary']:
                        st.write(f"**Summary:** {article_info['summary'][:200]}...")
                    if article_info['link']:
                        st.markdown(f"[Read full article]({article_info['link']})")
        
        # News sources
        if news_analysis['news_sources']:
            st.write(f"**📰 Sources:** {', '.join(news_analysis['news_sources'])}")
    
    else:
        st.info(f"No recent news found for {crypto_symbol}")

def main():
    # Language selector (at the top)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        language = st.selectbox(
            "🌐 Language / Ngôn ngữ",
            ["English", "Tiếng Việt"],
            index=0 if st.session_state.language == "en" else 1
        )
        
        # Update language in session state
        new_lang = "en" if language == "English" else "vi"
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()
    
    lang = st.session_state.language
    
    # Header
    st.markdown(f'<h1 class="main-header">{get_text("app_title", lang)}</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header(get_text("settings", lang))
    
    # Monitoring controls
    st.sidebar.subheader(get_text("real_time_monitoring", lang))
    
    monitoring_button_text = get_text("start_monitoring", lang) if not st.session_state.monitoring else get_text("stop_monitoring", lang)
    if st.sidebar.button(monitoring_button_text):
        if not st.session_state.monitoring:
            st.session_state.monitoring = True
            st.sidebar.success(get_text("monitoring_started", lang))
        else:
            st.session_state.monitoring = False
            st.sidebar.info(get_text("monitoring_stopped", lang))
    
    # Manual refresh
    if st.sidebar.button(get_text("refresh_data", lang)):
        st.session_state.last_update = datetime.now()
        # Clear cache to force fresh data while keeping current interval
        st.session_state.analysis_cache = {}
        st.rerun()
    
    # Auto-refresh interval
    refresh_interval = st.sidebar.selectbox(
        get_text("auto_refresh_interval", lang),
        [30, 60, 300, 600, 900],
        index=2
    )
    
    # Settings
    st.sidebar.subheader(get_text("chart_settings", lang))
    show_technical_indicators = st.sidebar.checkbox(get_text("show_technical_indicators", lang), value=True)
    
    # Get current index for chart interval to maintain selection
    intervals = ["5m", "15m", "1h", "4h", "1d"]
    current_index = intervals.index(st.session_state.current_interval) if st.session_state.current_interval in intervals else 0
    
    chart_interval = st.sidebar.selectbox(get_text("chart_interval", lang), intervals, index=current_index)
    
    # Check if interval changed
    interval_changed = chart_interval != st.session_state.previous_interval
    if interval_changed:
        st.session_state.previous_interval = chart_interval
        st.session_state.current_interval = chart_interval
        st.session_state.analysis_cache = {}  # Clear cache when interval changes
    
    # Market selector
    st.subheader("📊 Market Selection")
    market_tabs = st.tabs(["📈 Cryptocurrency", "🥇 Gold Market", "🇻🇳 Vietnamese Stocks"])
    
    # Cryptocurrency Analysis Tab
    with market_tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(get_text("current_market_analysis", lang))
            
            # Get current analysis
            cache_key = f"crypto_analysis_{chart_interval}"
        
            # Use cached data if available and not stale (less than 1 minute old)
            # Don't use cache if user just clicked refresh (last_update is very recent)
            just_refreshed = (
                st.session_state.last_update and 
                (datetime.now() - st.session_state.last_update).seconds < 5
            )
            
            use_cache = (
                cache_key in st.session_state.analysis_cache and 
                not interval_changed and
                not just_refreshed and
                (datetime.now() - st.session_state.analysis_cache[cache_key]['timestamp']).seconds < 60
            )
        
            if use_cache:
                results = st.session_state.analysis_cache[cache_key]['data']
                st.info(get_text("using_cached_data", lang, interval=chart_interval))
            else:
                spinner_text = get_text("fetching_fresh_data", lang, interval=chart_interval) if just_refreshed else get_text("fetching_market_data", lang, interval=chart_interval)
                with st.spinner(spinner_text):
                    try:
                        results = st.session_state.analyzer.analyze_all_symbols(interval=chart_interval)
                        
                        # Cache the results
                        st.session_state.analysis_cache[cache_key] = {
                            'data': results,
                            'timestamp': datetime.now()
                        }
                    except Exception as e:
                        st.error(f"❌ Error connecting to market data: {str(e)}")
                        st.info("🔄 Please try refreshing the page or check your internet connection.")
                        # Use cached data if available, otherwise show empty results
                        if cache_key in st.session_state.analysis_cache:
                            results = st.session_state.analysis_cache[cache_key]['data']
                            st.warning("📊 Using cached data due to connection issues")
                        else:
                            results = {}
                    
                if interval_changed:
                    st.success(get_text("charts_updated", lang, interval=chart_interval))
                elif just_refreshed:
                    st.success(get_text("data_refreshed", lang, interval=chart_interval))
        
            if results:
                # Create tabs for each symbol
                tabs = st.tabs([symbol.replace('USDT', '/USDT') for symbol in results.keys()])
                
                for i, (symbol, data) in enumerate(results.items()):
                    with tabs[i]:
                        if 'error' in data:
                            st.error(f"❌ {get_text('error_fetching_data', lang, symbol=symbol, error=data['error'])}")
                            st.info("🔄 This might be due to temporary API issues. Please try again in a few minutes.")
                            # Show a placeholder with basic info
                            st.markdown("""
                            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid #6c757d;">
                                <h3 style="color: #6c757d; margin: 0;">⚠️ Data Unavailable</h3>
                                <p>Market data is temporarily unavailable. Please check back later.</p>
                            </div>
                            """, unsafe_allow_html=True)
                            continue
                        
                        analysis = data['analysis']
                        df = data.get('data', pd.DataFrame())
                        
                        # Signal display
                        signal_color = get_signal_color(analysis['signal'])
                        st.markdown(
                            f"""
                            <div style="background-color: {signal_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {signal_color}; margin-bottom: 1rem;">
                                <h3 style="color: {signal_color}; margin: 0;">
                                    {format_signal_display(analysis['signal'], analysis['strength'], lang)}
                                </h3>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Key metrics
                        metric_cols = st.columns(4)
                        with metric_cols[0]:
                            st.metric(get_text("current_price", lang), f"${analysis['current_price']:,.4f}")
                        with metric_cols[1]:
                            rsi_status = get_text("oversold", lang) if analysis['rsi'] < 30 else get_text("overbought", lang) if analysis['rsi'] > 70 else get_text("neutral_rsi", lang)
                            st.metric("📈 RSI", f"{analysis['rsi']:.2f}")
                        with metric_cols[2]:
                            st.metric("📊 MACD", f"{analysis['macd']:.6f}")
                        with metric_cols[3]:
                            st.metric(get_text("signal_strength", lang), analysis['strength'])
                        
                        # Add news sentiment indicator
                        crypto_symbol = symbol.replace('USDT', '')
                        if crypto_symbol in ['BTC', 'ETH']:
                            with st.spinner("Fetching news sentiment..."):
                                news_analysis = get_news_analysis(crypto_symbol, hours_back=12)
                            
                            if news_analysis and news_analysis['articles_analyzed'] > 0:
                                sentiment = news_analysis['overall_sentiment']
                                sentiment_color = get_news_sentiment_color(sentiment)
                                sentiment_emoji = get_news_sentiment_emoji(sentiment)
                                
                                news_cols = st.columns(3)
                                with news_cols[0]:
                                    st.markdown(f"""
                                    <div style="background-color: {sentiment_color}20; padding: 0.5rem; border-radius: 0.25rem; text-align: center; margin-top: 1rem;">
                                        <strong>📰 News Sentiment: <span style="color: {sentiment_color};">{sentiment_emoji} {sentiment}</span></strong>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with news_cols[1]:
                                    st.metric("📰 Articles", news_analysis['articles_analyzed'])
                                with news_cols[2]:
                                    st.metric("📊 Confidence", f"{news_analysis['trading_recommendation']['confidence']:.1f}%")
                        
                        # Entry and exit levels
                        if analysis['signal'] != 'NEUTRAL':
                            entry_cols = st.columns(3)
                            with entry_cols[0]:
                                st.metric(get_text("entry_price", lang), f"${analysis['entry_price']:,.4f}")
                            with entry_cols[1]:
                                if analysis['stop_loss'] > 0:
                                    st.metric(get_text("stop_loss", lang), f"${analysis['stop_loss']:,.4f}")
                            with entry_cols[2]:
                                if analysis['take_profit'] > 0:
                                    st.metric(get_text("take_profit", lang), f"${analysis['take_profit']:,.4f}")
                        
                        # Analysis reasons
                        st.subheader(get_text("analysis_details", lang))
                        for reason in analysis['reasons']:
                            translated_reason = get_analysis_reason_translation(reason, lang)
                            st.write(f"• {translated_reason}")
                        
                        # Combined analysis (technical + news)
                        crypto_symbol = symbol.replace('USDT', '')
                        if crypto_symbol in ['BTC', 'ETH'] and news_analysis and news_analysis['articles_analyzed'] > 0:
                            st.subheader("📊 Combined Analysis (Technical + News)")
                            
                            # Get news sentiment and technical signal
                            news_sentiment = news_analysis['overall_sentiment']
                            tech_signal = analysis['signal']
                            recommendation = news_analysis['trading_recommendation']['action']
                            
                            # Determine if signals align or conflict
                            aligned = (('LONG' in tech_signal and news_sentiment in ['VERY_POSITIVE', 'POSITIVE']) or
                                      ('SHORT' in tech_signal and news_sentiment in ['VERY_NEGATIVE', 'NEGATIVE']) or
                                      (tech_signal == 'NEUTRAL' and news_sentiment == 'NEUTRAL'))
                            
                            conflicted = (('LONG' in tech_signal and news_sentiment in ['VERY_NEGATIVE', 'NEGATIVE']) or
                                         ('SHORT' in tech_signal and news_sentiment in ['VERY_POSITIVE', 'POSITIVE']))
                            
                            if aligned:
                                st.success("✅ Technical analysis and news sentiment are aligned!")
                                st.markdown(f"""
                                <div style="background-color: #28a74520; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Recommendation:</strong> {recommendation} with increased confidence
                                </div>
                                """, unsafe_allow_html=True)
                            elif conflicted:
                                st.warning("⚠️ Technical analysis and news sentiment are conflicting!")
                                st.markdown(f"""
                                <div style="background-color: #ffc10720; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Recommendation:</strong> Exercise caution - consider waiting for alignment
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("ℹ️ Technical analysis and news sentiment provide mixed signals")
                                st.markdown(f"""
                                <div style="background-color: #17a2b820; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Recommendation:</strong> Consider both factors in your decision
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Technical chart
                        if show_technical_indicators and not df.empty:
                            st.subheader(f"{get_text('technical_analysis_chart', lang)} ({chart_interval})")
                            chart = create_price_chart(df, symbol.replace('USDT', '/USDT'), chart_interval)
                            st.plotly_chart(chart, use_container_width=True)

        with col2:
            st.subheader(get_text("alert_history", lang))
            
            # Load alert history
            try:
                alert_history = st.session_state.alert_system.get_alert_history(20)
                
                if alert_history:
                    for alert in reversed(alert_history[-10:]):  # Show last 10 alerts
                        symbol_clean = alert['symbol'].replace('USDT', '/USDT')
                        signal_color = get_signal_color(alert['signal'])
                        translated_signal = get_signal_translation(alert['signal'], lang)
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {signal_color}10; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; border-left: 3px solid {signal_color};">
                                <strong>{symbol_clean}</strong><br>
                                <span style="color: {signal_color};">{translated_signal}</span><br>
                                <small>{alert['timestamp']}</small><br>
                                <small>${alert['price']:,.4f}</small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info(get_text("no_alerts_yet", lang))
                    
            except Exception as e:
                st.error(get_text("error_loading_history", lang, error=str(e)))
            
            # System status
            st.subheader(get_text("system_status", lang))
            status_color = "#28a745" if st.session_state.monitoring else "#dc3545"
            status_text = get_text("active", lang) if st.session_state.monitoring else get_text("inactive", lang)
            last_update_text = st.session_state.last_update or get_text("never", lang)
            
            st.markdown(
                f"""
                <div style="background-color: {status_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {status_color};">
                    <strong>{get_text("monitoring_status", lang)}:</strong> {status_text}<br>
                    <strong>{get_text("chart_interval_status", lang)}:</strong> {chart_interval}<br>
                    <strong>{get_text("last_update", lang)}:</strong> {last_update_text}<br>
                    <strong>{get_text("symbols", lang)}:</strong> BTC/USDT, ETH/USDT
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add news analysis section
            st.markdown("---")
            
            # Create tabs for news analysis
            news_tabs = st.tabs(["📰 BTC News", "📰 ETH News"])
            
            with news_tabs[0]:
                display_news_analysis("BTC", lang)
                
            with news_tabs[1]:
                display_news_analysis("ETH", lang)
    
    # Gold Market Analysis Tab
    with market_tabs[1]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🥇 Gold Market Analysis")
            
            # Get current gold analysis
            gold_cache_key = f"gold_analysis_{chart_interval}"
        
            # Use cached data if available and not stale
            just_refreshed = (
                st.session_state.last_update and 
                (datetime.now() - st.session_state.last_update).seconds < 5
            )
            
            use_cache = (
                gold_cache_key in st.session_state.analysis_cache and 
                not interval_changed and
                not just_refreshed and
                (datetime.now() - st.session_state.analysis_cache[gold_cache_key]['timestamp']).seconds < 60
            )
        
            if use_cache:
                gold_results = st.session_state.analysis_cache[gold_cache_key]['data']
                st.info(f"📊 Using cached gold data ({chart_interval})")
            else:
                spinner_text = f"📊 Fetching fresh gold data ({chart_interval})..." if just_refreshed else f"📊 Fetching gold market data ({chart_interval})..."
                with st.spinner(spinner_text):
                    gold_results = st.session_state.gold_analyzer.analyze_all_symbols(interval=chart_interval)
                    
                    # Cache the results
                    st.session_state.analysis_cache[gold_cache_key] = {
                        'data': gold_results,
                        'timestamp': datetime.now()
                    }
                    
                if interval_changed:
                    st.success(f"✅ Gold charts updated to {chart_interval}")
                elif just_refreshed:
                    st.success(f"🔄 Gold data refreshed ({chart_interval})")
        
            if gold_results:
                # Create tabs for each gold symbol
                gold_symbol_names = {
                    'GC=F': '🥇 Gold Futures (GC=F)',
                    'GLD': '🥇 Gold ETF (GLD)'
                }
                gold_tabs = st.tabs([gold_symbol_names.get(symbol, symbol) for symbol in gold_results.keys()])
                
                for i, (symbol, data) in enumerate(gold_results.items()):
                    with gold_tabs[i]:
                        if 'error' in data:
                            st.error(f"❌ Error fetching data for {symbol}: {data['error']}")
                            continue
                        
                        analysis = data['analysis']
                        df = data.get('data', pd.DataFrame())
                        
                        # Signal display
                        signal_color = get_signal_color(analysis['signal'])
                        st.markdown(
                            f"""
                            <div style="background-color: {signal_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {signal_color}; margin-bottom: 1rem;">
                                <h3 style="color: {signal_color}; margin: 0;">
                                    🥇 {format_signal_display(analysis['signal'], analysis['strength'], lang)}
                                </h3>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Gold-specific metrics
                        metric_cols = st.columns(5)
                        with metric_cols[0]:
                            st.metric("💰 Current Price", f"${analysis['current_price']:,.2f}")
                        with metric_cols[1]:
                            rsi_val = analysis['rsi']
                            rsi_status = "Oversold" if rsi_val < 25 else "Overbought" if rsi_val > 75 else "Neutral"
                            st.metric("📈 RSI", f"{rsi_val:.2f}", help=f"Gold RSI thresholds: <25 oversold, >75 overbought")
                        with metric_cols[2]:
                            st.metric("📊 MACD", f"{analysis['macd']:.6f}")
                        with metric_cols[3]:
                            if 'cci' in analysis:
                                st.metric("📈 CCI", f"{analysis['cci']:.2f}", help="Commodity Channel Index")
                        with metric_cols[4]:
                            st.metric("🎯 Signal Strength", analysis['strength'])
                        
                        # Add gold news sentiment
                        with st.spinner("Fetching gold news sentiment..."):
                            gold_news = get_news_analysis('GOLD', hours_back=12)
                        
                        if gold_news and gold_news['articles_analyzed'] > 0:
                            sentiment = gold_news['overall_sentiment']
                            sentiment_color = get_news_sentiment_color(sentiment)
                            sentiment_emoji = get_news_sentiment_emoji(sentiment)
                            
                            news_cols = st.columns(3)
                            with news_cols[0]:
                                st.markdown(f"""
                                <div style="background-color: {sentiment_color}20; padding: 0.5rem; border-radius: 0.25rem; text-align: center; margin-top: 1rem;">
                                    <strong>📰 Gold News Sentiment: <span style="color: {sentiment_color};">{sentiment_emoji} {sentiment}</span></strong>
                                </div>
                                """, unsafe_allow_html=True)
                            with news_cols[1]:
                                st.metric("📰 Articles", gold_news['articles_analyzed'])
                            with news_cols[2]:
                                st.metric("📊 Confidence", f"{gold_news['trading_recommendation']['confidence']:.1f}%")
                        
                        # Entry and exit levels for gold
                        if analysis['signal'] != 'NEUTRAL':
                            entry_cols = st.columns(3)
                            with entry_cols[0]:
                                st.metric("🎯 Entry Price", f"${analysis['entry_price']:,.2f}")
                            with entry_cols[1]:
                                if analysis['stop_loss'] > 0:
                                    st.metric("🛑 Stop Loss", f"${analysis['stop_loss']:,.2f}")
                            with entry_cols[2]:
                                if analysis['take_profit'] > 0:
                                    st.metric("🎯 Take Profit", f"${analysis['take_profit']:,.2f}")
                        
                        # Gold-specific indicators
                        if any(key in analysis for key in ['atr', 'cci', 'donchian_upper', 'donchian_lower']):
                            st.subheader("📊 Gold-Specific Indicators")
                            gold_indicator_cols = st.columns(4)
                            
                            if 'atr' in analysis:
                                with gold_indicator_cols[0]:
                                    st.metric("📊 ATR", f"{analysis['atr']:.2f}", help="Average True Range - Volatility measure")
                            
                            if 'cci' in analysis:
                                with gold_indicator_cols[1]:
                                    cci_val = analysis['cci']
                                    cci_status = "Oversold" if cci_val < -100 else "Overbought" if cci_val > 100 else "Neutral"
                                    st.metric("📈 CCI", f"{cci_val:.2f}", help=f"Commodity Channel Index: {cci_status}")
                            
                            if 'donchian_upper' in analysis and 'donchian_lower' in analysis:
                                with gold_indicator_cols[2]:
                                    st.metric("📈 Donchian High", f"${analysis['donchian_upper']:,.2f}")
                                with gold_indicator_cols[3]:
                                    st.metric("📉 Donchian Low", f"${analysis['donchian_lower']:,.2f}")
                        
                        # Analysis reasons
                        st.subheader("📋 Analysis Details")
                        for reason in analysis['reasons']:
                            st.write(f"• {reason}")
                        
                        # Combined gold analysis (technical + news)
                        if gold_news and gold_news['articles_analyzed'] > 0:
                            st.subheader("📊 Combined Gold Analysis (Technical + News)")
                            
                            # Get news sentiment and technical signal
                            news_sentiment = gold_news['overall_sentiment']
                            tech_signal = analysis['signal']
                            recommendation = gold_news['trading_recommendation']['action']
                            
                            # Determine if signals align or conflict
                            aligned = (('LONG' in tech_signal and news_sentiment in ['VERY_POSITIVE', 'POSITIVE']) or
                                      ('SHORT' in tech_signal and news_sentiment in ['VERY_NEGATIVE', 'NEGATIVE']) or
                                      (tech_signal == 'NEUTRAL' and news_sentiment == 'NEUTRAL'))
                            
                            conflicted = (('LONG' in tech_signal and news_sentiment in ['VERY_NEGATIVE', 'NEGATIVE']) or
                                         ('SHORT' in tech_signal and news_sentiment in ['VERY_POSITIVE', 'POSITIVE']))
                            
                            if aligned:
                                st.success("✅ Gold technical analysis and news sentiment are aligned!")
                                st.markdown(f"""
                                <div style="background-color: #28a74520; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Gold Recommendation:</strong> {recommendation} with increased confidence
                                </div>
                                """, unsafe_allow_html=True)
                            elif conflicted:
                                st.warning("⚠️ Gold technical analysis and news sentiment are conflicting!")
                                st.markdown(f"""
                                <div style="background-color: #ffc10720; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Gold Recommendation:</strong> Exercise caution - wait for alignment
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("ℹ️ Gold technical and news signals provide mixed information")
                                st.markdown(f"""
                                <div style="background-color: #17a2b820; padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                                    <strong>Technical Signal:</strong> {tech_signal}<br>
                                    <strong>News Sentiment:</strong> {news_sentiment}<br>
                                    <strong>Gold Recommendation:</strong> Consider both technical and fundamental factors
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Technical chart for gold
                        if show_technical_indicators and not df.empty:
                            st.subheader(f"📊 Gold Technical Chart ({chart_interval})")
                            # Create gold-specific chart title
                            gold_name = "Gold Futures" if symbol == "GC=F" else "Gold ETF"
                            chart = create_price_chart(df, f"{gold_name} ({symbol})", chart_interval)
                            st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("⚠️ No gold market data available. Check your internet connection.")

        with col2:
            st.subheader("🥇 Gold Alert History")
            
            # Load gold-specific alert history
            try:
                alert_history = st.session_state.alert_system.get_alert_history(20)
                gold_alerts = [alert for alert in alert_history if alert['symbol'] in ['GC=F', 'GLD']]
                
                if gold_alerts:
                    for alert in reversed(gold_alerts[-10:]):  # Show last 10 gold alerts
                        symbol_clean = f"🥇 {alert['symbol']}"
                        signal_color = get_signal_color(alert['signal'])
                        translated_signal = get_signal_translation(alert['signal'], lang)
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {signal_color}10; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; border-left: 3px solid {signal_color};">
                                <strong>{symbol_clean}</strong><br>
                                <span style="color: {signal_color};">{translated_signal}</span><br>
                                <small>{alert['timestamp']}</small><br>
                                <small>${alert['price']:,.2f}</small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("📭 No gold alerts yet")
                    
            except Exception as e:
                st.error(f"❌ Error loading gold alert history: {str(e)}")
            
            # Gold system status
            st.subheader("🥇 Gold System Status")
            status_color = "#28a745" if st.session_state.monitoring else "#dc3545"
            status_text = get_text("active", lang) if st.session_state.monitoring else get_text("inactive", lang)
            last_update_text = st.session_state.last_update or get_text("never", lang)
            
            st.markdown(
                f"""
                <div style="background-color: {status_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {status_color};">
                    <strong>🥇 Gold Monitoring:</strong> {status_text}<br>
                    <strong>📊 Chart Interval:</strong> {chart_interval}<br>
                    <strong>🔄 Last Update:</strong> {last_update_text}<br>
                    <strong>📈 Gold Symbols:</strong> GC=F Futures, GLD ETF<br>
                    <strong>📰 News Sources:</strong> MarketWatch, Kitco News
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add gold news analysis section
            st.markdown("---")
            st.subheader("📰 Gold Market News")
            display_news_analysis("GOLD", lang)
    
    # Vietnamese Stocks Analysis Tab
    with market_tabs[2]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🇻🇳 Vietnamese Stock Market Analysis")
            
            # Stock selection
            vn_analyzer = st.session_state.vn_stock_analyzer
            stock_options = ["ALL"] + list(vn_analyzer.vn_stocks.keys())
            
            # Stock selector
            selected_stocks = st.multiselect(
                "📈 Select Vietnamese Stocks to Analyze",
                options=stock_options,
                default=["ALL"] if "ALL" in stock_options else stock_options[:5],
                help="Select specific stocks or 'ALL' for top performers"
            )
            
            # Number of stocks limit when ALL is selected
            if "ALL" in selected_stocks:
                stock_limit = st.slider("Number of stocks to analyze", 5, 15, 8)
                selected_stocks = ["ALL"]
            else:
                stock_limit = len(selected_stocks)
            
            # Get current Vietnamese stock analysis
            vn_cache_key = f"vn_analysis_{chart_interval}_{'-'.join(selected_stocks)}_{stock_limit}"
        
            # Use cached data if available and not stale
            just_refreshed = (
                st.session_state.last_update and 
                (datetime.now() - st.session_state.last_update).seconds < 5
            )
            
            use_cache = (
                vn_cache_key in st.session_state.analysis_cache and 
                not interval_changed and
                not just_refreshed and
                (datetime.now() - st.session_state.analysis_cache[vn_cache_key]['timestamp']).seconds < 60
            )
        
            if use_cache:
                vn_results = st.session_state.analysis_cache[vn_cache_key]['data']
                st.info(f"📊 Using cached Vietnamese stock data ({chart_interval})")
            else:
                spinner_text = f"📊 Fetching fresh Vietnamese stock data ({chart_interval})..." if just_refreshed else f"📊 Fetching Vietnamese stock data ({chart_interval})..."
                with st.spinner(spinner_text):
                    if "ALL" in selected_stocks:
                        vn_results = vn_analyzer.analyze_all_symbols(interval=chart_interval, limit=stock_limit)
                    else:
                        vn_results = {}
                        for stock in selected_stocks:
                            if stock != "ALL":
                                result = vn_analyzer.analyze_symbol(stock, interval=chart_interval)
                                vn_results[stock] = result
                    
                    # Cache the results
                    st.session_state.analysis_cache[vn_cache_key] = {
                        'data': vn_results,
                        'timestamp': datetime.now()
                    }
                    
                if interval_changed:
                    st.success(f"✅ Vietnamese stock charts updated to {chart_interval}")
                elif just_refreshed:
                    st.success(f"🔄 Vietnamese stock data refreshed ({chart_interval})")
        
            if vn_results:
                # Sort results by signal strength
                sorted_vn_results = sorted(
                    [(symbol, data) for symbol, data in vn_results.items() if 'analysis' in data],
                    key=lambda x: x[1]['analysis']['strength'],
                    reverse=True
                )
                
                # Create tabs for each Vietnamese stock
                if sorted_vn_results:
                    vn_stock_names = []
                    for symbol, data in sorted_vn_results:
                        company_name = data['analysis'].get('company_name', symbol)
                        signal = data['analysis']['signal']
                        strength = data['analysis']['strength']
                        
                        # Add signal emoji
                        if 'LONG' in signal:
                            emoji = "📈"
                        elif 'SHORT' in signal:
                            emoji = "📉"
                        else:
                            emoji = "➡️"
                        
                        vn_stock_names.append(f"{emoji} {company_name} ({strength})")
                    
                    vn_tabs = st.tabs(vn_stock_names)
                    
                    for i, (symbol, data) in enumerate(sorted_vn_results):
                        with vn_tabs[i]:
                            if 'error' in data:
                                st.error(f"❌ Error fetching data for {symbol}: {data['error']}")
                                continue
                            
                            analysis = data['analysis']
                            df = data.get('data', pd.DataFrame())
                            
                            # Signal display
                            signal_color = get_signal_color(analysis['signal'])
                            st.markdown(
                                f"""
                                <div style="background-color: {signal_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {signal_color}; margin-bottom: 1rem;">
                                    <h3 style="color: {signal_color}; margin: 0;">
                                        🇻🇳 {format_signal_display(analysis['signal'], analysis['strength'], lang)}
                                    </h3>
                                    <p style="margin: 0.5rem 0 0 0; color: #666;">{analysis['company_name']} ({symbol})</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Vietnamese stock-specific metrics
                            metric_cols = st.columns(7)
                            with metric_cols[0]:
                                st.metric("💰 Current Price", f"{analysis['current_price']:,.1f}K VND")
                            with metric_cols[1]:
                                rsi_val = analysis['rsi']
                                rsi_status = "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral"
                                st.metric("📈 RSI", f"{rsi_val:.1f}", help=f"Status: {rsi_status}")
                            with metric_cols[2]:
                                st.metric("📊 MACD", f"{analysis['macd']:.4f}")
                            with metric_cols[3]:
                                # EMA20 with trend indication
                                if 'ema_20' in analysis:
                                    ema_trend = "📈" if analysis['current_price'] > analysis['ema_20'] else "📉"
                                    st.metric("📊 EMA20", f"{analysis['ema_20']:,.1f}K", help=f"{ema_trend} Price vs EMA20")
                            with metric_cols[4]:
                                st.metric("📊 ATR", f"{analysis['atr']:.2f}")
                            with metric_cols[5]:
                                if 'volume_ratio' in analysis:
                                    volume_color = "🟢" if analysis['volume_ratio'] > 1.2 else "🔴" if analysis['volume_ratio'] < 0.8 else "🟡"
                                    st.metric("📊 Volume", f"{analysis['volume_ratio']:.2f}x", help=f"{volume_color} Volume vs average")
                            with metric_cols[6]:
                                st.metric("🎯 Signal Strength", f"{analysis['strength']}/10")
                            
                            # Additional Vietnamese market indicators
                            if any(key in analysis for key in ['mfi', 'bullish_score', 'bearish_score']):
                                st.subheader("📊 Vietnamese Market Indicators")
                                vn_indicator_cols = st.columns(3)
                                
                                if 'mfi' in analysis and analysis['mfi'] > 0:
                                    with vn_indicator_cols[0]:
                                        mfi_val = analysis['mfi']
                                        mfi_status = "Oversold" if mfi_val < 20 else "Overbought" if mfi_val > 80 else "Neutral"
                                        st.metric("💰 Money Flow Index", f"{mfi_val:.1f}", help=f"Status: {mfi_status}")
                                
                                if 'bullish_score' in analysis and 'bearish_score' in analysis:
                                    with vn_indicator_cols[1]:
                                        st.metric("📈 Bullish Score", analysis['bullish_score'])
                                    with vn_indicator_cols[2]:
                                        st.metric("📉 Bearish Score", analysis['bearish_score'])
                            
                            # Entry and exit levels for Vietnamese stocks
                            if analysis['signal'] != 'NEUTRAL':
                                entry_cols = st.columns(3)
                                with entry_cols[0]:
                                    st.metric("🎯 Entry Price", f"{analysis['entry_price']:,.1f}K VND")
                                with entry_cols[1]:
                                    if analysis['stop_loss'] > 0:
                                        st.metric("🛑 Stop Loss", f"{analysis['stop_loss']:,.1f}K VND")
                                with entry_cols[2]:
                                    if analysis['take_profit'] > 0:
                                        st.metric("🎯 Take Profit", f"{analysis['take_profit']:,.1f}K VND")
                            
                            # Analysis reasons
                            st.subheader("📋 Analysis Details")
                            for reason in analysis['reasons']:
                                st.write(f"• {reason}")
                            
                            # Technical chart for Vietnamese stocks
                            if show_technical_indicators and not df.empty:
                                st.subheader(f"📊 {analysis['company_name']} Technical Chart ({chart_interval})")
                                chart = create_price_chart(df, f"{analysis['company_name']} ({symbol})", chart_interval)
                                st.plotly_chart(chart, use_container_width=True)
                else:
                    st.warning("⚠️ No Vietnamese stock analysis available.")
            else:
                st.warning("⚠️ No Vietnamese stock data available. Check your internet connection.")

        with col2:
            st.subheader("🇻🇳 Vietnamese Stock Alerts")
            
            # Load Vietnamese stock-specific alert history
            try:
                alert_history = st.session_state.alert_system.get_alert_history(20)
                vn_stock_symbols = list(st.session_state.vn_stock_analyzer.vn_stocks.keys())
                vn_alerts = [alert for alert in alert_history if alert['symbol'] in vn_stock_symbols]
                
                if vn_alerts:
                    for alert in reversed(vn_alerts[-10:]):  # Show last 10 Vietnamese stock alerts
                        symbol_clean = f"🇻🇳 {alert['symbol']}"
                        signal_color = get_signal_color(alert['signal'])
                        translated_signal = get_signal_translation(alert['signal'], lang)
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {signal_color}10; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; border-left: 3px solid {signal_color};">
                                <strong>{symbol_clean}</strong><br>
                                <span style="color: {signal_color};">{translated_signal}</span><br>
                                <small>{alert['timestamp']}</small><br>
                                <small>{alert['price']:,.1f}K VND</small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("📭 No Vietnamese stock alerts yet")
                    
            except Exception as e:
                st.error(f"❌ Error loading Vietnamese stock alert history: {str(e)}")
            
            # Vietnamese stock system status
            st.subheader("🇻🇳 Vietnamese Stock System")
            status_color = "#28a745" if st.session_state.monitoring else "#dc3545"
            status_text = get_text("active", lang) if st.session_state.monitoring else get_text("inactive", lang)
            last_update_text = st.session_state.last_update or get_text("never", lang)
            
            st.markdown(
                f"""
                <div style="background-color: {status_color}20; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {status_color};">
                    <strong>🇻🇳 VN Stock Monitoring:</strong> {status_text}<br>
                    <strong>📊 Chart Interval:</strong> {chart_interval}<br>
                    <strong>🔄 Last Update:</strong> {last_update_text}<br>
                    <strong>📈 Total Stocks:</strong> {len(st.session_state.vn_stock_analyzer.vn_stocks)}<br>
                    <strong>🏢 Markets:</strong> HSX, HNX Exchanges<br>
                    <strong>💱 Currency:</strong> Vietnamese Dong (VND)
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Vietnamese stock market overview
            st.markdown("---")
            st.subheader("📊 Market Overview")
            
            # Show top Vietnamese stocks
            if vn_results:
                st.write("**📈 Top Performers:**")
                top_stocks = sorted(
                    [(symbol, data) for symbol, data in vn_results.items() 
                     if 'analysis' in data and 'LONG' in data['analysis']['signal']],
                    key=lambda x: x[1]['analysis']['strength'],
                    reverse=True
                )[:3]
                
                if top_stocks:
                    for symbol, data in top_stocks:
                        analysis = data['analysis']
                        st.write(f"• **{analysis['company_name']}** ({symbol}): {analysis['signal']} ({analysis['strength']}/10)")
                else:
                    st.write("No bullish signals currently")
    
    # Auto-refresh
    if st.session_state.monitoring:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main() 