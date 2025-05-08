import ccxt
import pandas as pd
import time
import os
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('BYBIT_API_KEY')
API_SECRET = os.getenv('BYBIT_SECRET_KEY')

# Initialize exchange (Bybit example)
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,  # Avoid rate limits
    'options': {
        'adjustForTimeDifference': True,  # Auto-sync time (recommended)
        'recvWindow': 10000,  # Increase to 10 seconds (default: 5000 ms)
    },
})

# Trading parameters
SYMBOL = "BTC/USDT:USDT"  # Forex CFD example: "EUR/USD" (if available)
TIMEFRAME = "1h"     # 1-hour candles
TRADE_AMOUNT = 10   # USD to trade per order
TAKE_PROFIT = 0.10  # 10% take profit
STOP_LOSS = 0.01    # 1% stop loss

def fetch_data(symbol, timeframe, limit=100):
    """Fetch OHLCV (Open-High-Low-Close-Volume) data."""
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def get_current_price():
    ticker = exchange.fetch_ticker(SYMBOL)
    return ticker['last']

def check_open_position():
    """Check if we have an open position and return its details"""
    positions = exchange.fetch_positions([SYMBOL])
    for pos in positions:
        if pos['symbol'] == SYMBOL and pos['contracts'] >  0:
            return pos
    return None

def calculate_pnl(position, current_price):
    """Calculate unrealized profit/loss percentage"""
    entry_price = float(position['entryPrice'])
    size = float(position['contracts'])
    side = position['side']
    
    if side == 'long':
        return (current_price - entry_price) / entry_price
    elif side == 'short':
        return (entry_price - current_price) / entry_price
    return 0

def close_position(position):
    """Close the specified position"""
    side = 'sell' if position['side'] == 'long' else 'buy'
    try:
        exchange.create_market_order(
            SYMBOL,
            side,
            abs(float(position['contracts'])))
        print(f"Closed {position['side']} position")
    except Exception as e:
        print(f"Error closing position: {e}")

def moving_average_strategy(df, short_window=5, long_window=20):
    """Simple Moving Average Crossover Strategy."""
    df["sma_short"] = df["close"].rolling(short_window).mean()
    df["sma_long"] = df["close"].rolling(long_window).mean()
    
    # Buy signal: Short SMA > Long SMA
    # Sell signal: Short SMA < Long SMA
    df["signal"] = 0
    df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1  # Buy
    df.loc[df["sma_short"] < df["sma_long"], "signal"] = -1 # Sell
    return df

def execute_trade(symbol, side, amount):
    """Place a market order."""
    try:
        print(f"Placing {side} order for {amount} {symbol}")
        order = exchange.create_market_order(symbol, side, amount)
        print(f"Order executed: {order}")
    except Exception as e:
        print(f"Trade failed: {e}")

# markets = exchange.load_markets()

# exchange.verbose = True  # uncomment for debugging purposes

# params = {'stop_px': 9750, 'base_price': 11152}
# order = exchange.create_order('BTC/USDT', 'market', 'buy', 911, None, params)

# pprint(order)



def run_bot():
    print("Starting trading bot...")
    balance = exchange.fetch_balance()
    usdt_balance = balance['USDT']['free']  # Available USDT
    print(f"Available USDT: {usdt_balance}")
    while True:
        try:
            # Check existing positions
            position = check_open_position()
            current_price = get_current_price()
            
            # Manage open position
            # if position:
            #     pnl = calculate_pnl(position, current_price)
            #     print(f"Current PnL: {pnl*100:.2f}%")
                
            #     # Close position if profit/loss target hit
            #     if pnl >= TAKE_PROFIT or pnl <= -STOP_LOSS:
            #         close_position(position)
            #         continue  # Skip new signals until next cycle
            
            # Fetch new data and check signals
            # ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)
            # df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            # df = moving_average_strategy(df)
            # signal = df['signal'].iloc[-1]
            
            # # Execute new trade if no position is open
            # if not position:
            #     if signal == 1:
            #         exchange.create_market_order(SYMBOL, 'buy', TRADE_AMOUNT)
            #         print("Opened long position")
            #     elif signal == -1:
            #         exchange.create_market_order(SYMBOL, 'sell', TRADE_AMOUNT)
            #         print("Opened short position")
            
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\nStopping bot...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

