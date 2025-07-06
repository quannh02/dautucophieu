#!/usr/bin/env python3
"""
Gold Market Analyzer
Comprehensive gold market technical analysis system
Uses Yahoo Finance for gold price data (GC=F - Gold Futures)
"""

import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional
import logging
import yfinance as yf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoldAnalyzer:
    """
    A comprehensive gold market technical analysis system
    """
    
    def __init__(self):
        # Gold symbols - using Yahoo Finance symbols
        self.symbols = {
            "GC=F": "Gold Futures",  # COMEX Gold Futures
            "GLD": "Gold ETF",       # SPDR Gold Shares ETF (correct symbol)
        }
        
        # Gold-specific analysis parameters
        self.volatility_threshold = 2.0  # Gold specific volatility threshold
        self.trend_strength_period = 20  # Period for trend strength calculation
        
    def get_gold_data(self, symbol: str, period: str = "5d", interval: str = "5m") -> pd.DataFrame:
        """
        Fetch historical gold data from Yahoo Finance
        """
        try:
            logger.info(f"Fetching gold data for {symbol}")
            
            # Map interval format for yfinance
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "1h", "1d": "1d"
            }
            
            period_map = {
                "1m": "1d", "5m": "5d", "15m": "5d", "30m": "5d",
                "1h": "10d", "4h": "30d", "1d": "1y"
            }
            
            yf_interval = interval_map.get(interval, "5m")
            yf_period = period_map.get(interval, "5d")
            
            # For 4h, we need to resample 1h data
            if interval == "4h":
                yf_interval = "1h"
                yf_period = "60d"
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=yf_period, interval=yf_interval)
            
            if df.empty:
                logger.error(f"No data received for {symbol}")
                return pd.DataFrame()
            
            # Rename columns to match crypto analyzer format
            df.columns = [col.lower() for col in df.columns]
            
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing column {col} in data")
                    return pd.DataFrame()
            
            # Resample to 4h if needed
            if interval == "4h":
                df = df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
            
            # Remove any rows with NaN values
            df = df.dropna()
            
            # Limit to recent data to match crypto analyzer
            max_rows = 200
            if len(df) > max_rows:
                df = df.tail(max_rows)
            
            logger.info(f"Successfully fetched {len(df)} rows of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching gold data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators optimized for gold market
        """
        if df.empty:
            return df
            
        try:
            # Moving Averages - adjusted for gold volatility
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # RSI - standard for commodities
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # MACD - optimized for gold
            df['macd'] = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12)
            df['macd_signal'] = ta.trend.macd_signal(df['close'], window_slow=26, window_fast=12)
            df['macd_histogram'] = ta.trend.macd(df['close'], window_slow=26, window_fast=12)
            
            # Bollinger Bands - wider bands for gold volatility
            bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2.5)
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_lower'] = bollinger.bollinger_lband()
            
            # Stochastic Oscillator
            df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
            
            # Williams %R
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # Average True Range (ATR) - important for gold volatility
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Gold-specific indicators
            # Commodity Channel Index (CCI) - good for commodities
            df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
            
            # Donchian Channels - useful for breakout analysis
            df['donchian_high'] = df['high'].rolling(window=20).max()
            df['donchian_low'] = df['low'].rolling(window=20).min()
            df['donchian_middle'] = (df['donchian_high'] + df['donchian_low']) / 2
            
            # Price Rate of Change (ROC) - momentum indicator
            df['roc'] = ta.momentum.roc(df['close'], window=12)
            
            # Volume indicators (if volume data available)
            if 'volume' in df.columns and not df['volume'].isna().all():
                df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
                # On-Balance Volume
                df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def calculate_price_action_signals(self, df: pd.DataFrame) -> List[str]:
        """
        Calculate price action signals inspired by Naked Forex principles
        """
        if df.empty or len(df) < 20:
            return []
        
        signals = []
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        recent = df.tail(10)  # Last 10 candles for pattern analysis
        
        try:
            # Support and Resistance levels
            high_20 = df['high'].tail(20).max()
            low_20 = df['low'].tail(20).min()
            
            # Key level breakouts
            if latest['close'] > high_20 * 0.999:  # Near or above 20-period high
                signals.append("Breakout Above Key Resistance - Strong Bullish")
            elif latest['close'] < low_20 * 1.001:  # Near or below 20-period low
                signals.append("Breakdown Below Key Support - Strong Bearish")
            
            # Trend analysis using moving averages
            if latest['close'] > latest['sma_20'] > latest['sma_50']:
                signals.append("Strong Uptrend - Price Above Both MAs")
            elif latest['close'] < latest['sma_20'] < latest['sma_50']:
                signals.append("Strong Downtrend - Price Below Both MAs")
            
            # Momentum shifts
            if latest['close'] > prev['close'] and latest['high'] > prev['high']:
                signals.append("Bullish Momentum - Higher Highs")
            elif latest['close'] < prev['close'] and latest['low'] < prev['low']:
                signals.append("Bearish Momentum - Lower Lows")
            
            # Volatility analysis
            avg_atr = df['atr'].tail(10).mean()
            current_atr = latest['atr']
            
            if current_atr > avg_atr * 1.5:
                signals.append("High Volatility - Increased Market Activity")
            elif current_atr < avg_atr * 0.5:
                signals.append("Low Volatility - Potential Breakout Setup")
            
            # Donchian Channel analysis
            if latest['close'] > latest['donchian_high'] * 0.999:
                signals.append("Donchian Breakout - Bullish Breakout Signal")
            elif latest['close'] < latest['donchian_low'] * 1.001:
                signals.append("Donchian Breakdown - Bearish Breakdown Signal")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error calculating price action signals: {e}")
            return []
    
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signals based on gold market technical analysis
        """
        if df.empty or len(df) < 50:
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'reasons': ['Insufficient data for analysis'],
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0
            }
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        signal_strength = 0
        
        # RSI Analysis - adjusted thresholds for gold
        if latest['rsi'] < 25:  # More extreme oversold for gold
            signals.append("RSI Deeply Oversold - Strong Long Signal")
            signal_strength += 3
        elif latest['rsi'] < 35:
            signals.append("RSI Oversold - Long Signal")
            signal_strength += 1
        elif latest['rsi'] > 75:  # More extreme overbought for gold
            signals.append("RSI Severely Overbought - Strong Short Signal")
            signal_strength -= 3
        elif latest['rsi'] > 65:
            signals.append("RSI Overbought - Short Signal")
            signal_strength -= 1
        
        # MACD Analysis
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals.append("MACD Bullish Crossover - Long Signal")
            signal_strength += 3
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals.append("MACD Bearish Crossover - Short Signal")
            signal_strength -= 3
        
        # Moving Average Analysis
        if latest['close'] > latest['sma_20'] > latest['sma_50']:
            signals.append("Price Above Moving Averages - Bullish Trend")
            signal_strength += 2
        elif latest['close'] < latest['sma_20'] < latest['sma_50']:
            signals.append("Price Below Moving Averages - Bearish Trend")
            signal_strength -= 2
        
        # EMA Crossover (Golden/Death Cross)
        if latest['ema_12'] > latest['ema_26'] and prev['ema_12'] <= prev['ema_26']:
            signals.append("EMA Golden Cross - Strong Long Signal")
            signal_strength += 3
        elif latest['ema_12'] < latest['ema_26'] and prev['ema_12'] >= prev['ema_26']:
            signals.append("EMA Death Cross - Strong Short Signal")
            signal_strength -= 3
        
        # Bollinger Bands Analysis
        if latest['close'] < latest['bb_lower']:
            signals.append("Price Below Lower Bollinger Band - Oversold")
            signal_strength += 2
        elif latest['close'] > latest['bb_upper']:
            signals.append("Price Above Upper Bollinger Band - Overbought")
            signal_strength -= 2
        
        # CCI Analysis (Commodity Channel Index)
        if 'cci' in df.columns:
            if latest['cci'] < -150:  # Extreme oversold for commodities
                signals.append("CCI Extreme Oversold - Strong Long Signal")
                signal_strength += 2
            elif latest['cci'] > 150:  # Extreme overbought for commodities
                signals.append("CCI Extreme Overbought - Strong Short Signal")
                signal_strength -= 2
        
        # Stochastic Analysis
        if latest['stoch_k'] < 15 and latest['stoch_d'] < 15:
            signals.append("Stochastic Oversold - Long Signal")
            signal_strength += 1
        elif latest['stoch_k'] > 85 and latest['stoch_d'] > 85:
            signals.append("Stochastic Overbought - Short Signal")
            signal_strength -= 1
        
        # Williams %R Analysis
        if latest['williams_r'] < -85:
            signals.append("Williams %R Oversold - Long Signal")
            signal_strength += 1
        elif latest['williams_r'] > -15:
            signals.append("Williams %R Overbought - Short Signal")
            signal_strength -= 1
        
        # Add price action signals
        price_action_signals = self.calculate_price_action_signals(df)
        signals.extend(price_action_signals)
        
        # Adjust signal strength based on price action
        for signal in price_action_signals:
            if "Strong Bullish" in signal or "Bullish Breakout" in signal:
                signal_strength += 2
            elif "Strong Bearish" in signal or "Bearish Breakdown" in signal:
                signal_strength -= 2
            elif "Bullish" in signal:
                signal_strength += 1
            elif "Bearish" in signal:
                signal_strength -= 1
        
        # Determine overall signal
        if signal_strength >= 4:
            overall_signal = "STRONG_LONG"
        elif signal_strength >= 2:
            overall_signal = "LONG"
        elif signal_strength <= -4:
            overall_signal = "STRONG_SHORT"
        elif signal_strength <= -2:
            overall_signal = "SHORT"
        else:
            overall_signal = "NEUTRAL"
        
        # Calculate entry, stop loss, and take profit levels
        current_price = latest['close']
        atr = latest['atr']
        
        # Gold-specific risk management (wider stops due to volatility)
        if 'LONG' in overall_signal:
            entry_price = current_price
            stop_loss = current_price - (2.5 * atr)  # Wider stop for gold
            take_profit = current_price + (4 * atr)   # Better risk/reward
        elif 'SHORT' in overall_signal:
            entry_price = current_price
            stop_loss = current_price + (2.5 * atr)
            take_profit = current_price - (4 * atr)
        else:
            entry_price = current_price
            stop_loss = 0
            take_profit = 0
        
        return {
            'signal': overall_signal,
            'strength': abs(signal_strength),
            'reasons': signals if signals else ['No clear signals detected'],
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2) if stop_loss > 0 else 0,
            'take_profit': round(take_profit, 2) if take_profit > 0 else 0,
            'current_price': round(current_price, 2),
            'rsi': round(latest['rsi'], 2),
            'macd': round(latest['macd'], 6),
            'cci': round(latest.get('cci', 0), 2),
            'atr': round(latest['atr'], 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def analyze_symbol(self, symbol: str, interval: str = "5m") -> Dict:
        """
        Perform complete analysis for a gold symbol
        """
        logger.info(f"Analyzing {symbol} ({self.symbols.get(symbol, symbol)}) on {interval} timeframe")
        
        # Get historical data
        df = self.get_gold_data(symbol, interval=interval)
        
        if df.empty:
            return {
                'symbol': symbol,
                'error': 'Failed to fetch gold market data'
            }
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Generate signals
        signals = self.generate_signals(df)
        
        return {
            'symbol': symbol,
            'name': self.symbols.get(symbol, symbol),
            'analysis': signals,
            'data': df,
            'interval': interval,
            'market': 'GOLD'
        }
    
    def analyze_all_symbols(self, interval: str = "5m") -> Dict:
        """
        Analyze all gold symbols
        """
        results = {}
        
        for symbol in self.symbols.keys():
            try:
                result = self.analyze_symbol(symbol, interval)
                results[symbol] = result
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                results[symbol] = {
                    'symbol': symbol,
                    'error': f'Analysis failed: {str(e)}'
                }
        
        return results

if __name__ == "__main__":
    # Test the gold analyzer
    analyzer = GoldAnalyzer()
    results = analyzer.analyze_all_symbols(interval="1h")
    
    for symbol, data in results.items():
        print(f"\n=== {symbol} ===")
        if 'error' in data:
            print(f"Error: {data['error']}")
        else:
            analysis = data['analysis']
            print(f"Signal: {analysis['signal']} (Strength: {analysis['strength']})")
            print(f"Price: ${analysis['current_price']}")
            print(f"RSI: {analysis['rsi']}")
            print("Reasons:")
            for reason in analysis['reasons']:
                print(f"  - {reason}") 