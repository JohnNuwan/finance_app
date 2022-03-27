

import os
import sys 

import MetaTrader5 as mt5

from rich import print
from rich.console import Console


import pandas as pd 
import numpy as np

import ta

from datetime import datetime 

import pytz

def get_data(name, timeframe, num_bars):
	try:
		TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']
		TIMEFRAME_DICT = {
			'M1': mt5.TIMEFRAME_M1,
			'M3': mt5.TIMEFRAME_M3,
			'M5': mt5.TIMEFRAME_M5,
			'M15': mt5.TIMEFRAME_M15,
			'M30': mt5.TIMEFRAME_M30,
			'H1': mt5.TIMEFRAME_H1,
			'H4': mt5.TIMEFRAME_H4,
			'D1': mt5.TIMEFRAME_D1,
			'W1': mt5.TIMEFRAME_W1,
			'MN1': mt5.TIMEFRAME_MN1,
		}
		timeframe = TIMEFRAME_DICT[timeframe]
		
		mt5.initialize()
		bars = mt5.copy_rates_from_pos(name, timeframe, 0, num_bars)
		df = pd.DataFrame(bars)
		df['time'] = pd.to_datetime(df['time'], unit='s')
		df.set_index(['time'], inplace=True)
		return df
		
	except Exception as e:
		print(f'Error :\n\n\t{e}')


def get_data_hist(name, timeframe, num_bars):
    try:
        TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']
        TIMEFRAME_DICT = {
            'M1': mt5.TIMEFRAME_M1,
            'M3': mt5.TIMEFRAME_M3,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1,
        }
        timeframe = TIMEFRAME_DICT[timeframe]
        
        mt5.initialize()
        # crée des objets 'datetime' dans le fuseau horaire UTC pour éviter l'implémentation d'un décalage de fuseau horaire local
        utc_from = datetime(2022, 1, 1)
        utc_to = datetime.now()
        # récupère des barres de USDJPY M5 dans l'intervalle 2020.01.10 00:00 - 2020.01.11 13:00 dans le fuseau horaire UTC
        rates = mt5.copy_rates_range(name, timeframe, utc_from, utc_to)
        # bars = mt5.copy_rates_from_pos(name, timeframe, 0, num_bars)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index(['time'], inplace=True)
        return df
        
    except Exception as e:
        print(f'Error :\n\n\t{e}')


def support_resistance(df, duration=5,spread=0):
    """THE DATAFRAME NEEDS TO HAVE the following column names: high, low, close"""

    # Support and resistance building
    df["support"] = np.nan
    df["resistance"] = np.nan

    df.loc[(df["low"].shift(5) > df["low"].shift(4)) &
        (df["low"].shift(4) > df["low"].shift(3)) &
        (df["low"].shift(3) > df["low"].shift(2)) &
        (df["low"].shift(2) > df["low"].shift(1)) &
        (df["low"].shift(1) > df["low"].shift(0)), "support"] = df["low"]


    df.loc[(df["high"].shift(5) < df["high"].shift(4)) &
    (df["high"].shift(4) < df["high"].shift(3)) &
    (df["high"].shift(3) < df["high"].shift(2)) &
    (df["high"].shift(2) < df["high"].shift(1)) &
    (df["high"].shift(1) < df["high"].shift(0)), "resistance"] = df["high"]


    # Create Simple moving average 30 days
    df["SMA fast"] = df["close"].rolling(30).mean()

    # Create Simple moving average 60 days
    df["SMA slow"] = df["close"].rolling(60).mean()

    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=10).rsi()

    # RSI yersteday
    df["rsi yersteday"] = df["rsi"].shift(1)

    # Create the signal
    df["signal"] = 0

    df["smooth resistance"] = df["resistance"].fillna(method="ffill")
    df["smooth support"] = df["support"].fillna(method="ffill")


    condition_1_buy = (df["close"].shift(1) < df["smooth resistance"].shift(1)) & \
                    (df["smooth resistance"]*(1+0.5/100) < df["close"])
    condition_2_buy = df["SMA fast"] > df["SMA slow"]

    condition_3_buy = df["rsi"] < df["rsi yersteday"]

    condition_1_sell = (df["close"].shift(1) > df["smooth support"].shift(1)) & \
                    (df["smooth support"]*(1+0.5/100) > df["close"])
    condition_2_sell = df["SMA fast"] < df["SMA slow"]

    condition_3_sell = df["rsi"] > df["rsi yersteday"]



    df.loc[condition_1_buy & condition_2_buy & condition_3_buy, "signal"] = 1
    df.loc[condition_1_sell & condition_2_sell & condition_3_sell, "signal"] = -1


    # Compute the profits
    df["pct"] = df["close"].pct_change(1)

    df["return"] = np.array([df["pct"].shift(i) for i in range(duration)]).sum(axis=0) * (df["signal"].shift(duration))
    df.loc[df["return"]==-1, "return"] = df["return"]-spread
    df.loc[df["return"]==1, "return"] = df["return"]-spread


    return df


def open_trade_buy(action, symbol, lot,  deviation, comment):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    try:
        print(symbol)
        mt5.initialize()
        symbol = f"{symbol}"
        symbol_info = get_info(symbol)
        ea_magic_number = 9986989
        if action == 'buy':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        elif action =='sell':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        point = mt5.symbol_info(symbol).point

        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": trade_type,
            "price": price,
            # "sl": price - sl_points * point,
            # "tp": price + tp_points * point,
            "deviation": deviation,
            "magic": ea_magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # send a trading request
        result = mt5.order_send(buy_request)
        # mt5.shutdown()  
        # sys.exit()      
        return True
    except Exception as e:
        print(e)

def get_info(symbol):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolinfo_py
    '''
   
    try:
         # get symbol properties
        info=mt5.symbol_info(symbol)
        return info
    except Exception as e:
        return e

