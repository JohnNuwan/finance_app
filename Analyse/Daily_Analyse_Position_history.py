

import os  
import pandas as pd 
from datetime import datetime 
import MetaTrader5 as mt5

from rich import print
import requests

disc_daily = "https://discord.com/api/webhooks/960949053674389536/usUsJxcYxOMBDp9a8UGjgD73ceZzJ_qqgF4B6ipjbzHp-2mmd_39KE0BnyQ_CLK1iHo0"

os.system('cls')
# établit une connexion avec le terminal MetaTrader 5
mt5.initialize()
 
# récupère le nombre d'ordres dans l'historique
from_date=datetime(2022,3,5) 
to_date=datetime.now()

# récupère les transactions des symboles dont les noms contiennent "GBP" dans un intervalle spécifié
deals=mt5.history_deals_get(from_date, to_date, group="*GBP*")
# if deals==None:
#     print("Aucune transaction pour le groupe=\"*USD*\", code d'erreur={}".format(mt5.last_error()))
# elif len(deals)> 0:
#     print("history_deals_get({}, {}, group=\"*GBP*\")={}".format(from_date,to_date,len(deals)))
 
# récupère les transactions des symboles dont les noms ne contiennent ni "EUR" ni "GBP"
deals = mt5.history_deals_get(from_date, to_date, group="*,!*EUR*,!*GBP*")
if deals == None:
    print("Aucune transaction, code d'erreur={}".format(mt5.last_error()))
elif len(deals) > 0:
    # print("history_deals_get(from_date, to_date, group=\"*,!*EUR*,!*GBP*\") =", len(deals))
 # affiche ces transactions sous forme de tableau à l'aide de pandas.DataFrame
    df=pd.DataFrame(list(deals),columns=deals[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # print(df)


mask_symbol = df.drop(columns=['ticket','time_msc','price','order','magic','position_id','reason'],axis=1)
mask_symbol['x1'] = mask_symbol['type'].map({1: 'sell', 0: 'buy'})
mask_symbol = mask_symbol.groupby(["symbol",'type']).sum()


mask_comment = df.drop(columns=['ticket','time_msc','price','order','magic','position_id','reason'],axis=1)
mask_comment = mask_comment.groupby(["symbol"]).agg('sum')

total_volume = df['volume'].sum()
total_profit = df['profit'].sum()

texte = f"Rapport Pour la periode du {from_date} au {to_date} \nLes position du jour \n{mask_symbol.to_string()}\n\n{'-'*10}\n \
		Rapport Part Symbole : \n{mask_symbol.to_string()}\n\n\tTotal Volume : {round(total_volume,2)} Lot\n\n\tTotal profit : {round(total_profit,2)} $"

print(texte)

Name = "Rapport Management "

Avatar = "https://i.imgur.com/F1UMx9K.jpeg"

chat_message = {
					"username": Name,
					"avatar_url": Avatar,
					"content": f"------------------\n{texte}"
				}

requests.post(disc_daily, json=chat_message)