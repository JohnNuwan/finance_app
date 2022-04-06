
import os 
import sys
os.system('cls')

import time 
import pandas as pd
import MetaTrader5 as mt5
from rich import print
from termcolor import colored, cprint

from config.config import *


import schedule

import requests
import json

url = f"http://{host}:{port}"
DISCORD_URL:"https://discord.com/api/webhooks/961166524238950400/1ZaocpBePBc7ZOSmvxRGJrEaqeWv7QZbz6sVBZwq2pm56vEvfDsIVhe2YvrrFoq692nW"

ultra_scalp = ["renfort_engulfin","ichimoku",'Support_Ress']
scalp = []
intraday = []
swing = []

secur_pos = "HOLD"
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
	print("initialize() failed, error code =",mt5.last_error())
	quit()
 
# check the presence of open positions
positions_total=mt5.positions_total()
if positions_total>0:
	print("Total positions=",positions_total)
else:
	print("Positions not found")

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

def renfort():

	comment = "renfort_engulfin"
	lot = 0.02
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
		# display these positions as a table using pandas.DataFrame
		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
		df['time'] = pd.to_datetime(df['time'], unit='s')
		df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
		df = df.set_index("time")
		df["pct_chang"] =  df.apply(lambda row: calc_dif(row),axis=1)
		df["Pips"] =  df.apply(lambda row: pips(row),axis=1)
		print(df)
		for row in df.itertuples():
			name = row.symbol
			timeframe = "M1"
			if (row.comment == secur_pos) and row.pct_chang > 0.05:
				data = get_data(row.symbol,timeframe)
				# print(data.tail(1))
				# condition_buy = (data['signal'][-1] == 1) and (row.type == 0)
				# condition_sell = (data['signal'][-1] == -1) and (row.type == 1)
				# print(f"buyt : {condition_buy}   sell : {condition_sell}")
				if data['signal'][-1] != 0:
					# print(row.symbol,row.comment,row.profit, row.type)
					condition_buy = (data['signal'][-1] == 1) and (row.type == 0)
					condition_sell = (data['signal'][-1] == -1) and (row.type == 1)
					print(f"buyt : {condition_buy}   sell : {condition_sell}")
					if condition_buy:
						route_position = f"{url}/open_position/{name}/{timeframe}/buy/{comment}/{lot}"
						print(route_position)
						r2 = requests.get(route_position)
						print(r2)

					if condition_sell:
						route_position = f"{url}/open_position/{name}/{timeframe}/sell/{comment}/{lot}"
						print(route_position)
						r2 = requests.get(route_position)
						print(r2)



def Management_position():

	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
		# display these positions as a table using pandas.DataFrame
		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
		df['time'] = pd.to_datetime(df['time'], unit='s')
		df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
		df = df.set_index("time")
		df["pct_chang"] =  df.apply(lambda row: calc_dif(row),axis=1)
		df["Pips"] =  df.apply(lambda row: pips(row),axis=1)
		for row in df.itertuples():
			for k in ultra_scalp :
				if row.comment == k:
					print(row.comment,k,row.profit,round(row.pct_chang,4),row.Pips)
					pct_split = 0.02
					pct_lose = -0.04





def get_data(name,timeframe,num_bars=200):
	route_data = f"{url}/sup_res/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(route_data)
	print(r2)
	print(route_data)
	data = json.loads(r2.text)
	df = pd.read_json(data)
	return df

def worker():
	Management_position()


schedule.every(1).minutes.do(worker)
# # schedule.every(5).minutes.do( worker_scalp_m5)
# schedule.every(15).minutes.do(worker_intra_m15)
# schedule.every(30).minutes.do(worker_intra)
# schedule.every().day.do(worker_Daily)
# # schedule.every().weeks.do(worker_weekly)

while True:
	try:
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)