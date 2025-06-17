"""
Multi-language translation system for Crypto Trading Alert System
Supports English and Vietnamese
"""

TRANSLATIONS = {
    'en': {
        # Main titles
        'app_title': '🚀 Crypto Trading Alert System',
        'crypto_analyzer': '🚀 CRYPTO TRADING ANALYZER 🚀',
        'system_startup': '🚀 Crypto Trading Alert System',
        
        # Menu and navigation
        'settings': '⚙️ Settings',
        'real_time_monitoring': '🔄 Real-time Monitoring',
        'chart_settings': '📊 Chart Settings',
        'current_market_analysis': '📈 Current Market Analysis',
        'alert_history': '🚨 Alert History',
        'system_status': '📊 System Status',
        
        # Buttons and controls
        'start_monitoring': '▶️ Start Monitoring',
        'stop_monitoring': '⏹️ Stop Monitoring',
        'refresh_data': '🔄 Refresh Data',
        'show_technical_indicators': 'Show Technical Indicators',
        'chart_interval': 'Chart Interval',
        'auto_refresh_interval': 'Auto-refresh interval (seconds)',
        'language': '🌐 Language',
        
        # Analysis sections
        'analysis_details': '📋 Analysis Details',
        'technical_analysis_chart': '📊 Technical Analysis Chart',
        'trading_levels': '🎯 TRADING LEVELS',
        'recommendation': '🎯 RECOMMENDATION',
        
        # Metrics
        'current_price': '💰 Current Price',
        'signal_strength': '🎯 Signal Strength',
        'entry_price': '🎯 Entry Price',
        'stop_loss': '🛑 Stop Loss',
        'take_profit': '🎯 Take Profit',
        
        # Signals
        'STRONG_LONG': 'STRONG_LONG',
        'LONG': 'LONG',
        'NEUTRAL': 'NEUTRAL',
        'SHORT': 'SHORT',
        'STRONG_SHORT': 'STRONG_SHORT',
        
        # Signal descriptions
        'signal_strength_label': 'Strength',
        'oversold': 'Oversold',
        'overbought': 'Overbought',
        'neutral_rsi': 'Neutral',
        
        # Recommendations
        'buy_long': 'BUY/LONG',
        'sell_short': 'SELL/SHORT',
        'hold_wait': 'HOLD/WAIT',
        'risk_level': 'Risk Level',
        'suggested_action': 'Suggested Action',
        'current_sentiment': 'Current Sentiment',
        
        # Risk levels
        'risk_high': 'HIGH',
        'risk_medium': 'MEDIUM',
        'risk_low': 'LOW',
        
        # Actions
        'consider_long_position': 'Consider opening a long position',
        'consider_short_position': 'Consider opening a short position',
        'wait_for_signals': 'Wait for clearer signals',
        
        # Sentiments
        'bullish_momentum': 'Bullish momentum detected',
        'bearish_momentum': 'Bearish momentum detected',
        'market_consolidating': 'Market is consolidating',
        
        # Status messages
        'monitoring_started': 'Monitoring started!',
        'monitoring_stopped': 'Monitoring stopped!',
        'monitoring_status': 'Monitoring Status',
        'chart_interval_status': 'Chart Interval',
        'last_update': 'Last Update',
        'symbols': 'Symbols',
        'active': '🟢 Active',
        'inactive': '🔴 Inactive',
        'never': 'Never',
        
        # Cache and loading
        'using_cached_data': '📊 Using cached data for {interval} timeframe',
        'fetching_market_data': 'Fetching market data for {interval} timeframe...',
        'fetching_fresh_data': 'Fetching fresh market data for {interval} timeframe...',
        'charts_updated': '📈 Charts updated to {interval} timeframe!',
        'data_refreshed': '🔄 Data refreshed for {interval} timeframe!',
        
        # Alerts and errors
        'no_alerts_yet': 'No alerts yet. Start monitoring to see alerts here.',
        'error_loading_history': 'Error loading alert history: {error}',
        'error_fetching_data': '❌ Error fetching data for {symbol}: {error}',
        'failed_to_fetch': '❌ Failed to fetch market data',
        'error_occurred': '❌ Error: {error}',
        'check_connection': 'Make sure you have internet connection and all dependencies installed',
        
        # Analysis reasons
        'rsi_oversold_long': 'RSI Oversold - Potential Long',
        'rsi_overbought_short': 'RSI Overbought - Potential Short',
        'macd_bullish_crossover': 'MACD Bullish Crossover - Long Signal',
        'macd_bearish_crossover': 'MACD Bearish Crossover - Short Signal',
        'price_above_ma_bullish': 'Price Above Moving Averages - Bullish',
        'price_below_ma_bearish': 'Price Below Moving Averages - Bearish',
        'ema_golden_cross': 'EMA Golden Cross - Strong Long',
        'ema_death_cross': 'EMA Death Cross - Strong Short',
        'bb_oversold': 'Price Below Lower Bollinger Band - Oversold',
        'bb_overbought': 'Price Above Upper Bollinger Band - Overbought',
        'stoch_oversold': 'Stochastic Oversold - Long Signal',
        'stoch_overbought': 'Stochastic Overbought - Short Signal',
        'williams_oversold': 'Williams %R Oversold - Long Signal',
        'williams_overbought': 'Williams %R Overbought - Short Signal',
        'no_clear_signals': 'No clear signals',
        'insufficient_data': 'Insufficient data',
        
        # Footer messages
        'analysis_completed': '📊 Analysis completed at {timestamp} ({interval} timeframe)',
        'educational_purpose': '⚠️  This is for educational purposes only. Not financial advice!',
        'run_again': '🔄 Run again: python quick_analysis.py [interval]',
        'available_intervals': 'Available intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M',
        'example_usage': 'Example: python quick_analysis.py 1h',
        'web_interface': '🌐 Web interface: streamlit run streamlit_app.py',
        'real_time_alerts': '🚨 Real-time alerts: python alert_system.py',
        
        # Command line
        'analyzing_symbols': 'Analyzing BTC and ETH on {interval} timeframe using Binance API...',
        'fetching_data': 'Fetching market data for {interval} interval...',
        'analysis_interrupted': 'Analysis interrupted by user',
        'invalid_interval': 'Invalid interval. Using default 5m',
        'monitoring_stopped_user': 'Monitoring stopped by user',
        'starting_monitoring': 'Starting continuous monitoring (checking every {interval} seconds)',
        'error_in_monitoring': 'Error in monitoring loop: {error}',
    },
    
    'vi': {
        # Main titles
        'app_title': '🚀 Hệ Thống Cảnh Báo Giao Dịch Crypto',
        'crypto_analyzer': '🚀 PHÂN TÍCH GIAO DỊCH CRYPTO 🚀',
        'system_startup': '🚀 Hệ Thống Cảnh Báo Giao Dịch Crypto',
        
        # Menu and navigation
        'settings': '⚙️ Cài Đặt',
        'real_time_monitoring': '🔄 Giám Sát Thời Gian Thực',
        'chart_settings': '📊 Thiết Lập Biểu Đồ',
        'current_market_analysis': '📈 Phân Tích Thị Trường Hiện Tại',
        'alert_history': '🚨 Lịch Sử Cảnh Báo',
        'system_status': '📊 Trạng Thái Hệ Thống',
        
        # Buttons and controls
        'start_monitoring': '▶️ Bắt Đầu Giám Sát',
        'stop_monitoring': '⏹️ Dừng Giám Sát',
        'refresh_data': '🔄 Làm Mới Dữ Liệu',
        'show_technical_indicators': 'Hiển Thị Chỉ Báo Kỹ Thuật',
        'chart_interval': 'Khung Thời Gian Biểu Đồ',
        'auto_refresh_interval': 'Khoảng thời gian tự động làm mới (giây)',
        'language': '🌐 Ngôn Ngữ',
        
        # Analysis sections
        'analysis_details': '📋 Chi Tiết Phân Tích',
        'technical_analysis_chart': '📊 Biểu Đồ Phân Tích Kỹ Thuật',
        'trading_levels': '🎯 MỨC GIA GIAO DỊCH',
        'recommendation': '🎯 KHUYẾN NGHỊ',
        
        # Metrics
        'current_price': '💰 Giá Hiện Tại',
        'signal_strength': '🎯 Độ Mạnh Tín Hiệu',
        'entry_price': '🎯 Giá Vào Lệnh',
        'stop_loss': '🛑 Cắt Lỗ',
        'take_profit': '🎯 Chốt Lời',
        
        # Signals
        'STRONG_LONG': 'MUA MẠNH',
        'LONG': 'MUA',
        'NEUTRAL': 'TRUNG TÍNH',
        'SHORT': 'BÁN',
        'STRONG_SHORT': 'BÁN MẠNH',
        
        # Signal descriptions
        'signal_strength_label': 'Độ Mạnh',
        'oversold': 'Quá Bán',
        'overbought': 'Quá Mua',
        'neutral_rsi': 'Trung Tính',
        
        # Recommendations
        'buy_long': 'MUA/LONG',
        'sell_short': 'BÁN/SHORT',
        'hold_wait': 'GIỮ/CHỜ',
        'risk_level': 'Mức Độ Rủi Ro',
        'suggested_action': 'Hành Động Đề Xuất',
        'current_sentiment': 'Tâm Lý Thị Trường',
        
        # Risk levels
        'risk_high': 'CAO',
        'risk_medium': 'TRUNG BÌNH',
        'risk_low': 'THẤP',
        
        # Actions
        'consider_long_position': 'Cân nhắc mở lệnh mua',
        'consider_short_position': 'Cân nhắc mở lệnh bán',
        'wait_for_signals': 'Đợi tín hiệu rõ ràng hơn',
        
        # Sentiments
        'bullish_momentum': 'Phát hiện động lực tăng giá',
        'bearish_momentum': 'Phát hiện động lực giảm giá',
        'market_consolidating': 'Thị trường đang tích lũy',
        
        # Status messages
        'monitoring_started': 'Đã bắt đầu giám sát!',
        'monitoring_stopped': 'Đã dừng giám sát!',
        'monitoring_status': 'Trạng Thái Giám Sát',
        'chart_interval_status': 'Khung Thời Gian',
        'last_update': 'Cập Nhật Cuối',
        'symbols': 'Cặp Giao Dịch',
        'active': '🟢 Hoạt Động',
        'inactive': '🔴 Không Hoạt Động',
        'never': 'Chưa Bao Giờ',
        
        # Cache and loading
        'using_cached_data': '📊 Sử dụng dữ liệu đã lưu cho khung {interval}',
        'fetching_market_data': 'Đang tải dữ liệu thị trường cho khung {interval}...',
        'fetching_fresh_data': 'Đang tải dữ liệu mới cho khung {interval}...',
        'charts_updated': '📈 Biểu đồ đã cập nhật sang khung {interval}!',
        'data_refreshed': '🔄 Dữ liệu đã làm mới cho khung {interval}!',
        
        # Alerts and errors
        'no_alerts_yet': 'Chưa có cảnh báo nào. Bắt đầu giám sát để xem cảnh báo tại đây.',
        'error_loading_history': 'Lỗi tải lịch sử cảnh báo: {error}',
        'error_fetching_data': '❌ Lỗi tải dữ liệu cho {symbol}: {error}',
        'failed_to_fetch': '❌ Không thể tải dữ liệu thị trường',
        'error_occurred': '❌ Lỗi: {error}',
        'check_connection': 'Kiểm tra kết nối internet và cài đặt các thư viện cần thiết',
        
        # Analysis reasons
        'rsi_oversold_long': 'RSI Quá Bán - Có Thể Mua',
        'rsi_overbought_short': 'RSI Quá Mua - Có Thể Bán',
        'macd_bullish_crossover': 'MACD Cắt Tăng - Tín Hiệu Mua',
        'macd_bearish_crossover': 'MACD Cắt Giảm - Tín Hiệu Bán',
        'price_above_ma_bullish': 'Giá Trên Đường MA - Tăng Giá',
        'price_below_ma_bearish': 'Giá Dưới Đường MA - Giảm Giá',
        'ema_golden_cross': 'EMA Golden Cross - Mua Mạnh',
        'ema_death_cross': 'EMA Death Cross - Bán Mạnh',
        'bb_oversold': 'Giá Dưới Bollinger Dưới - Quá Bán',
        'bb_overbought': 'Giá Trên Bollinger Trên - Quá Mua',
        'stoch_oversold': 'Stochastic Quá Bán - Tín Hiệu Mua',
        'stoch_overbought': 'Stochastic Quá Mua - Tín Hiệu Bán',
        'williams_oversold': 'Williams %R Quá Bán - Tín Hiệu Mua',
        'williams_overbought': 'Williams %R Quá Mua - Tín Hiệu Bán',
        'no_clear_signals': 'Không có tín hiệu rõ ràng',
        'insufficient_data': 'Dữ liệu không đủ',
        
        # Footer messages
        'analysis_completed': '📊 Phân tích hoàn thành lúc {timestamp} (khung {interval})',
        'educational_purpose': '⚠️  Chỉ mang tính chất giáo dục. Không phải lời khuyên đầu tư!',
        'run_again': '🔄 Chạy lại: python quick_analysis.py [interval]',
        'available_intervals': 'Khung thời gian có sẵn: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M',
        'example_usage': 'Ví dụ: python quick_analysis.py 1h',
        'web_interface': '🌐 Giao diện web: streamlit run streamlit_app.py',
        'real_time_alerts': '🚨 Cảnh báo thời gian thực: python alert_system.py',
        
        # Command line
        'analyzing_symbols': 'Đang phân tích BTC và ETH trên khung {interval} qua Binance API...',
        'fetching_data': 'Đang tải dữ liệu thị trường cho khung {interval}...',
        'analysis_interrupted': 'Phân tích bị ngắt bởi người dùng',
        'invalid_interval': 'Khung thời gian không hợp lệ. Sử dụng mặc định 5m',
        'monitoring_stopped_user': 'Giám sát đã dừng bởi người dùng',
        'starting_monitoring': 'Bắt đầu giám sát liên tục (kiểm tra mỗi {interval} giây)',
        'error_in_monitoring': 'Lỗi trong vòng lặp giám sát: {error}',
    }
}

def get_text(key, lang='en', **kwargs):
    """
    Get translated text for the given key and language
    
    Args:
        key: Translation key
        lang: Language code ('en' or 'vi')
        **kwargs: Format parameters for the text
    
    Returns:
        Translated and formatted text
    """
    if lang not in TRANSLATIONS:
        lang = 'en'  # Default to English
    
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))
    
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text

def get_signal_translation(signal, lang='en'):
    """Get translated signal name"""
    signal_key = signal.upper()
    return get_text(signal_key, lang)

def get_analysis_reason_translation(reason, lang='en'):
    """Translate analysis reasons to Vietnamese"""
    if lang != 'vi':
        return reason
    
    # Map English reasons to Vietnamese translation keys
    reason_map = {
        'RSI Oversold - Potential Long': 'rsi_oversold_long',
        'RSI Overbought - Potential Short': 'rsi_overbought_short',
        'MACD Bullish Crossover - Long Signal': 'macd_bullish_crossover',
        'MACD Bearish Crossover - Short Signal': 'macd_bearish_crossover',
        'Price Above Moving Averages - Bullish': 'price_above_ma_bullish',
        'Price Below Moving Averages - Bearish': 'price_below_ma_bearish',
        'EMA Golden Cross - Strong Long': 'ema_golden_cross',
        'EMA Death Cross - Strong Short': 'ema_death_cross',
        'Price Below Lower Bollinger Band - Oversold': 'bb_oversold',
        'Price Above Upper Bollinger Band - Overbought': 'bb_overbought',
        'Stochastic Oversold - Long Signal': 'stoch_oversold',
        'Stochastic Overbought - Short Signal': 'stoch_overbought',
        'Williams %R Oversold - Long Signal': 'williams_oversold',
        'Williams %R Overbought - Short Signal': 'williams_overbought',
        'No clear signals': 'no_clear_signals',
        'Insufficient data': 'insufficient_data',
    }
    
    translation_key = reason_map.get(reason)
    if translation_key:
        return get_text(translation_key, lang)
    
    return reason  # Return original if no translation found 