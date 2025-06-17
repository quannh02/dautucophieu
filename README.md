# 🚀 Crypto Trading Alert System

A comprehensive real-time cryptocurrency trading alert system with advanced technical analysis for BTC and ETH. This system provides professional-grade trading signals using multiple technical indicators and delivers alerts through multiple channels.

## ✨ Features

### 📊 Technical Analysis
- **RSI (Relative Strength Index)** - Momentum oscillator for overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)** - Trend-following momentum indicator
- **Moving Averages** - SMA 20, SMA 50, EMA 12, EMA 26
- **Bollinger Bands** - Volatility and trend analysis
- **Stochastic Oscillator** - Momentum indicator comparing closing price to price range
- **Williams %R** - Momentum indicator showing overbought/oversold levels
- **Average True Range (ATR)** - Volatility measurement for stop-loss calculation

### 🚨 Alert System
- **Real-time monitoring** with customizable intervals
- **Desktop notifications** using system notifications
- **Email notifications** with rich HTML formatting
- **Console alerts** with colored output
- **Signal strength scoring** (1-10 scale)
- **Entry/Exit level calculations** with ATR-based stop-loss and take-profit
- **Alert history** with JSON persistence

### 🎯 Trading Signals
- **STRONG_LONG** - High confidence buy signal
- **LONG** - Moderate buy signal
- **NEUTRAL** - No clear direction
- **SHORT** - Moderate sell signal
- **STRONG_SHORT** - High confidence sell signal

### 🌐 Multiple Interfaces
1. **Command Line** - Quick analysis (`quick_analysis.py`)
2. **Real-time Console** - Continuous monitoring (`alert_system.py`)
3. **Web Dashboard** - Beautiful Streamlit interface (`streamlit_app.py`)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for API access

### Quick Setup

1. **Clone or download the project files**
```bash
# Make sure all files are in the same directory
ls -la
# You should see: crypto_analyzer.py, alert_system.py, streamlit_app.py, quick_analysis.py, requirements.txt
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Test the installation**
```bash
python quick_analysis.py
```

## 🚀 Usage

### Startup Script (Recommended)
Use the convenient startup script for all operations:

```bash
# Quick analysis (English, 5m default)
./run.sh quick

# Quick analysis in Vietnamese
./run.sh quick vi

# Analysis with custom timeframes
./run.sh quick en 1h        # English, 1 hour
./run.sh quick vietnamese 4h # Vietnamese, 4 hours
./run.sh quick 1d           # English (default), daily

# Start monitoring (runs indefinitely)
./run.sh monitor

# Start monitoring for specific duration
./run.sh monitor 1h        # Run for 1 hour
./run.sh monitor 30m       # Run for 30 minutes
./run.sh monitor 2h30m     # Run for 2 hours 30 minutes

# Launch web interface
./run.sh web

# Install dependencies
./run.sh install
```

### 1. Quick Analysis (Instant Results)
Get immediate technical analysis for BTC and ETH:

```bash
# English (default)
python quick_analysis.py

# Vietnamese
python quick_analysis.py vi

# With custom interval
python quick_analysis.py 1h        # English, 1 hour
python quick_analysis.py vi 4h     # Vietnamese, 4 hours
```

**Sample Output:**
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
🚀 CRYPTO TRADING ANALYZER 🚀
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
📊 BTC/USDT ANALYSIS
============================================================
🟢 SIGNAL: STRONG_LONG (Strength: 5)
💰 Current Price: $43,567.8900
📈 RSI: 45.23 (Neutral)
📊 MACD: 0.002341

🎯 TRADING LEVELS:
   Entry: $43,567.89
   Stop Loss: $42,891.45
   Take Profit: $44,583.12

📋 ANALYSIS DETAILS:
   1. MACD Bullish Crossover - Long Signal
   2. Price Above Moving Averages - Bullish
   3. EMA Golden Cross - Strong Long
```

### 2. Real-time Monitoring (Console)
Start continuous monitoring with alerts:

```bash
# Run indefinitely
python alert_system.py

# Run for specific duration
python alert_system.py 1h      # 1 hour
python alert_system.py 30m     # 30 minutes
python alert_system.py 2h30m   # 2 hours 30 minutes

# Or use the run script
./run.sh monitor 1h
```

Features:
- Checks every 5 minutes (configurable)
- **Time-limited monitoring** with automatic stop
- **Countdown timer** showing remaining time
- Desktop notifications for new signals
- Colored console output
- Alert history saved to JSON
- Ctrl+C to stop manually

### 3. Web Dashboard (Streamlit)
Launch the beautiful web interface:

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

Features:
- **Multi-language Support**: Switch between English and Vietnamese
- Interactive charts with technical indicators
- Real-time price updates
- Signal history
- Customizable refresh intervals
- Mobile-responsive design

## 📈 Technical Indicators Explained

### RSI (Relative Strength Index)
- **< 30**: Oversold (potential buy signal)
- **> 70**: Overbought (potential sell signal)
- **30-70**: Neutral zone

### MACD (Moving Average Convergence Divergence)
- **Bullish Crossover**: MACD line crosses above signal line
- **Bearish Crossover**: MACD line crosses below signal line
- **Histogram**: Shows momentum strength

### Moving Averages
- **Golden Cross**: Short MA crosses above long MA (bullish)
- **Death Cross**: Short MA crosses below long MA (bearish)
- **Price vs MA**: Price above/below moving averages indicates trend

### Bollinger Bands
- **Price at Lower Band**: Potentially oversold
- **Price at Upper Band**: Potentially overbought
- **Band Squeeze**: Low volatility (potential breakout)

## ⚙️ Configuration

### Customizing Symbols
Edit `crypto_analyzer.py` to add more trading pairs:

```python
self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
```

### Adjusting Alert Frequency
Modify `alert_system.py`:

```python
alert_system = AlertSystem(check_interval=300)  # 300 seconds = 5 minutes
```

### Changing Technical Parameters
In `crypto_analyzer.py`, adjust indicator periods:

```python
# RSI period
df['rsi'] = ta.momentum.rsi(df['close'], window=14)  # Default: 14

# Moving average windows
df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)  # Default: 20
df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)  # Default: 50
```

## 📊 Signal Interpretation

### Signal Strength Scoring
- **Strength 1-2**: Weak signal, use with caution
- **Strength 3-4**: Moderate signal, good for confirmation
- **Strength 5-7**: Strong signal, reliable for trading
- **Strength 8-10**: Very strong signal, high confidence

### Risk Management
- **Stop Loss**: Calculated using 2x ATR below entry (long) or above entry (short)
- **Take Profit**: Calculated using 3x ATR above entry (long) or below entry (short)
- **Position Sizing**: Always use proper position sizing (risk 1-2% of capital per trade)

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
```bash
pip install --upgrade -r requirements.txt
```

2. **API Connection Issues**
- Check internet connection
- Binance API might be temporarily unavailable
- Try again after a few minutes

3. **Missing Dependencies**
```bash
pip install pandas numpy ta requests streamlit plotly colorama plyer
```

4. **Permission Errors (macOS/Linux)**
```bash
chmod +x quick_analysis.py
python3 quick_analysis.py
```

### Performance Optimization
- Reduce check interval for faster updates (higher API usage)
- Increase interval to reduce API calls
- Use fewer technical indicators for faster computation

## 📈 Advanced Usage

### Custom Indicators
Add your own indicators in `crypto_analyzer.py`:

```python
def calculate_custom_indicator(self, df):
    # Your custom indicator logic here
    df['custom_indicator'] = your_calculation
    return df
```

### Multiple Timeframes
Analyze different timeframes:

```python
# In crypto_analyzer.py
df_5m = self.get_klines(symbol, interval="5m")
df_1h = self.get_klines(symbol, interval="1h")
df_1d = self.get_klines(symbol, interval="1d")
```

### Email Alerts
Add email notifications in `alert_system.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(self, message):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    # Add your email logic here
```

## 📧 Email Notifications

The system now supports email notifications for trading alerts! When enabled, you'll receive beautifully formatted HTML emails with all the trading signal details.

## Setting Up Email Alerts

1. **Copy the configuration file:**
   ```bash
   cp config.example config.py
   ```

2. **Edit `config.py` and configure email settings:**
   ```python
   # Enable email alerts
   ENABLE_EMAIL_ALERTS = True
   
   # Email configuration (Gmail example)
   EMAIL_SMTP_SERVER = "smtp.gmail.com"
   EMAIL_SMTP_PORT = 587
   EMAIL_SENDER = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"  # Use Gmail App Password, not regular password
   EMAIL_RECIPIENTS = ["recipient1@gmail.com", "recipient2@gmail.com"]
   EMAIL_USE_TLS = True
   ```

3. **For Gmail users:**
   - Enable 2-factor authentication on your Google account
   - Generate an App Password: Go to Google Account Settings → Security → App passwords
   - Use the App Password (not your regular Gmail password) in the `EMAIL_PASSWORD` field

4. **For other email providers:**
   - Update `EMAIL_SMTP_SERVER` and `EMAIL_SMTP_PORT` according to your provider
   - Common SMTP settings:
     - **Outlook/Hotmail:** `smtp-mail.outlook.com`, port `587`
     - **Yahoo:** `smtp.mail.yahoo.com`, port `587`
     - **Custom SMTP:** Contact your email provider for settings

## Email Features

- 📧 **Rich HTML emails** with color-coded alerts
- 🎯 **Multiple recipients** support
- 🔒 **Secure TLS encryption**
- 📊 **Complete trading information** including entry/exit levels
- 🚨 **Batch alerts** - multiple signals in one email
- ✅ **Email validation** to prevent configuration errors

## Testing Email Setup

You can test your email configuration using the dedicated test script:

```bash
python test_email.py
```

This will:
- ✅ Verify your email configuration
- 📧 Send a test email with sample trading data
- 🔧 Provide troubleshooting tips if there are issues

Alternatively, you can test with a real analysis:

```bash
python quick_analysis.py
```

If email alerts are enabled and configured correctly, you'll receive an email when trading signals are detected.

## ⚠️ Disclaimer

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY**

- This is not financial advice
- Cryptocurrency trading involves significant risk
- Past performance does not guarantee future results
- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- Consider consulting with a financial advisor

## 📋 API Rate Limits

### Binance API Limits
- **Weight limit**: 1200 per minute
- **Order limit**: 10 per second
- **This system**: Uses ~2-4 weight per analysis cycle

### Staying Within Limits
- Default 5-minute intervals are safe
- Avoid intervals less than 30 seconds
- Monitor console for rate limit warnings

## 🤝 Contributing

Feel free to contribute improvements:

1. Add new technical indicators
2. Implement additional alert channels (Discord, Telegram, etc.)
3. Add more cryptocurrency pairs
4. Improve the web interface
5. Add backtesting functionality

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Ensure all dependencies are installed
3. Verify internet connection
4. Check Binance API status

## 🎯 Roadmap

Future features planned:
- [ ] Backtesting engine
- [ ] Portfolio tracking
- [ ] More exchanges (Coinbase, Kraken)
- [ ] Machine learning signals
- [ ] Mobile app
- [ ] Discord/Telegram bots
- [ ] Advanced charting tools

---

**Happy Trading! 🚀📈**

Remember: The best traders are those who manage risk properly and never stop learning. 