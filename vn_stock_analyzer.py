#!/usr/bin/env python3
"""
Vietnamese Stock Market Analyzer
Provides technical analysis for Vietnamese stocks listed on HSX and HNX
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VNStockAnalyzer:
    """Analyzer for Vietnamese stock market with technical indicators"""
    
    def __init__(self):
        """Initialize the Vietnamese stock analyzer"""
        # Major Vietnamese stocks
        self.vn_stocks = {
            'VNM.VN': 'Vinamilk',
            'VCB.VN': 'Vietcombank', 
            'VIC.VN': 'Vingroup',
            'HPG.VN': 'Hoa Phat Group',
            'TCB.VN': 'Techcombank',
            'MSN.VN': 'Masan Group',
            'FPT.VN': 'FPT Corporation',
            'MWG.VN': 'Mobile World',
            'GAS.VN': 'PV Gas',
            'CTG.VN': 'VietinBank',
            'NVL.VN': 'NovaLand',
            'TPB.VN': 'Tien Phong Bank',
            'HHV.VN': 'Hoa Hao Vinamilk',
            'VJC.VN': 'VietJet Aviation',
            'VND.VN': 'VN Direct Securities'
        }
        
        # Vietnamese market specific intervals mapping
        self.interval_mapping = {
            '5m': '5m',
            '15m': '15m', 
            '1h': '1h',
            '4h': '1h',  # Will resample 1h to 4h
            '1d': '1d'
        }
    
    def get_vn_stock_data(self, symbol, interval='1h', period='60d'):
        """
        Fetch Vietnamese stock data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'VNM.VN')
            interval: Time interval ('5m', '15m', '1h', '4h', '1d')
            period: Data period ('60d', '30d', '7d', etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            yf_interval = self.interval_mapping.get(interval, '1h')
            
            # Adjust period based on interval for Vietnamese market hours
            if interval in ['5m', '15m']:
                period = '7d'  # Shorter period for intraday
            elif interval == '1h':
                period = '30d'
            elif interval == '4h':
                period = '60d'
            else:  # 1d
                period = '1y'
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=yf_interval)
            
            if df.empty:
                logger.error(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Clean column names
            df.columns = [col.lower() for col in df.columns]
            
            # Handle 4h resampling from 1h data
            if interval == '4h' and yf_interval == '1h':
                df = df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
            
            # Convert prices to thousands VND for easier reading
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col] / 1000
            
            logger.info(f"Fetched {len(df)} data points for {symbol} ({interval})")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators optimized for Vietnamese stocks
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with technical indicators added
        """
        if df.empty or len(df) < 50:
            return df
        
        try:
            # Moving Averages (Vietnamese market typically uses 10, 20, 50)
            df['sma_10'] = ta.trend.sma_indicator(df['close'], window=10)
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # RSI (14-period standard for Vietnamese market)
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['macd_signal'] = ta.trend.macd_signal(df['close'])
            df['macd_histogram'] = ta.trend.macd_diff(df['close']) - ta.trend.macd_signal(df['close'])
            
            # Bollinger Bands (20-period, 2 std dev)
            df['bb_upper'] = ta.volatility.bollinger_hband(df['close'])
            df['bb_middle'] = ta.volatility.bollinger_mavg(df['close'])
            df['bb_lower'] = ta.volatility.bollinger_lband(df['close'])
            
            # Stochastic Oscillator
            df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
            
            # Williams %R
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # ATR (Average True Range)
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Volume indicators
            df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price Rate of Change
            df['roc'] = ta.momentum.roc(df['close'], window=12)
            
            # Money Flow Index (useful for Vietnamese market)
            df['mfi'] = ta.volume.money_flow_index(
                df['high'], df['low'], df['close'], df['volume']
            )
            
            # On-Balance Volume
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def calculate_vietnamese_market_signals(self, df):
        """
        Calculate Vietnamese market-specific trading signals
        
        Args:
            df: DataFrame with technical indicators
            
        Returns:
            Dictionary with price action signals
        """
        if df.empty or len(df) < 20:
            return {}
        
        try:
            current = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else current
            
            signals = {}
            
            # Vietnamese market trend analysis
            # SMA trend (10 > 20 > 50 = strong uptrend)
            sma_trend = 0
            if current['sma_10'] > current['sma_20'] > current['sma_50']:
                sma_trend = 2  # Strong uptrend
            elif current['sma_10'] > current['sma_20']:
                sma_trend = 1  # Mild uptrend
            elif current['sma_10'] < current['sma_20'] < current['sma_50']:
                sma_trend = -2  # Strong downtrend
            elif current['sma_10'] < current['sma_20']:
                sma_trend = -1  # Mild downtrend
            
            signals['sma_trend'] = sma_trend
            
            # Price position relative to SMA
            price_above_sma20 = current['close'] > current['sma_20']
            price_above_sma50 = current['close'] > current['sma_50']
            
            # RSI conditions (Vietnamese market often uses 30/70 levels)
            rsi_oversold = current['rsi'] < 30
            rsi_overbought = current['rsi'] > 70
            rsi_neutral = 30 <= current['rsi'] <= 70
            
            # MACD momentum
            macd_bullish = current['macd'] > current['macd_signal']
            macd_improving = current['macd'] > prev['macd']
            
            # Bollinger Bands position
            bb_squeeze = (current['bb_upper'] - current['bb_lower']) / current['bb_middle'] < 0.1
            bb_breakout_up = current['close'] > current['bb_upper']
            bb_breakout_down = current['close'] < current['bb_lower']
            
            # Volume confirmation
            volume_confirmation = current['volume_ratio'] > 1.2
            
            # Stochastic momentum
            stoch_oversold = current['stoch_k'] < 20 and current['stoch_d'] < 20
            stoch_overbought = current['stoch_k'] > 80 and current['stoch_d'] > 80
            
            signals.update({
                'price_above_sma20': price_above_sma20,
                'price_above_sma50': price_above_sma50,
                'rsi_oversold': rsi_oversold,
                'rsi_overbought': rsi_overbought,
                'rsi_neutral': rsi_neutral,
                'macd_bullish': macd_bullish,
                'macd_improving': macd_improving,
                'bb_squeeze': bb_squeeze,
                'bb_breakout_up': bb_breakout_up,
                'bb_breakout_down': bb_breakout_down,
                'volume_confirmation': volume_confirmation,
                'stoch_oversold': stoch_oversold,
                'stoch_overbought': stoch_overbought
            })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error calculating Vietnamese market signals: {e}")
            return {}
    
    def generate_signals(self, df, symbol):
        """
        Generate buy/sell signals for Vietnamese stocks
        
        Args:
            df: DataFrame with technical indicators
            symbol: Stock symbol
            
        Returns:
            Dictionary with analysis results
        """
        if df.empty:
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'current_price': 0,
                'reasons': ['No data available']
            }
        
        try:
            current = df.iloc[-1]
            market_signals = self.calculate_vietnamese_market_signals(df)
            
            # Initialize scoring
            bullish_score = 0
            bearish_score = 0
            reasons = []
            
            # SMA Trend Analysis (Weight: 3)
            sma_trend = market_signals.get('sma_trend', 0)
            if sma_trend >= 2:
                bullish_score += 3
                reasons.append("Strong uptrend: SMA 10 > 20 > 50")
            elif sma_trend == 1:
                bullish_score += 2
                reasons.append("Mild uptrend: SMA 10 > 20")
            elif sma_trend <= -2:
                bearish_score += 3
                reasons.append("Strong downtrend: SMA 10 < 20 < 50")
            elif sma_trend == -1:
                bearish_score += 2
                reasons.append("Mild downtrend: SMA 10 < 20")
            
            # Price Position (Weight: 2)
            if market_signals.get('price_above_sma20') and market_signals.get('price_above_sma50'):
                bullish_score += 2
                reasons.append("Price above key moving averages")
            elif not market_signals.get('price_above_sma20') and not market_signals.get('price_above_sma50'):
                bearish_score += 2
                reasons.append("Price below key moving averages")
            
            # RSI Analysis (Weight: 2)
            if market_signals.get('rsi_oversold'):
                bullish_score += 2
                reasons.append(f"RSI oversold at {current['rsi']:.1f}")
            elif market_signals.get('rsi_overbought'):
                bearish_score += 2
                reasons.append(f"RSI overbought at {current['rsi']:.1f}")
            elif market_signals.get('rsi_neutral'):
                reasons.append(f"RSI neutral at {current['rsi']:.1f}")
            
            # MACD Analysis (Weight: 2)
            if market_signals.get('macd_bullish') and market_signals.get('macd_improving'):
                bullish_score += 2
                reasons.append("MACD bullish with improving momentum")
            elif not market_signals.get('macd_bullish'):
                bearish_score += 1
                reasons.append("MACD bearish signal")
            
            # Bollinger Bands (Weight: 1)
            if market_signals.get('bb_breakout_up'):
                bullish_score += 1
                reasons.append("Bollinger Bands upward breakout")
            elif market_signals.get('bb_breakout_down'):
                bearish_score += 1
                reasons.append("Bollinger Bands downward breakout")
            elif market_signals.get('bb_squeeze'):
                reasons.append("Bollinger Bands squeeze - potential breakout")
            
            # Volume Confirmation (Weight: 1)
            if market_signals.get('volume_confirmation'):
                if bullish_score > bearish_score:
                    bullish_score += 1
                    reasons.append("Strong volume confirmation")
                else:
                    bearish_score += 1
                    reasons.append("High volume on weakness")
            
            # Stochastic (Weight: 1)
            if market_signals.get('stoch_oversold'):
                bullish_score += 1
                reasons.append("Stochastic oversold")
            elif market_signals.get('stoch_overbought'):
                bearish_score += 1
                reasons.append("Stochastic overbought")
            
            # Determine signal
            net_score = bullish_score - bearish_score
            strength = min(10, max(1, abs(net_score)))
            
            if net_score >= 6:
                signal = 'STRONG_LONG'
            elif net_score >= 3:
                signal = 'LONG'
            elif net_score <= -6:
                signal = 'STRONG_SHORT'
            elif net_score <= -3:
                signal = 'SHORT'
            else:
                signal = 'NEUTRAL'
            
            # Calculate entry/exit levels
            atr = current['atr']
            current_price = current['close']
            
            if signal in ['LONG', 'STRONG_LONG']:
                entry_price = current_price
                stop_loss = current_price - (2 * atr)
                take_profit = current_price + (3 * atr)
            elif signal in ['SHORT', 'STRONG_SHORT']:
                entry_price = current_price
                stop_loss = current_price + (2 * atr)
                take_profit = current_price - (3 * atr)
            else:
                entry_price = current_price
                stop_loss = 0
                take_profit = 0
            
            return {
                'signal': signal,
                'strength': strength,
                'current_price': current_price,
                'entry_price': entry_price,
                'stop_loss': max(0, stop_loss),
                'take_profit': max(0, take_profit),
                'rsi': current['rsi'],
                'macd': current['macd'],
                'atr': atr,
                'volume_ratio': current['volume_ratio'],
                'mfi': current.get('mfi', 0),
                'reasons': reasons,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score,
                'company_name': self.vn_stocks.get(symbol, symbol)
            }
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'current_price': 0,
                'reasons': [f'Error in analysis: {str(e)}']
            }
    
    def analyze_symbol(self, symbol, interval='1h'):
        """
        Analyze a single Vietnamese stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'VNM.VN')
            interval: Time interval
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get stock data
            df = self.get_vn_stock_data(symbol, interval)
            
            if df.empty:
                return {
                    'symbol': symbol,
                    'error': 'No data available'
                }
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Generate signals
            analysis = self.generate_signals(df, symbol)
            
            return {
                'symbol': symbol,
                'analysis': analysis,
                'data': df,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e)
            }
    
    def analyze_all_symbols(self, interval='1h', limit=None):
        """
        Analyze all Vietnamese stocks
        
        Args:
            interval: Time interval
            limit: Maximum number of stocks to analyze (None for all)
            
        Returns:
            Dictionary with analysis results for all symbols
        """
        results = {}
        symbols_to_analyze = list(self.vn_stocks.keys())
        
        if limit:
            symbols_to_analyze = symbols_to_analyze[:limit]
        
        logger.info(f"Analyzing {len(symbols_to_analyze)} Vietnamese stocks with {interval} interval")
        
        for symbol in symbols_to_analyze:
            logger.info(f"Analyzing {symbol} ({self.vn_stocks[symbol]})")
            results[symbol] = self.analyze_symbol(symbol, interval)
        
        return results

if __name__ == "__main__":
    # Test the analyzer
    analyzer = VNStockAnalyzer()
    
    print("🇻🇳 Vietnamese Stock Market Analyzer Test")
    print("=" * 50)
    
    # Test single stock
    result = analyzer.analyze_symbol('VNM.VN', '1h')
    
    if 'error' not in result:
        analysis = result['analysis']
        print(f"\n📊 {analysis['company_name']} (VNM.VN) Analysis:")
        print(f"  Signal: {analysis['signal']}")
        print(f"  Strength: {analysis['strength']}/10")
        print(f"  Current Price: {analysis['current_price']:,.1f}K VND")
        print(f"  RSI: {analysis['rsi']:.1f}")
        print("  Reasons:")
        for reason in analysis['reasons'][:3]:
            print(f"    • {reason}")
    else:
        print(f"❌ Error: {result['error']}")
