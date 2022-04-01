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

from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich.table import Table
from rich import box

import json
import requests

# Partie Definition Console Promt
custom_theme = Theme({
	"info": "dim cyan",
	"good": "bold yellow",
	"action": "dim yellow",
	"separate": "dim red",
	"warning": "magenta",
	"danger": "bold red"
})
cs = Console(theme=custom_theme)


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


def calc_dif(df):
    """
    CALCUL D'UNE DIFFÉRENCE EN POURCENTAGE

    Augmenter ou diminuer un montant de 1% signifie augmenter ou diminuer ce montant d'une certaine proportion.
    Les pourcentages sont calculés sur une base de 100, c'est pourquoi on parle de pourCENTage.
    (Il existe également d'autres bases de calcul, comme une base de 24 pour un jour ou une base de 60 pour une heure ou une minute.)
    Pour augmenter ou diminuer un montant de 1%, il faut définir :
    V1 : la valeur de départ, soit le montant de base que l'on veut augmenter ou diminuer ;
    V2 : la valeur finale, soit le nouveau montant après l'augmentation ou la diminution.
    La formule pour calculer le pourcentage de l'augmentation ou de la diminution est :
    Différence (en %) = ((V2 - V1) / V1) x 100 
    """
    V2   = df.price_current
    V1   = df.price_open
    Diff = 0
    if df.type == 0: 
        Diff = ((V2 - V1 )/V1)*100
        # print("Chang\t:",Diff, "%")
        return Diff

    if df.type == 1: 
        Diff = ((V1 - V2 )/V2)*100
        # print("Chang\t:",Diff, "%")
        return Diff


def pips(df):

    if str(df.price_open).index('.') >= 3:  # JPY pair
        multiplier = 0.001
    else:
        multiplier = 0.0001

    pips = round((df.price_current - df.price_open) / multiplier)
    return int(pips)


def engulfing(df):

    
    df["Candle way"] = -1
    df.loc[(df["open"] - df["close"]) < 0, "Candle way"] = 1
    df["amplitude"] = np.abs(df["close"] - df["open"])
    
    
    buy =(df["Candle way"].shift(3).iloc[-1] == -1) and\
        (df["Candle way"].shift(2).iloc[-1] == -1) and\
        (df["Candle way"].shift(1).iloc[-1] == -1) and\
        (df["Candle way"].iloc[-1] == 1) and\
        (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
        (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
        (df["amplitude"].shift(1).iloc[-1]*1.5 < df["amplitude"].iloc[-1])
    
    
    
    sell = (df["Candle way"].shift(3).iloc[-1] == 1) and\
       (df["Candle way"].shift(2).iloc[-1] == 1) and\
       (df["Candle way"].shift(1).iloc[-1] == 1) and\
       (df["Candle way"].iloc[-1] == -1) and\
       (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
       (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
       (df["amplitude"].shift(1).iloc[-1] * 1.5< df["amplitude"].iloc[-1])
    

    return {"Buy":buy, "Sell":sell}

def chek_take_position(symbol,comment,Type):
	url = f"http://{host}:{port}"

	route_position = "/positions_en_court"
	url = f"{url}{route_position}"
	cs.log(url)
	count = 0
	volume_count = 0

	tt_pips = 0
	profit = 0
	tt_change = 0
	itme_now = datetime.now()
	recv_data = requests.get(url)
	encode_data = json.loads(recv_data.text)
	# cs.log(encode_data)
	df = pd.read_json(encode_data)
	list_frame = []

	df.drop(columns=['external_id','time_msc', 'reason','time_update','time_update_msc'],inplace=True)
	df['time'] = pd.to_datetime(df['time'], unit='s')
	df.set_index(df['time'],inplace=True)
	df["pct_chang"] =  df.apply(lambda row: calc_dif(row),axis=1)
	df["Pips"] =  df.apply(lambda row: pips(row),axis=1)

	print(df)
	# symbol_df_filtre = pd.DataFrame()

	for row in df.itertuples():
		# print(f"{row.symbol}      {row.type}      {row.comment}      {row.profit}      {row.volume}")
		if row.symbol == symbol:#
			# print(row)
			if row.comment == comment:
				if row.type == Type:
					volume_count += row.volume
					profit += row.profit
					tt_change += row.pct_chang
					tt_pips += row.Pips
					print(f"{row.symbol} {row.type} {row.ticket} Changement\t:\t",calc_dif(row))
					count +=1

	data_send = {
			"Name": symbol,
			"Type":Type,
			"Total":count,
			'TT_Volume': volume_count,
			"profit": profit,
			"TT_Change": tt_change,
			"TT_Pips" : tt_pips
	}
	return data_send
				# # last_time = row.index
				# data_check = {
				#       "time" : row.time,
				#       "Name": symbol,
				#       "Nb Pos" : count,
				#       "Lot" : volume_count,
				#       "Type" : Type
				#   }
				# # df = pd.DataFrame(data_check)
				# print(data_check)
				# return data_check#df.to_json()
		
		# else :
			# return "Note Data"





def splite_reverse_position(name,Type,comment):
	url = f"http://{host}:{port}"
	route_position = "/positions_en_court"
	url = f"{url}{route_position}"
	cs.log(url)	
	count = 0
	volume_count = 0

	tt_pips = 0
	profit = 0
	tt_change = 0
	itme_now = datetime.now()
	recv_data = requests.get(url)
	encode_data = json.loads(recv_data.text)
	# cs.log(encode_data)
	df = pd.read_json(encode_data)
	list_frame = []

	df.drop(columns=['external_id','time_msc', 'reason','time_update','time_update_msc'],inplace=True)
	df['time'] = pd.to_datetime(df['time'], unit='s')
	df.set_index(df['time'],inplace=True)
	df["pct_chang"] =  df.apply(lambda row: calc_dif(row),axis=1)
	df["Pips"] =  df.apply(lambda row: pips(row),axis=1)
	for row in df.itertuples():
		# if row.symbol != name:
		# 	cs.print("Not Good",style='warning')
		if row.symbol == name and row.comment == comment:
			if row.type == Type:
				print(row.pct_chang())
				pass
				# print("Same Type")
				# print(f"Symbol : {row.symbol}\nType : {row.type}\nComment : {row.comment}\nProfit : {row.profit}\nPips : {row.Pips}")
			else:
				print("-"*30)
				cs.print("Good",style="good")
				cs.print("Inverse symbol", style='danger')
				print(f"Symbol : {row.symbol}\nType : {row.type}\nVolume : {row.volume}\nComment : {row.comment}\nProfit : {row.profit}\nPips : {row.Pips}")
				cs.print("\nSPLITE OR CLOSE POSITIONS!!",justify='center')
				if row.profit < 0 or row.volume == 0.01:
					cs.print("CLOSE ", justify='center',style='danger')
					close_position(row.symbol,row.type,row.identifier,new_sl,row.volume,'Close Reverse')

				if row.profit > 0:
						cs.print("Splite",justify='center', style='info')
						cs.print("Move SL To BE + 1%",justify='left', style='info')
						print(f"Init SL : {row.sl}")
						new_sl = (row.price_current + row.price_open)/2
						print(f"New SL : {new_sl}")
						split_position(row.symbol,row.type,row.identifier,row.volume,'Teste API SPLIT')
						change_sl(row.symbol,row.type,row.identifier,new_sl,"Split")
						return True




def close_position(symbol,action,positions,lot,comment):
	mt5.initialize()
	print(symbol,action,positions,lot,comment)
	if action == 1:
		trade_type = mt5.ORDER_TYPE_BUY
		price = mt5.symbol_info_tick(symbol).ask
	elif action == 0 :
		trade_type = mt5.ORDER_TYPE_SELL
		price = mt5.symbol_info_tick(symbol).bid

	request={
		"action": mt5.TRADE_ACTION_DEAL,
		"symbol": symbol,
		"volume": lot,
		"type": trade_type,
		"position": positions,
		"price": price,
		"deviation": 20,
		"magic": 234000,
		"comment": comment,
		"type_time": mt5.ORDER_TIME_GTC,
		"type_filling": mt5.ORDER_FILLING_IOC,
	}
	# send a trading request
	result=mt5.order_send(request)
	print(result)
	requests.post("https://discord.com/api/webhooks/957993538971398164/QcgkgEaDYL8LStujoLQdTwf-utWR0Lu5OLcBslsGsgPqctqg1hM8z1RgqU8yuXi2TKzQ", json=request)
	if result.retcode != mt5.TRADE_RETCODE_DONE: 
		cs.print(f"Order closing failed: {result.retcode}",style='warning')#.format())

	else:
		cs.print("closed correctly","blue",style='info')

def change_sl(symbol,action,positions,sl,comment):
	mt5.initialize()

	print(f"{symbol} new_sl : {sl} % ")
	request = {
		"action": mt5.TRADE_ACTION_SLTP,
		"symbol": symbol,
		"type": action,
		"position": positions,
		"sl": sl,
		"deviation": 20,
		"magic": 666,
		"comment": comment,
		"type_time": mt5.ORDER_TIME_GTC,
		"type_filling": mt5.ORDER_FILLING_FOK,
		"ENUM_ORDER_STATE": mt5.ORDER_FILLING_IOC,
		}

	## perform the check and display the result 'as is'
	result = mt5.order_send(request)
	if result.retcode != mt5.TRADE_RETCODE_DONE:
		print("-"*60) 
		print(f"{row.symbol}\t:\n\t\tOrder Change failed: {result.retcode} \n\t\t Profit : \t{row.profit}$")
	else:
		print("Change correctly")




def split_position(symbol,action,positions,lot,comment):
	mt5.initialize()
	print(symbol,action,positions,lot,comment)
	if action == 1:
		trade_type = mt5.ORDER_TYPE_BUY
		price = mt5.symbol_info_tick(symbol).ask
	elif action == 0 :
		trade_type = mt5.ORDER_TYPE_SELL
		price = mt5.symbol_info_tick(symbol).bid

	request={
		"action": mt5.TRADE_ACTION_DEAL,
		"symbol": symbol,
		"volume": lot/2,
		"type": trade_type,
		"position": positions,
		"price": price,
		"deviation": 20,
		"magic": 234000,
		"comment": comment,
		"type_time": mt5.ORDER_TIME_GTC,
		"type_filling": mt5.ORDER_FILLING_IOC,
	}
	# send a trading request
	result=mt5.order_send(request)
	print(result)
	requests.post("https://discord.com/api/webhooks/957993538971398164/QcgkgEaDYL8LStujoLQdTwf-utWR0Lu5OLcBslsGsgPqctqg1hM8z1RgqU8yuXi2TKzQ", json=request)
	if result.retcode != mt5.TRADE_RETCODE_DONE: 
		cs.print(f"Order closing failed: {result.retcode}",style='warning')#.format())

	else:
		cs.print("closed correctly","blue",style='info')

#__________________________________________________
# Definition Serveur
host = "localhost"
port = 8095
debug = True
url = f"http://{host}:{port}"

#__________________________________________________

# name = "[DJI30]"

# splite_reverse_position(name=name,Type=1,comment="HOLD")