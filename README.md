# 🚀 Multi-Market Trading Alert System

A comprehensive technical analysis and alert system for **cryptocurrency**, **gold market**, and **Vietnamese stock** trading. Combines real-time technical indicators with news sentiment analysis to provide enhanced trading signals.

## 📊 Supported Markets

### 📈 Cryptocurrency Markets
- **BTC/USDT** (Bitcoin)
- **ETH/USDT** (Ethereum)
- Data source: Binance API

### 🥇 Gold Markets  
- **GC=F** (COMEX Gold Futures)
- **GLD** (SPDR Gold Shares ETF)
- Data source: Yahoo Finance

### 🇻🇳 Vietnamese Stock Markets
- **VNM.VN** (Vinamilk)
- **VCB.VN** (Vietcombank)
- **VIC.VN** (Vingroup)
- **HPG.VN** (Hoa Phat Group)
- **TCB.VN** (Techcombank)
- **MSN.VN** (Masan Group)
- **FPT.VN** (FPT Corporation)
- **MWG.VN** (Mobile World)
- **GAS.VN** (PV Gas)
- **CTG.VN** (VietinBank)
- **NVL.VN** (NovaLand)
- **TPB.VN** (Tien Phong Bank)
- **HHV.VN** (Hoa Hao Vinamilk)
- **VJC.VN** (VietJet Aviation)
- **VND.VN** (VN Direct Securities)
- Data source: Yahoo Finance (HSX/HNX)
- **Total: 15 Major Vietnamese Stocks**

## 🌟 Features

- **📊 Multi-Market Technical Analysis**: Crypto + Gold + Vietnamese stocks
- **📰 News Sentiment Analysis**: Multi-source news aggregation with sentiment scoring
- **🚨 Real-time Alerts**: Desktop and email notifications
- **🌐 Web Dashboard**: Interactive Streamlit interface
- **🎯 Price Action Analysis**: Based on proven trading principles
- **🔔 Smart Signal Enhancement**: Combines technical + news sentiment
- **🌍 Multi-language Support**: English and Vietnamese
- **⚡ Multiple Timeframes**: 5m to 1d intervals

## 🛠 Quick Start

### 1. Installation
```bash
# Clone and setup
git clone <repository-url>
cd dautucophieu
./run.sh install

# Or manually:
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

### 2. Quick Analysis

#### Cryptocurrency Analysis
```bash
# Quick crypto analysis (5m timeframe)
./run.sh quick

# 1-hour crypto analysis in Vietnamese
./run.sh quick vi 1h

# Daily crypto analysis  
./run.sh quick en 1d
```

#### Gold Market Analysis
```bash
# Gold market analysis (1h timeframe default)
./run.sh gold

# 4-hour gold analysis
./run.sh gold 4h

# Daily gold analysis in Vietnamese
./run.sh gold vi 1d
```

#### Vietnamese Stock Analysis
```bash
# Analyze top 5 Vietnamese stocks (1h timeframe)
./run.sh vnstock

# Analyze specific Vietnamese stock
./run.sh vnstock VNM.VN 1h en     # Vinamilk analysis
./run.sh vnstock VCB.VN 4h vi     # Vietcombank in Vietnamese

# Analyze multiple stocks in Vietnamese
./run.sh vnstock ALL 1d vi 10     # Top 10 stocks, daily timeframe
```

### 3. News Sentiment Analysis
```bash
# Analyze crypto news
./run.sh news BTC 24        # BTC news from last 24 hours
./run.sh news ETH 12        # ETH news from last 12 hours

# Analyze gold news  
./run.sh news GOLD 6        # Gold news from last 6 hours
./run.sh news CRYPTO 24     # General crypto news
```

### 4. Real-time Monitoring
```bash
# Start continuous monitoring (all markets)
./run.sh monitor

# Monitor for specific duration
./run.sh monitor 2h         # Monitor for 2 hours
./run.sh monitor 30m        # Monitor for 30 minutes
```

### 5. Web Dashboard
```bash
# Launch interactive web interface
./run.sh web
# Open browser at http://localhost:8501
```

## 📈 Technical Indicators

### Universal Indicators (Crypto + Gold)
- **RSI (14)**: Relative Strength Index
- **MACD (12,26,9)**: Moving Average Convergence Divergence  
- **SMA (20,50)**: Simple Moving Averages
- **EMA (12,26)**: Exponential Moving Averages
- **Bollinger Bands (20,2)**: Volatility bands
- **Stochastic Oscillator**: Momentum indicator
- **Williams %R**: Momentum oscillator
- **ATR**: Average True Range (volatility)

### Gold-Specific Indicators
- **CCI (20)**: Commodity Channel Index
- **Donchian Channels (20)**: Breakout analysis
- **ROC (12)**: Rate of Change
- **OBV**: On-Balance Volume
- **Price Action Signals**: Support/resistance levels, trend analysis

## 🥇 Gold Market Analysis Features

### Technical Analysis Optimized for Gold
- **Wider Bollinger Bands**: Adjusted for gold volatility (2.5 standard deviations)
- **Gold-Specific RSI Thresholds**: 25/75 for extreme oversold/overbought
- **Commodity-Focused Indicators**: CCI and Donchian Channels
- **Enhanced Risk Management**: 2.5x ATR stops, 4x ATR targets
- **Price Action Patterns**: Support/resistance, breakouts, trend strength

### Two Gold Instruments
1. **Gold Futures (GC=F)**
   - COMEX gold futures contract
   - Higher volatility and leverage
   - Real-time futures pricing
   
2. **Gold ETF (GLD)**  
   - SPDR Gold Shares ETF
   - More stable, less volatile
   - Stock market hours

### Gold-Specific Features
- **Breakout Detection**: Donchian channel breakouts
- **Trend Strength Analysis**: Moving average slopes and crossovers  
- **Volatility Assessment**: ATR-based volatility analysis
- **Momentum Shifts**: Higher highs/lower lows detection
- **Key Level Analysis**: 20-period support/resistance levels

## 📰 News Sentiment Analysis

### Crypto News Sources
- **CoinDesk**: Leading cryptocurrency news
- **Cointelegraph**: Comprehensive crypto coverage
- **Decrypt**: Technology-focused journalism  
- **Bitcoinist**: Bitcoin and altcoin insights

### Gold News Sources
- **MarketWatch**: Financial and commodity news
- **Kitco News**: Precious metals specialist
- **CoinDesk**: Also covers digital gold trends
- **Cointelegraph**: Crypto-gold correlations

### Sentiment Analysis Features
- **Multi-source Aggregation**: 6 major news sources
- **Relevance Filtering**: Asset-specific keyword matching
- **Sentiment Scoring**: TextBlob + custom keyword analysis
- **Confidence Metrics**: Reliability assessment
- **Trading Recommendations**: Buy/sell/hold based on sentiment
- **Signal Enhancement**: Combines with technical analysis

### News Integration
- **Aligned Signals**: News supports technical analysis (higher confidence)
- **Conflicting Signals**: News contradicts technical (warning issued)
- **News Override**: Strong news can override neutral technical signals
- **Multi-timeframe**: 1-168 hours of historical analysis

## 🎯 Signal Types and Strength

### Signal Categories
- **STRONG_LONG**: High confidence bullish signal (strength 4-10)
- **LONG**: Moderate bullish signal (strength 2-3)
- **NEUTRAL**: No clear direction (strength 0-1)
- **SHORT**: Moderate bearish signal (strength 2-3)
- **STRONG_SHORT**: High confidence bearish signal (strength 4-10)

### Signal Enhancement
Technical signals are enhanced with news sentiment:
- **Aligned**: Technical + news in same direction → Increased strength
- **Conflicted**: Technical vs news opposite → Warning flag
- **News-driven**: Strong news overrides weak technical → New signal

### Gold vs Crypto Signal Differences
**Gold Markets:**
- More conservative thresholds (25/75 RSI)
- Wider stop losses (2.5x ATR)
- Better risk/reward ratios (4x ATR targets)
- Commodity-specific indicators (CCI, Donchian)

**Crypto Markets:**
- Standard thresholds (30/70 RSI)
- Standard stop losses (2x ATR)  
- Standard targets (3x ATR)
- Crypto-optimized indicators

## 🚨 Alert System

### Real-time Monitoring
- **Multi-market**: Monitors both crypto and gold simultaneously
- **Smart Alerts**: Only triggers on signal changes or strong signals
- **Multiple Channels**: Desktop notifications + email alerts
- **Enhanced Notifications**: Includes news sentiment in alerts
- **Alert History**: Persistent storage of all alerts

### Alert Triggers
- Signal changes (NEUTRAL → LONG, LONG → SHORT, etc.)
- Strong signals (STRONG_LONG, STRONG_SHORT)
- New signals from neutral state
- News sentiment conflicts with technical analysis

### Notification Content
- Market type (crypto/gold) and symbol
- Signal type and strength
- Current price and key metrics (RSI, MACD)
- Entry/exit levels if applicable
- News sentiment summary
- Reasoning behind the signal

## 🌐 Web Dashboard

### Multi-Market Interface
- **Market Tabs**: Separate tabs for Crypto and Gold markets
- **Real-time Data**: Auto-refreshing price and indicator data
- **Interactive Charts**: Plotly-based technical analysis charts
- **News Integration**: Sentiment indicators and article summaries
- **Combined Analysis**: Shows technical vs news alignment

### Dashboard Features
- **Multi-language**: English/Vietnamese interface
- **Customizable Intervals**: 5m to 1d timeframes
- **Technical Charts**: Full candlestick charts with indicators
- **Alert History**: Recent signals and their outcomes
- **System Status**: Monitoring state and last update times
- **Mobile Responsive**: Works on desktop and mobile devices

## ⚙️ Configuration

### Crypto Symbols (Binance)
Edit `crypto_analyzer.py`:
```python
self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]  # Add more pairs
```

### Gold Symbols (Yahoo Finance)  
Edit `gold_analyzer.py`:
```python
self.symbols = {
    "GC=F": "Gold Futures",
    "GLD": "Gold ETF", 
    "GOLD": "Additional Gold ETF"  # Add more gold instruments
}
```

### Alert Settings
Edit `alert_system.py`:
```python
alert_system = AlertSystem(check_interval=300)  # 5 minutes
```

### Technical Parameters

**Crypto Settings:**
```python
# RSI thresholds
oversold = 30
overbought = 70

# Stop loss/take profit
stop_loss_atr = 2.0
take_profit_atr = 3.0
```

**Gold Settings:**
```python  
# RSI thresholds (more conservative)
oversold = 25  
overbought = 75

# Stop loss/take profit (wider for volatility)
stop_loss_atr = 2.5
take_profit_atr = 4.0
```

## 📊 Usage Examples

### Multi-Market Analysis Workflow

1. **Morning Market Check**:
   ```bash
   # Quick overview of all markets
   ./run.sh quick en 1h      # Crypto hourly
   ./run.sh gold en 1h       # Gold hourly
   ./run.sh news CRYPTO 12   # Overnight crypto news
   ./run.sh news GOLD 12     # Overnight gold news
   ```

2. **Day Trading Setup**:
   ```bash
   # Start real-time monitoring
   ./run.sh monitor 8h       # Monitor for trading day
   
   # Or use web interface
   ./run.sh web              # Interactive dashboard
   ```

3. **Swing Trading Analysis**:
   ```bash
   # Daily timeframe analysis
   ./run.sh quick en 1d      # Daily crypto trends
   ./run.sh gold en 1d       # Daily gold trends
   ./run.sh news CRYPTO 48   # 2-day news sentiment
   ./run.sh news GOLD 48     # 2-day gold news
   ```

4. **Correlation Analysis**:
   ```bash
   # Compare crypto vs gold
   ./run.sh quick en 4h && ./run.sh gold en 4h
   ```

### Integration with Trading Platforms

The system provides:
- **Entry/Exit Levels**: Calculated stop loss and take profit levels
- **Risk Management**: ATR-based position sizing guidance
- **Market Context**: News sentiment adds fundamental context
- **Multi-timeframe**: Various timeframes for different strategies

## 🔧 Advanced Features

### Custom Indicators
Add your own indicators in the analyzer files:

**For Crypto** (`crypto_analyzer.py`):
```python
def calculate_custom_indicator(self, df):
    df['custom'] = your_calculation
    return df
```

**For Gold** (`gold_analyzer.py`):
```python  
def calculate_gold_specific_indicator(self, df):
    df['gold_custom'] = your_gold_calculation
    return df
```

### News Source Customization
Add new news sources in `news_analyzer.py`:
```python
self.news_sources['new_source'] = {
    'rss': 'https://newssite.com/feed',
    'name': 'New Source'
}
```

### Multi-timeframe Analysis
```python
# Analyze multiple timeframes
timeframes = ["5m", "1h", "4h", "1d"]
for tf in timeframes:
    crypto_results = analyzer.analyze_all_symbols(interval=tf)
    gold_results = gold_analyzer.analyze_all_symbols(interval=tf)
```

## 🚨 Risk Management

### Position Sizing
- **ATR-based Stops**: Dynamic stop losses based on market volatility
- **Risk/Reward**: Minimum 1:1.5 ratio (crypto), 1:1.6 (gold)
- **Position Size**: Risk 1-2% of capital per trade

### Signal Validation
- **Multiple Confirmations**: Require 2+ indicators for strong signals
- **News Alignment**: Higher confidence when news supports technical
- **Timeframe Consensus**: Check multiple timeframes
- **Market Context**: Consider overall market conditions

### Gold-Specific Risks
- **Higher Volatility**: Gold can have sudden moves
- **News Sensitivity**: Reacts strongly to economic data
- **Session Differences**: Futures (24/7) vs ETF (market hours)
- **Leverage Warning**: Futures contracts are leveraged

### Crypto-Specific Risks  
- **Extreme Volatility**: Crypto can move 10%+ in minutes
- **24/7 Markets**: No closing bell, constant monitoring needed
- **News Impact**: Social media and regulation news
- **Liquidity**: Some pairs may have low liquidity

## 🛠 Troubleshooting

### Common Issues

**Installation Problems:**
```bash
# Reinstall dependencies
./run.sh install

# Manual installation
pip install --upgrade -r requirements.txt
```

**Data Fetching Issues:**
- **Binance API**: Check internet connection, try again later
- **Yahoo Finance**: Some symbols may be delisted or renamed
- **News Sources**: RSS feeds may be temporarily unavailable

**Gold Data Issues:**
```bash
# Test gold analyzer
python -c "from gold_analyzer import GoldAnalyzer; g = GoldAnalyzer(); print('OK')"

# Test specific symbol
python gold_analysis.py 1h
```

**Performance Optimization:**
- Reduce monitoring frequency for less API usage
- Use longer timeframes for swing trading
- Cache results to reduce redundant calculations

## 📚 Educational Resources

### Technical Analysis Concepts
- **RSI**: Measures momentum, 0-100 scale
- **MACD**: Trend following indicator with signal line
- **Bollinger Bands**: Volatility-based support/resistance
- **ATR**: Measures market volatility for stop placement

### Gold Market Fundamentals
- **Economic Indicators**: GDP, inflation, interest rates
- **Currency Correlation**: USD strength vs gold prices
- **Safe Haven**: Gold performance during market stress
- **Physical vs Paper**: Futures vs ETF differences

### Risk Management
- **Position Sizing**: Never risk more than 2% per trade
- **Stop Losses**: Always use stops, no exceptions
- **Diversification**: Don't put all capital in one market
- **Emotion Control**: Follow system signals, avoid FOMO

## ⚠️ Disclaimers

- **Educational Purpose**: This system is for learning and research only
- **Not Financial Advice**: Always do your own research and consult professionals
- **Past Performance**: Historical results don't guarantee future performance
- **Risk Warning**: Trading involves substantial risk of loss
- **Market Hours**: Consider different trading sessions for various markets
- **Regulation**: Ensure compliance with local trading regulations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/gold-analysis`)
3. Commit changes (`git commit -m 'Add gold analysis'`)
4. Push to branch (`git push origin feature/gold-analysis`)
5. Open Pull Request

### Development Guidelines
- **Code Quality**: Follow PEP 8 style guidelines
- **Testing**: Test all new features thoroughly
- **Documentation**: Update README for new features
- **Compatibility**: Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Trading! 🚀📈🥇**

*Remember: The best trading system is the one you understand and can execute consistently. Start with paper trading to validate signals before risking real capital.* 