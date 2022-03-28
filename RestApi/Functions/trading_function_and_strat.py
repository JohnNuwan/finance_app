#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : K.Azazel
# Created Date: 27/03/2022
# =============================================================================
"""
    Docstring :
            Fichier Contenant les fonction de tradion principal 
                    recuperation data
                    recuperation Past data
                    Calcule Support / Resistance
                    Open Order sur la PlatFrom MetaTrader5
"""
# =============================================================================
# Imports
# =============================================================================

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

def ichi(name,timeframe,num_bars):
    route_data = f"{url}/OHLC/{name}/{timeframe}/{num_bars}"
    r2 = requests.get(route_data)
    data = json.loads(r2.text)
    df = pd.read_json(data)


    nine_periodf_high = df['high'].rolling(window= 9).max()
    nine_periodf_low = df['low'].rolling(window= 9).min()

    periodf26_high = df['high'].rolling(window=26).max()
    periodf26_low = df['low'].rolling(window=26).min()


    df['tenkan_sen'] = (nine_periodf_high + nine_periodf_low) /2

    # Kijun-sen (Base Line): (26-periodf high + 26-periodf low)/2))
    df['kijun_sen'] = (periodf26_high + periodf26_low) / 2
    df['prev_kijun_sen'] = df['kijun_sen'].shift(1)
    df['prev_tenkan_sen'] = df['tenkan_sen'].shift(1)

    # Senkou Span A (Leadfing Span A): (Conversion Line + Base Line)/2))
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    # Senkou Span B (Leadfing Span B): (52-periodf high + 52-periodf low)/2))
    periodf52_high = df['high'].rolling(window=52).max()
    periodf52_low = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((periodf52_high + periodf52_low) / 2).shift(52)

    d = df.copy()
    d['chikou_span'] = d['close'].shift(-26)
    # d.dropna(inplace=True)
    d['above_cloud'] = 0
    d['above_cloud'] = np.where((d['low'] > d['senkou_span_a'])  & (d['low'] > d['senkou_span_b'] ), 1, d['above_cloud'])
    d['above_cloud'] = np.where((d['high'] < d['senkou_span_a']) & (d['high'] < d['senkou_span_b']), -1, d['above_cloud'])
    d['A_above_B'] = np.where((d['senkou_span_a'] > d['senkou_span_b']), 1, -1)
    d['tenkan_kiju_cross'] = np.NaN
    d['tenkan_kiju_cross'] = np.where((d['tenkan_sen'].shift(1) <= d['kijun_sen'].shift(1)) & (d['tenkan_sen'] > d['kijun_sen']), 1, d['tenkan_kiju_cross'])
    d['tenkan_kiju_cross'] = np.where((d['tenkan_sen'].shift(1) >= d['kijun_sen'].shift(1)) & (d['tenkan_sen'] < d['kijun_sen']), -1, d['tenkan_kiju_cross'])
    d['price_tenkan_cross'] = np.NaN
    d['price_tenkan_cross'] = np.where((d['open'].shift(1) <= d['tenkan_sen'].shift(1)) & (d['open'] > d['tenkan_sen']), 1, d['price_tenkan_cross'])
    d['price_tenkan_cross'] = np.where((d['open'].shift(1) >= d['tenkan_sen'].shift(1)) & (d['open'] < d['tenkan_sen']), -1, d['price_tenkan_cross'])
    d['buy'] = np.NaN
    d['buy'] = np.where((d['above_cloud'].shift(1) == 1) & (d['A_above_B'].shift(1) == 1) & ((d['tenkan_kiju_cross'].shift(1) == 1) | (d['price_tenkan_cross'].shift(1) == 1)), 1, d['buy'])
    d['buy'] = np.where(d['tenkan_kiju_cross'].shift(1) == -1, 0, d['buy'])
    # d['buy'].ffill(inplace=True)

    d['sell'] = np.NaN
    d['sell'] = np.where((d['above_cloud'].shift(1) == -1) & (d['A_above_B'].shift(1) == -1) & ((d['tenkan_kiju_cross'].shift(1) == -1) | (d['price_tenkan_cross'].shift(1) == -1)), -1, d['sell'])
    d['sell'] = np.where(d['tenkan_kiju_cross'].shift(1) == 1, 0, d['sell'])
    # d['sell'].ffill(inplace=True)
    d['position'] = d['buy'] + d['sell']
    d['stock_returns'] = np.log(d['open']) - np.log(d['open'].shift(1))
    d['strategy_returns'] = d['stock_returns'] * d['position']
    # d[['stock_returns','strategy_returns']].cumsum().plot(figsize=(15,8))

    # print(d.tail(2))

    data  = d.fillna(0, inplace=False)
    return data
