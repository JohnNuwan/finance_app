#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : K.Azazel
# Created Date: 27/03/2022
# =============================================================================
"""
	Docstring :
		
	

"""
# =============================================================================
# Imports
# =============================================================================



import os
import sys

from rich import print
from config.config import *
import art

from cryptography.fernet import Fernet

import pandas as pd

os.system('cls')
path = "./config/"

banner()

# Creation User dict
user_info = {}


def display_path(path):
	"""  Affiche Simplement Les Noms Fichiers  """
	try:
		for i in os.listdir(path):
			cs.print(f"{path} : {i}")
	except Exception as e:
		raise e


def init_user():
	try:
		sep_log("Creation User")
		
		# User info
		name = "K.Azazel"#input("enter Name : ")
		passwd = "Pass"#input("Enter Passwd : ")
		return name, passwd
		
	except Exception as e:
		cs.print(e,style='warning')


def init_master_key():
	try:
		sep_action("MASTER_KEY")
		# Generate Master Key
		MASTER_KEY  = Fernet.generate_key()
		f = Fernet(MASTER_KEY)
		cs.print("Input Your Master_Pass_Token",style='bold yellow')
		master_key_input = input("MASTER_KEY: ").encode()
		token = f.encrypt(master_key_input)
		d = f.decrypt(token)

		print("Token Key : ",token,"\n")
		print("Decode Token Key : ",d.decode(),"\n")

		with open(f'{path}MASTER_KEY.key', 'w') as file:
		        file.write(str(MASTER_KEY))

		return f
		
	except Exception as e:
		cs.print(e,style='warning')


def init_user_key():
		try:
			sep_action("Create User Key")
			KEY = Fernet.generate_key()
			return KEY
			
		except Exception as e:
			cs.print(e,style='warning')

def implement_user(user_info,MASTER_KEY):
	try:
		sep_action("Implement User")
		name,passwd = init_user()
		Key = init_user_key()
		user_info["Name"] = name
		user_info["Passwd"] = passwd
		user_info["Key"] = Key
		user_info["Encryt_Key"] = MASTER_KEY.encrypt(Key)
		 

		data = pd.Series(user_info)

		display(data,"User info")


		data.to_json(f"{path}user_info.json")
		
	except Exception as e:
		cs.print(e,style='warning')


def main():

	sep_log("Verification Path Init")

	sep_action("Path at Init")
	cs.print("Diplay Filname Befor Traitement",style='green')
	display_path(path)
	MASTER_KEY = init_master_key()
	
	implement_user(user_info,MASTER_KEY)

	sep_action("Path at Final")
	display_path(path)
	sep()
	message = "Congratulation La Master Keys A été Créé ! \n  | Attention N'oubliez pas de Copier la MASTER_KEY Dans le Dossier Client Pour la connection |"
	cs.print(message,justify="center",style="bold yellow")

if __name__ == '__main__':
	main()

