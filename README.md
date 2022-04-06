# Finance APP | Serveur | Worker | Clients | RestApi | Analyse

---

<!-- <img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.dI06HzHOuhwXKnLLMhHVTwHaHa%26pid%3DApi&f=1" alt="drawing" width="125"/> -->


---
**Language**  : *Python 3.8.0*

**PlatForme** : *MetaTrader5*

**Broker** : 

- [*FTMO*](https://trader.ftmo.com)
- [*Admiral Market*](https://admiralmarkets.com/start-trading/admiral-invest-stocks-and-etfs?raf=53471867)
- [*VantageFX*](https://www.vantagemarkets.com/forex-trading/forex-trading-account/?affid=58014)

---


### <span style="color:red">**| /!\ Pour Le Moment Le Script Ne gere Pas  /!\ |**</span>

dans le Script RestApi/Serveur_RestAPI_Finance.py, La route 

<code>/open_position/{name}/{timeframe}/{Type}/{comment}/{lot} </code>

fait appel a la fonction  <span style="color:cyan">**chek_take_position(symbol,comment,Type)**</span> dans le script Functions/trading_function_and_strat.py 

Ce code Fonctionne dans un fichier Seul . Mais dès qu'il est mis dans L'api celui-ci ne fonctionne plus.
Mes Connaisance dans le developpement et dans la programmations informatique ne sont pas assez avancer.


<code> 

	def chek_take_position(symbol,comment,Type):
		url = f"http://{host}:{port}"
		print(url)
		route_position = "/positions_en_court"
		url = f"{url}{route_position}"
		cs.log(url)
		print(url)
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

</code>

---
### Creation Venv

Creation D'un environement Virtuel 

	python3 -m venv venv 

Activation venv

windows

	venv\Scripts\activate

Linux | Mac

	source my_venv/bin/activat

---

#### Mise A jours du Paquet Pip


Juste parce L'information de mise a jours me saoul dans le terminal 

	python -m pip install --upgrade pip

---

# Installation Lib

	pip install -r requirements.txt

---

### Lib Utiliser:

Pandas

> pour L'analyse des donner en DataFrame

numpy

> Pour Les Calculs 

Ta

> Indicateur Technique

requests

> Requete des Strategies Au serveur

art

> Pour Affichage Dynamique

seaborn

> Pour visualisation de certaine Donnée

uvicorn

> Pour Facilité les traitement avec Fastapi

rich

> Pour retour promp 


schedule
> Pour Planifier des Actions Dans le Temps


FastAPi
> Pour La Creation De L'api


---

# Serveur API

creation d'un simple serveur pour echange données en temp reel 

donner boursiere , plus retour strategie 
prise de position automatique 
management des position 
recommandation de position 
correlation des different actife

## Création d'une api 

recuperé en temp-reel les donné sous deux forme OHCL 

### Server Route:

- Get /OHLC/{name}/{timeframe}/{num_bars}

| Open | High | Low | Close | Volume | Spread |
| ---- | ---- |---- | ----  |---- | ---- | 
| 1.232 | 1.260 | 1.110 | 1.250 | 150 | 9 |

- Get /stochc/{name}/{timeframe}/{num_bars}

	- ajout valeur Stochastique et Signal %K %D Strategy Stochastique

- Get /sup_res/{name}/{timeframe}/{num_bars}

	* Calcule Support Resistance de L'asset , avec Strategy Stochastique et RSI en plus au retourn d'inforamtion

- Get /ichimoku/{name}/{timeframe}/{num_bars}

	* Calcule De l'indicateur Ichimoku, Avec Retour Strategy

- Get /position_total

	* retourne Le Nombres Globales de Positons en court

- Get/positions_en_court

	* Retourne Les Positions en cours sous format Json 


Definition port : *localhost*
Definition host : **8090**


---


# First Init

Vous Trouver un fichier *RestApi/First_init_constructor_info.py*  lancer le avec la commande:

		python RestAPI/First_init_constructor_info.py

suivre les instructions

---
# Analyse

ReadMe dans le Folder