#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : K.Azazel
# Created Date: 27/03/2022
# =============================================================================
"""
	Docstring :
			Serveur RestAPI 

"""
# =============================================================================
# Imports
# =============================================================================


import os
import sys 


from fastapi import FastAPI, Request
import uvicorn

import MetaTrader5 as mt5

from rich import print
from rich.console import Console


import pandas as pd 
import numpy as np


from datetime import datetime 

import seaborn as sns
import matplotlib.pyplot as plt

import pytz

import ta 

from art import *

from config.config import *
from Functions.trading_function_and_strat import *


os.system('cls')
banner()

# print(os.getcwd())
file = open("./config/MASTER_KEY.key", "r")
MASTER_KEY =  file.read()

# sys.exit()
app = FastAPI()

sur_achat = 70
sur_vente = 30

path_ohlc = "./OHLC"
if not os.path.exists(path_ohlc):
	os.makedirs(path_ohlc)

@app.get('/')
async def home( request: Request):
	return {'status': 1, 'message': 'ok', 'Serveur': prog_name,"Description":description}
	# return {"Hello":"World" , "client_host": client_host}


@app.get('/positions_en_court')
async def teste():
	mt5.initialize()
	account_info=mt5.account_info()
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("Total Positions {}".format(len(usd_positions)))
		# display these positions as a table using pandas.DataFrame
		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
		print(df)
		return df.to_json()


@app.get('/position_total')
async def position_total():
	print('Chargement route position_total')
	mt5.initialize()
	account_info=mt5.account_info()
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("Total Positions {}".format(len(usd_positions)))
		return {"Total Positions" : len(usd_positions)}


# 

@app.get('/OHLC/{name}/{timeframe}/{num_bars}')
async def ohlc(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	return df.to_json()


@app.get('/OHLC_hist/{name}/{timeframe}/{num_bars}')
async def ohlc(name:str,timeframe:str,num_bars:int):
	df =  get_data_hist(name, timeframe, num_bars)
	return df

@app.get('/sup_res/{name}/{timeframe}/{num_bars}')
async def sup_res(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	data = support_resistance(df, duration=6)
	return data.to_json()


@app.get('/stochc/{name}/{timeframe}/{num_bars}')
async def stoch(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	print(df)
	#Create the "L14" column in the DataFrame
	df['L14'] = df['low'].rolling(window=14).min()
	#Create the "H14" column in the DataFrame
	df['H14'] = df['high'].rolling(window=14).max()
	#Create the "%K" column in the DataFrame
	df['%K'] = 100*((df['close'] - df['L14']) / (df['H14'] - df['L14']) )
	#Create the "%D" column in the DataFrame
	df['%D'] = df['%K'].rolling(window=3).mean()

	buy_entry = 0
	sell_entry = 0
	ovre_buy = 80
	over_sell = 20
	triger = 0

	if (df['%K'][-1] < df['%D'][-1])  & (df['%D'][-1] >= ovre_buy):
		triger = -1
		print("Sell")
	
	if (df['%K'][-1] > df['%D'][-1]) & (df['%D'][-1] <= over_sell):
		triger = 1
		print("buy")
	
	data = {
		"time" : df.index[-1],
		"name": name,
		"TimeFrame":timeframe,
		"Triger": triger,
		"Last %K": df['%K'][-1],
		"Last %D": df['%D'][-1]
	}
	
	print("\n\t","-"*30)
	print(data)
	return data#df.to_json()

@app.get('/ichimoku/{name}/{timeframe}/{num_bars}')
async def teste(name:str,timeframe:str,num_bars:int):
	data = ichi(name,timeframe,num_bars)
	return data
	

@app.get('/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}')
async def open_position(name:str,timeframe:str,Type:str,comment:str,lot:float):
	# print("Essai Ouverture")
	# # verif = chek_take_position(symbol=name,comment=comment,Type=Type)
	# # print(verif,Type)
	# # if verif['Total'] == 0: 
	# # 	# print("Sell Time ")
	# # 	# message(symbol=name,ut='M1',Type="Sell",price=price)

	# # 	data = {
	# # 			"Name" : name,
	# # 			"TimeFrame": timeframe,
	# # 			"Type" : Type,
	# # 			'Comment': comment,
	# # 			"Lot" : lot,
	# # 		}
	# # 	signal = open_trade_buy(action=Type, symbol=name, lot=lot,  deviation=20, comment=comment)
	# # 	print(signal)
	# # 	if signal == True:
	# # 		print(signal)
	# # 		print(data)

	# # if verif['Total'] < 1 :
	# data = splite_reverse_position(name,Type,comment)
	# return data
	try:
		data = {
				"Name" : name,
				"TimeFrame": timeframe,
				"Type" : Type,
				'Comment': comment,
				"Lot" : lot,
			}
		signal = open_trade_buy(action=Type, symbol=name, lot=lot,  deviation=20, comment=comment)
		print(signal)
		if signal == True:
			print(signal)
			print(data)
		else:
			return e
	except Exception as e:
		print(e)




if __name__ == '__main__':

	uvicorn.run(app, host=host, port=port, debug=debug)