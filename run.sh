#!/bin/bash

# Crypto Trading Alert System - Startup Script

echo "🚀 Crypto Trading Alert System"
echo "=============================="

# Activate virtual environment
source crypto_env/bin/activate

# Check command line argument
case "$1" in
    "quick"|"q")
        echo "📊 Running Quick Analysis..."
        if [ -n "$2" ]; then
            echo "Using $2 timeframe..."
            python quick_analysis.py $2
        else
            python quick_analysis.py
        fi
        ;;
    "monitor"|"m")
        echo "🚨 Starting Real-time Monitoring..."
        echo "Press Ctrl+C to stop"
        python alert_system.py
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
    *)
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  quick, q    - Quick analysis of BTC and ETH"
        echo "  monitor, m  - Start real-time monitoring with alerts"
        echo "  web, w      - Launch web dashboard"
        echo "  install, i  - Install/update dependencies"
        echo ""
        echo "Examples:"
        echo "  ./run.sh quick        # Get instant analysis (5m default)"
        echo "  ./run.sh quick 1h     # Analysis with 1 hour timeframe"
        echo "  ./run.sh quick 1d     # Analysis with daily timeframe"
        echo "  ./run.sh monitor      # Start monitoring"
        echo "  ./run.sh web          # Launch web interface"
        ;;
esac 