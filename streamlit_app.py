import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from crypto_analyzer import CryptoAnalyzer
from alert_system import AlertSystem
import threading
from translations import get_text, get_signal_translation, get_analysis_reason_translation

# Configure Streamlit page
st.set_page_config(
    page_title="🚀 Crypto Trading Alert System",
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
    st.session_state.alert_system = AlertSystem()
    st.session_state.monitoring = False
    st.session_state.last_update = None
    st.session_state.previous_interval = "5m"
    st.session_state.current_interval = "5m"
    st.session_state.analysis_cache = {}
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
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(get_text("current_market_analysis", lang))
        
        # Get current analysis
        cache_key = f"analysis_{chart_interval}"
        
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
                results = st.session_state.analyzer.analyze_all_symbols(interval=chart_interval)
                
                # Cache the results
                st.session_state.analysis_cache[cache_key] = {
                    'data': results,
                    'timestamp': datetime.now()
                }
                
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
                        st.error(get_text("error_fetching_data", lang, symbol=symbol, error=data['error']))
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
    
    # Auto-refresh
    if st.session_state.monitoring:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main() 