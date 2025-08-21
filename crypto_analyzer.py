import pandas as pd
import numpy as np
import ta
import time
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzer:
    """
    A comprehensive cryptocurrency technical analysis system
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.symbols = ["BTCUSDT", "ETHUSDT"]
        
    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 200) -> pd.DataFrame:
        """
        Fetch historical kline data from Binance
        """
        try:
            url = f"{self.base_url}/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
                
            # Convert timestamp
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol
        """
        try:
            url = f"{self.base_url}/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return float(data['price'])
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return 0.0
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate various technical indicators
        """
        if df.empty:
            return df
            
        # Moving Averages
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
        df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
        
        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        
        # MACD
        df['macd'] = ta.trend.macd_diff(df['close'])
        df['macd_signal'] = ta.trend.macd_signal(df['close'])
        df['macd_histogram'] = ta.trend.macd(df['close'])
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_lower'] = bollinger.bollinger_lband()
        
        # Stochastic Oscillator
        df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
        df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
        
        # Williams %R
        df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
        
        # Average True Range (ATR)
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
        
        # Volume indicators
        df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signals based on technical analysis
        """
        if df.empty or len(df) < 50:
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'reasons': ['Insufficient data'],
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0
            }
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        signal_strength = 0
        
        # RSI Analysis
        if latest['rsi'] < 30:
            signals.append("RSI Oversold - Potential Long")
            signal_strength += 2
        elif latest['rsi'] > 70:
            signals.append("RSI Overbought - Potential Short")
            signal_strength -= 2
        
        # MACD Analysis
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals.append("MACD Bullish Crossover - Long Signal")
            signal_strength += 3
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals.append("MACD Bearish Crossover - Short Signal")
            signal_strength -= 3
        
        # Moving Average Analysis
        if latest['close'] > latest['sma_20'] > latest['sma_50']:
            signals.append("Price Above Moving Averages - Bullish")
            signal_strength += 1
        elif latest['close'] < latest['sma_20'] < latest['sma_50']:
            signals.append("Price Below Moving Averages - Bearish")
            signal_strength -= 1
        
        # EMA Crossover
        if latest['ema_12'] > latest['ema_26'] and prev['ema_12'] <= prev['ema_26']:
            signals.append("EMA Golden Cross - Strong Long")
            signal_strength += 3
        elif latest['ema_12'] < latest['ema_26'] and prev['ema_12'] >= prev['ema_26']:
            signals.append("EMA Death Cross - Strong Short")
            signal_strength -= 3
        
        # Bollinger Bands Analysis
        if latest['close'] < latest['bb_lower']:
            signals.append("Price Below Lower Bollinger Band - Oversold")
            signal_strength += 1
        elif latest['close'] > latest['bb_upper']:
            signals.append("Price Above Upper Bollinger Band - Overbought")
            signal_strength -= 1
        
        # Stochastic Analysis
        if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:
            signals.append("Stochastic Oversold - Long Signal")
            signal_strength += 1
        elif latest['stoch_k'] > 80 and latest['stoch_d'] > 80:
            signals.append("Stochastic Overbought - Short Signal")
            signal_strength -= 1
        
        # Williams %R Analysis
        if latest['williams_r'] < -80:
            signals.append("Williams %R Oversold - Long Signal")
            signal_strength += 1
        elif latest['williams_r'] > -20:
            signals.append("Williams %R Overbought - Short Signal")
            signal_strength -= 1
        
        # Determine overall signal
        if signal_strength >= 3:
            overall_signal = "STRONG_LONG"
        elif signal_strength >= 1:
            overall_signal = "LONG"
        elif signal_strength <= -3:
            overall_signal = "STRONG_SHORT"
        elif signal_strength <= -1:
            overall_signal = "SHORT"
        else:
            overall_signal = "NEUTRAL"
        
        # Calculate entry, stop loss, and take profit levels
        current_price = latest['close']
        atr = latest['atr']
        
        if 'LONG' in overall_signal:
            entry_price = current_price
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        elif 'SHORT' in overall_signal:
            entry_price = current_price
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)
        else:
            entry_price = current_price
            stop_loss = 0
            take_profit = 0
        
        return {
            'signal': overall_signal,
            'strength': abs(signal_strength),
            'reasons': signals if signals else ['No clear signals'],
            'entry_price': round(entry_price, 4),
            'stop_loss': round(stop_loss, 4),
            'take_profit': round(take_profit, 4),
            'current_price': round(current_price, 4),
            'rsi': round(latest['rsi'], 2),
            'macd': round(latest['macd'], 6),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def analyze_symbol(self, symbol: str, interval: str = "5m") -> Dict:
        """
        Perform complete analysis for a symbol
        """
        logger.info(f"Analyzing {symbol} on {interval} timeframe")
        
        # Get historical data
        df = self.get_klines(symbol, interval=interval)
        
        if df.empty:
            return {
                'symbol': symbol,
                'error': 'Failed to fetch data'
            }
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Generate signals
        signals = self.generate_signals(df)
        
        return {
            'symbol': symbol,
            'analysis': signals,
            'data': df,
            'interval': interval
        }
    
    def analyze_all_symbols(self, interval: str = "5m") -> Dict:
        """
        Analyze all configured symbols with retry logic
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                # Add retry logic for better reliability
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        results[symbol] = self.analyze_symbol(symbol, interval=interval)
                        break  # Success, exit retry loop
                    except Exception as e:
                        if attempt == max_retries - 1:  # Last attempt
                            raise e
                        logger.warning(f"Attempt {attempt + 1} failed for {symbol}, retrying... Error: {e}")
                        time.sleep(1)  # Wait before retry
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol} after {max_retries} attempts: {e}")
                results[symbol] = {
                    'symbol': symbol,
                    'error': f"Failed to fetch data for {symbol}: {str(e)}"
                }
        
        return results 