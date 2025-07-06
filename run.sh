#!/bin/bash

# Crypto Trading Alert System - Startup Script

echo "🚀 Multi-Market Trading Alert System"
echo "===================================="

# Activate virtual environment
source crypto_env/bin/activate

# Check command line argument
case "$1" in
    "quick"|"q")
        echo "📊 Running Quick Analysis..."
        
        # Parse language and interval arguments
        lang=""
        interval=""
        
        # Check if second argument is a language
        if [ "$2" = "vi" ] || [ "$2" = "vietnamese" ] || [ "$2" = "en" ] || [ "$2" = "english" ]; then
            lang="$2"
            interval="$3"
        else
            # Second argument is interval, use default language
            interval="$2"
        fi
        
        # Build command
        cmd="python quick_analysis.py"
        if [ -n "$lang" ]; then
            cmd="$cmd $lang"
        fi
        if [ -n "$interval" ]; then
            cmd="$cmd $interval"
        fi
        
        echo "Command: $cmd"
        eval $cmd
        ;;
    "gold"|"g")
        echo "🥇 Running Gold Market Analysis..."
        
        # Parse language and interval arguments for gold
        lang=""
        interval=""
        
        # Check if second argument is a language
        if [ "$2" = "vi" ] || [ "$2" = "vietnamese" ] || [ "$2" = "en" ] || [ "$2" = "english" ]; then
            lang="$2"
            interval="$3"
        else
            # Second argument is interval, use default language
            interval="$2"
        fi
        
        # Build command for gold analysis
        cmd="python gold_analysis.py"
        if [ -n "$interval" ]; then
            cmd="$cmd $interval"
        fi
        if [ -n "$lang" ]; then
            cmd="$cmd $lang"
        fi
        
        echo "Command: $cmd"
        eval $cmd
        ;;
    "monitor"|"m")
        echo "🚨 Starting Real-time Monitoring..."
        if [ -n "$2" ]; then
            echo "Duration: $2"
            echo "Will automatically stop after the specified time"
        fi
        echo "Press Ctrl+C to stop manually"
        python alert_system.py $2
        ;;
    "web"|"w")
        echo "🌐 Starting Web Dashboard..."
        echo "Opening browser at http://localhost:8501"
        streamlit run streamlit_app.py
        ;;
    "install"|"i")
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        ;;
    "test-email"|"te")
        echo "📧 Testing Email Configuration..."
        python test_email.py
        ;;
    "news"|"n")
        echo "📰 Running News Sentiment Analysis..."
        
        # Parse arguments for news analysis
        crypto_symbol="BTC"
        hours="24"
        
        if [ -n "$2" ]; then
            crypto_symbol="$2"
        fi
        if [ -n "$3" ]; then
            hours="$3"
        fi
        
        echo "Analyzing $crypto_symbol news from the last $hours hours..."
        python news_analysis.py $crypto_symbol $hours
        ;;
    *)
        echo "Usage: ./run.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  quick, q       - Quick analysis of BTC and ETH"
        echo "  gold, g        - Gold market analysis (GC=F futures and GOLD ETF)"
        echo "  monitor, m     - Start real-time monitoring with alerts (optional: duration)"
        echo "  web, w         - Launch web dashboard"
        echo "  news, n        - Analyze news sentiment (optional: symbol, hours)"
        echo "  install, i     - Install/update dependencies"
        echo "  test-email, te - Test email notification configuration"
        echo ""
        echo "Languages:"
        echo "  en, english     - English (default)"
        echo "  vi, vietnamese  - Vietnamese (Tiếng Việt)"
        echo ""
        echo "Examples:"
        echo "  ./run.sh quick              # Get instant crypto analysis (English, 5m default)"
        echo "  ./run.sh quick vi           # Crypto analysis in Vietnamese (5m default)"
        echo "  ./run.sh quick en 1h        # English crypto analysis with 1 hour timeframe"
        echo "  ./run.sh gold               # Gold market analysis (English, 1h default)"
        echo "  ./run.sh gold 4h            # Gold analysis with 4 hour timeframe"
        echo "  ./run.sh gold vi 1d         # Vietnamese gold analysis with daily timeframe"
        echo "  ./run.sh monitor            # Start monitoring (runs indefinitely)"
        echo "  ./run.sh monitor 1h         # Start monitoring for 1 hour"
        echo "  ./run.sh monitor 30m        # Start monitoring for 30 minutes"
        echo "  ./run.sh monitor 2h30m      # Start monitoring for 2 hours 30 minutes"
        echo "  ./run.sh web                # Launch web interface"
        echo "  ./run.sh news               # Analyze BTC news from last 24 hours"
        echo "  ./run.sh news ETH 12        # Analyze ETH news from last 12 hours"
        echo "  ./run.sh news GOLD 6        # Analyze gold news from last 6 hours"
        echo "  ./run.sh news CRYPTO 6      # Analyze general crypto news from last 6 hours"
        echo "  ./run.sh test-email         # Test email configuration"
        echo ""
        echo "Available intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M"
        ;;
esac 