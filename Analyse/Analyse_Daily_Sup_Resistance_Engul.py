#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : K.Azazel
# Created Date: 28/03/2022
# =============================================================================
"""
	Docstring :
			Simple Script D'Init Fichier

"""
# =============================================================================
# Imports
# =============================================================================
import os  
import sys  

import requests
import json  

from config.config import *
from Functions.Discord_message import *

import time

import schedule

import pandas as pd
import numpy as np 


os.system('cls')


url = f"http://{host}:{port}"
print("Try to get Connection : "+url)
r = requests.get(url)
print(r.text)


name = "GOLD"#input('Enter Symbol Name : ')
timeframe = "D1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
# lot = input("Taille Lots :  ")
comment = f'Support_Ress'

list_name = ["USDCAD","GBPUSD",'EURUSD','USDJPY','[DAX40]','[DJI30]']
# route_position = f"{url}/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}"
# print(route_position)


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


def engulfing(df):
	
	# Import / Features engineering
	# df = MT5.get_data(symbol, 70, timeframe=mt5.TIMEFRAME_D1)
	
	
	df["Candle way"] = -1
	df.loc[(df["open"] - df["close"]) < 0, "Candle way"] = 1
	df["amplitude"] = np.abs(df["close"] - df["open"])
	
	
	buy = (df["Candle way"].shift(5).iloc[-1] == -1) and\
		(df["Candle way"].shift(4).iloc[-1] == -1) and\
		(df["Candle way"].shift(3).iloc[-1] == -1) and\
		(df["Candle way"].shift(2).iloc[-1] == -1) and\
		(df["Candle way"].shift(1).iloc[-1] == -1) and\
		(df["Candle way"].iloc[-1] == 1) and\
		(df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
		(df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
		(df["amplitude"].shift(1).iloc[-1]*1.5 < df["amplitude"].iloc[-1])
	
	
	
	sell = (df["Candle way"].shift(5).iloc[-1] == 1) and\
	   (df["Candle way"].shift(4).iloc[-1] == 1) and\
	   (df["Candle way"].shift(3).iloc[-1] == 1) and\
	   (df["Candle way"].shift(2).iloc[-1] == 1) and\
	   (df["Candle way"].shift(1).iloc[-1] == 1) and\
	   (df["Candle way"].iloc[-1] == -1) and\
	   (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
	   (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
	   (df["amplitude"].shift(1).iloc[-1] * 1.5< df["amplitude"].iloc[-1])
	

	return buy, sell

def worker(name,timeframe):
	# global num_bars
	# global url
	lot = 0.02
	triger_signal = 0
	comment = f'Support_Ress_Candels_{timeframe}'
	route_data = f"{url}/sup_res/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(route_data)
	print(r2)
	print(route_data)
	data = json.loads(r2.text)
	df = pd.read_json(data)
	# print(data)
	full_df = df.copy()
	print(full_df.tail())
	price = full_df['close'][-1]

	last_rsi = full_df['rsi'][-1]
	prev_rsi = full_df['rsi yersteday'][-1]

	last_sma_fast = full_df["SMA fast"][-1]
	last_sma_slow = full_df["SMA slow"][-1]

	last_res = full_df["smooth resistance"][-1]
	last_supp = full_df["smooth support"][-1]
	last_signal = full_df["signal"][-1]

	time_data = full_df.index[-1]

	data = {
			"time" : time_data,
			"name" : name,
			"timeframe" : timeframe,
			"Last resistance" : last_res,
			"Last support" : last_supp,
			"Last Price" : price,
			"Last RSI 7P" : last_rsi,
			"Prev RSI 7P" : prev_rsi,
			"SMA fast 10P" : last_sma_fast,
			"SMA slow 21P" : last_sma_slow,
			"Last_Signal" : last_signal,
	}

	recv_data = engulfing(df)
	buy, sell = engulfing(df)
	print(recv_data)
	print(buy,sell)
	if sell or buy == True:

		print("Candel")
		if (sell == True) and (last_signal == -1):
			print("Sell")
			route_position = f"{url}/open_position/{name}/{timeframe}/sell/{comment}/{lot}"
			print(route_position)
			r2 = requests.get(route_position)
			print(r2)

		if (buy == True) and (last_signal == 1):
			print("Buy")
			route_position = f"{url}/open_position/{name}/{timeframe}/buy/{comment}/{lot}"
			print(route_position)
			r2 = requests.get(route_position)
			print(r2)

	"""
	if last_signal == 1:
		print("Buy")
		route_position = f"{url}/open_position/{name}/{timeframe}/buy/{comment}/{lot}"
		print(route_position)
		r2 = requests.get(route_position)
		print(r2)

	if last_signal == -1:
		print("Sell")
		route_position = f"{url}/open_position/{name}/{timeframe}/sell/{comment}/{lot}"
		print(route_position)
		r2 = requests.get(route_position)
		print(r2)
	"""

	return data

# for timeframe in list_ut:		
# process = worker(name,timeframe)

# data = pd.Series(process).to_string()
# print(data)

# message_analyse(data,daily_webhook)


def worker_Daily():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'D1')

		data = pd.Series(process).to_string()
		print(data)

		message_analyse(data,daily_webhook)

def worker_weekly():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'W1')

		data = pd.Series(process).to_string()
		print(data)

		message_analyse(data,weekly_webhook)

def worker_intra():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'M30')

		data = pd.Series(process).to_string()
		print(data)

		message_analyse(data,intra_webhook)


def worker_intra_m15():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'M15')

		data = pd.Series(process).to_string()
		print(data)

		# message_analyse(data,intra_webhook)


def worker_scalp_m5():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'M5')

		data = pd.Series(process).to_string()
		print(data)

		# message_analyse(data,intra_webhook)


def worker_scalp_m3():
	global timeframe
	global list_name
	for name in list_name:
		process = worker(name,'M3')

		data = pd.Series(process).to_string()
		print(data)



# schedule.every(1).minutes.do(worker_intra)
schedule.every(5).minutes.do( worker_scalp_m5)
schedule.every(15).minutes.do(worker_intra_m15)
schedule.every(30).minutes.do(worker_intra)
schedule.every().day.do(worker_Daily)
schedule.every().weeks.do(worker_weekly)

while True:
	try:
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)