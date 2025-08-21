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
        self.fallback_url = "https://api.coingecko.com/api/v3"
        self.symbols = ["BTCUSDT", "ETHUSDT"]
        self.use_fallback = False
        
        # Detect if we're in a restricted environment (like Streamlit Cloud)
        self.detect_restricted_environment()
    
    def detect_restricted_environment(self):
        """
        Detect if we're running in a restricted environment that blocks external APIs
        """
        try:
            # Check if we're in Streamlit Cloud or similar restricted environment
            import os
            if os.environ.get('STREAMLIT_SERVER_PORT') or os.environ.get('STREAMLIT_SERVER_ADDRESS'):
                logger.info("Detected Streamlit Cloud environment - will use fallback APIs if needed")
                self.use_fallback = True
        except Exception as e:
            logger.warning(f"Could not detect environment: {e}")
        
    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 200) -> pd.DataFrame:
        """
        Fetch historical kline data from Binance or fallback to CoinGecko
        """
        # If in restricted environment, use fallback directly
        if self.use_fallback:
            logger.info(f"Using CoinGecko fallback for {symbol} due to restricted environment")
            return self.get_klines_fallback(symbol, interval, limit)
        
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
            logger.error(f"Error fetching klines for {symbol} from Binance: {e}")
            # Try fallback to CoinGecko
            try:
                return self.get_klines_fallback(symbol, interval, limit)
            except Exception as fallback_error:
                logger.error(f"Error fetching klines for {symbol} from fallback: {fallback_error}")
                return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol from Binance or fallback to CoinGecko
        """
        # If in restricted environment, use fallback directly
        if self.use_fallback:
            logger.info(f"Using CoinGecko fallback for current price of {symbol} due to restricted environment")
            return self.get_current_price_fallback(symbol)
        
        try:
            url = f"{self.base_url}/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return float(data['price'])
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol} from Binance: {e}")
            # Try fallback to CoinGecko
            try:
                return self.get_current_price_fallback(symbol)
            except Exception as fallback_error:
                logger.error(f"Error fetching current price for {symbol} from fallback: {fallback_error}")
                return 0.0
    
    def get_klines_fallback(self, symbol: str, interval: str = "5m", limit: int = 200) -> pd.DataFrame:
        """
        Fallback method using CoinGecko API for historical data
        """
        try:
            # Convert Binance symbol to CoinGecko format
            symbol_mapping = {
                "BTCUSDT": "bitcoin",
                "ETHUSDT": "ethereum"
            }
            
            coin_id = symbol_mapping.get(symbol)
            if not coin_id:
                raise ValueError(f"Unsupported symbol for fallback: {symbol}")
            
            # Convert interval to days
            interval_days = {
                "5m": 1,    # 1 day for 5m data
                "15m": 3,   # 3 days for 15m data
                "1h": 7,    # 7 days for 1h data
                "4h": 30,   # 30 days for 4h data
                "1d": 365   # 1 year for 1d data
            }
            
            days = interval_days.get(interval, 7)
            
            url = f"{self.fallback_url}/coins/{coin_id}/ohlc"
            params = {
                "vs_currency": "usd",
                "days": days
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame format similar to Binance
            df_data = []
            for candle in data:
                timestamp, open_price, high, low, close_price = candle
                df_data.append({
                    'timestamp': timestamp,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close_price,
                    'volume': 0  # CoinGecko doesn't provide volume in OHLC
                })
            
            df = pd.DataFrame(df_data)
            
            # Convert timestamp
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            # Limit to requested number of rows
            df = df.tail(limit)
            
            logger.info(f"Successfully fetched {len(df)} rows from CoinGecko fallback for {symbol}")
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error in CoinGecko fallback for {symbol}: {e}")
            raise
    
    def get_current_price_fallback(self, symbol: str) -> float:
        """
        Fallback method using CoinGecko API for current price
        """
        try:
            # Convert Binance symbol to CoinGecko format
            symbol_mapping = {
                "BTCUSDT": "bitcoin",
                "ETHUSDT": "ethereum"
            }
            
            coin_id = symbol_mapping.get(symbol)
            if not coin_id:
                raise ValueError(f"Unsupported symbol for fallback: {symbol}")
            
            url = f"{self.fallback_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            price = data[coin_id]['usd']
            
            logger.info(f"Successfully fetched price from CoinGecko fallback for {symbol}: ${price}")
            return float(price)
            
        except Exception as e:
            logger.error(f"Error in CoinGecko fallback price for {symbol}: {e}")
            raise
    
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