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

list_name = ["GOLD",'EURUSD','USDJPY','[DAX40]','[DJI30]']



def worker(name,timeframe):
	# global num_bars
	# global url
	triger_signal = 0
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
		process = worker(name,'M15')

		data = pd.Series(process).to_string()
		print(data)

		message_analyse(data,intra_webhook)


schedule.every(15).minutes.do(worker_intra)
schedule.every().day.do(worker_Daily)
schedule.every().weeks.do(worker_weekly)

while True:
	try:
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)