# Gmail Configuration Example for Crypto Trading Alert System
# Copy this file to config.py and modify with your actual credentials

# API Configuration (optional - uses public endpoints by default)
# BINANCE_API_KEY = "your_api_key_here"
# BINANCE_SECRET_KEY = "your_secret_key_here"

# Alert Settings
ALERT_INTERVAL = 300  # seconds (5 minutes)
ENABLE_DESKTOP_NOTIFICATIONS = True  # Set to False if desktop notifications don't work
ENABLE_CONSOLE_ALERTS = True
ENABLE_EMAIL_ALERTS = True  # Enable email notifications

# Gmail Email Configuration
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_SENDER = "your_gmail@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = "your_app_password"   # Replace with your Gmail App Password
EMAIL_RECIPIENTS = [
    "recipient1@gmail.com",  # Replace with actual recipient emails
    "recipient2@gmail.com"   # You can add multiple recipients
]
EMAIL_USE_TLS = True

# Trading Pairs (list)
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# Technical Analysis Settings
RSI_PERIOD = 14
SMA_SHORT = 20
SMA_LONG = 50
EMA_SHORT = 12
EMA_LONG = 26
BOLLINGER_PERIOD = 20
STOCH_PERIOD = 14

# Risk Management
ATR_STOP_LOSS_MULTIPLIER = 2.0
ATR_TAKE_PROFIT_MULTIPLIER = 3.0

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "crypto_alerts.log"

# Instructions for Gmail Setup:
# 1. Enable 2-Factor Authentication on your Google account
# 2. Go to Google Account Settings → Security → App passwords
# 3. Generate a new App Password for "Mail"
# 4. Use the generated 16-character password in EMAIL_PASSWORD above
# 5. Replace EMAIL_SENDER with your Gmail address
# 6. Replace EMAIL_RECIPIENTS with the email addresses you want to receive alerts 