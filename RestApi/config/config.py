#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : K.Azazel
# Created Date: 27/03/2022
# =============================================================================
"""
	Docstring :
		Fichier De Configuration pour le Serveur Coter RestApi
"""
# =============================================================================
# Imports
# =============================================================================

import os,sys
from art import *
from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich.table import Table
from rich import box


__author__ = "K.Azazel"
__copyright__ = "Copyright 2022"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "K.Azazel"
__status__ = "Beta"



"""

	Configuration des paramettre serveur 
	Configuration Du script init 
"""

# Partie Definition Console Promt
custom_theme = Theme({
	"info": "dim cyan",
	"action": "dim yellow",
	"separate": "dim red",
	"warning": "magenta",
	"danger": "bold red"
})
cs = Console(theme=custom_theme)

#__________________________________________________
# Definition Serveur
host = "localhost"
port = 8095
debug = True
url = f"http://{host}:{port}"

#__________________________________________________
# Definition Programme Name
prog_name = "RestAPI For Finance"

description = f" Welcome To Api For Finance Application . Find more information at http://{host}:{port}/docs"

def sep():
	cs.print("-"*30,justify='center',style="separate")


def sep_action(name):
	data = f"| {name} |"
	cs.print("-"*15,data,"-"*15,justify='center',style='info')
	cs.print("-"*len(data) ,justify='center',style="separate")

def sep_log(message):
	cs.print("-"*30,justify='center',style="separate")
	cs.log(message,justify='center',style='info')
	cs.print("-"*30,justify='center',style="separate")

def display(df,name):
	cs.print("-"*15,name,"-"*15,justify='center',style='info')
	print(df,"\n")

def banner():
	logo = tprint(prog_name,font="wizard", chr_ignore=True)
	sep()


	table = Table(title="Credits", box=box.MINIMAL_DOUBLE_HEAD)
	table.add_column("Author", justify="right", style="cyan", no_wrap=True)
	table.add_column("Version", justify="right", style="green")
	table.add_column("Status", style="magenta")

	table.add_row(__author__, __version__, __status__)
	cs.print(table,justify='center')
	cs.print("Python Version: 3.8.0",justify="right",style='info')
	sep()