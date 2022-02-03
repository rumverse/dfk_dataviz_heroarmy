#!/usr/bin/env python3

import os
import subprocess
import requests
import csv
import logging
from time import sleep
from math import ceil
import random
logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


dfk_hero_api = "https://us-central1-defi-kingdoms-api.cloudfunctions.net/query_heroes"
datafile = "dfk_heroes.csv"
sample_data = {
  "id": "1",
  "numberid": "1",
  "owner": "0x2E7669F61eA77F02445A015FBdcFe2DE47083E02",
  "creator": None,
  "statgenes": "55595053337262517174437940546058771473513094722680050621928661284030532",
  "visualgenes": "170877259497388213840353281232231169976585066888929467746175634464967719",
  "rarity": 4,
  "shiny": True,
  "generation": 0,
  "firstname": 184,
  "lastname": 85,
  "shinystyle": 4,
  "mainclass": "2",
  "subclass": "5",
  "summonedtime": "1633044270",
  "nextsummontime": "1633044270",
  "summonerid": "0",
  "assistantid": "0",
  "summons": 0,
  "maxsummons": 11,
  "staminafullat": "1643802946",
  "hpfullat": "0",
  "mpfullat": "0",
  "level": 2,
  "xp": "1813",
  "currentquest": "0x0000000000000000000000000000000000000000",
  "sp": 0,
  "status": "0",
  "strength": 12,
  "intelligence": 9,
  "wisdom": 9,
  "luck": 14,
  "agility": 13,
  "vitality": 8,
  "endurance": 7,
  "dexterity": 9,
  "hp": 177,
  "mp": 51,
  "stamina": 26,
  "strengthgrowthp": 5500,
  "intelligencegrowthp": 2500,
  "wisdomgrowthp": 3500,
  "luckgrowthp": 6700,
  "agilitygrowthp": 7000,
  "vitalitygrowthp": 5000,
  "endurancegrowthp": 4500,
  "dexteritygrowthp": 5500,
  "strengthgrowths": 750,
  "intelligencegrowths": 2000,
  "wisdomgrowths": 2000,
  "luckgrowths": 1400,
  "agilitygrowths": 1000,
  "vitalitygrowths": 1250,
  "endurancegrowths": 1250,
  "dexteritygrowths": 750,
  "hpsmgrowth": 2500,
  "hprggrowth": 5000,
  "hplggrowth": 2500,
  "mpsmgrowth": 3000,
  "mprggrowth": 4000,
  "mplggrowth": 3000,
  "mining": 2,
  "gardening": 5,
  "foraging": 15,
  "fishing": 16,
  "profession": "gardening",
  "passive1": "Basic1",
  "passive2": "Basic2",
  "active1": "Basic3",
  "active2": "Basic4",
  "statboost1": "INT",
  "statboost2": "LCK",
  "statsunknown1": "0",
  "element": "fire",
  "statsunknown2": "4",
  "gender": "female",
  "headappendage": "1",
  "backappendage": "6",
  "background": "plains",
  "hairstyle": "1",
  "haircolor": "d7bc65",
  "visualunknown1": "0",
  "eyecolor": "2494a2",
  "skincolor": "e6a861",
  "appendagecolor": "a0304d",
  "backappendagecolor": "830e18",
  "visualunknown2": "7",
  "assistingauction": None,
  "assistingprice": "0",
  "saleauction": None,
  "saleprice": "0",
  "privateauctionprofile": None,
  "summoner_id": None,
  "summoner_mainclass": None,
  "summoner_rarity": None,
  "summoner_generation": None,
  "summoner_visualgenes": None,
  "assistant_id": None,
  "assistant_mainclass": None,
  "assistant_rarity": None,
  "assistant_generation": None,
  "assistant_visualgenes": None,
  "owner_name": "Magia",
  "owner_picid": 6,
  "owner_address": "0x2E7669F61eA77F02445A015FBdcFe2DE47083E02",
  "assistauction_startingprice": None,
  "assistauction_endingprice": None,
  "assistauction_duration": None,
  "assistauction_startedat": None,
  "saleauction_startingprice": None,
  "saleauction_endingprice": None,
  "saleauction_duration": None,
  "saleauction_startedat": None,
  "firstname_string": "Frida",
  "lastname_string": "Farwolf",
  "summons_remaining": 11,
  "floorprice": 0
}

# applies to both main and sub
classes = {
	"0": "Warrior",
	"1": "Knight",
	"2": "Thief",
	"3": "Archer",
	"4": "Priest",
	"5": "Wizard",
	"6": "Monk",
	"7": "Pirate",
	"16": "Paladin",
	"17": "Darkknight",
	"18": "Summoner",
	"19": "Ninja",
	"24": "Dragoon",
	"25": "Sage",
	"28": "Dreadknight",
	"None": "None"
}

limit = 200
fprices = {}

def get_floorprices():
	global fprices
	if bool(fprices) == False:
		url = "https://us-east1-dfkwatch-328521.cloudfunctions.net/heroFloor"
		fprices = requests.get(url).json()
	return fprices

def _get_summonbucket(maxsummons):

	if maxsummons is None:
		maxsummons = 0

	if maxsummons == 0:
		return "S0"
	elif maxsummons == 11:
		# infinite summons
		return "Si"
	elif maxsummons >= 1 and maxsummons <= 4:
		return "S1-4"
	elif maxsummons >= 5 and maxsummons <= 7:
		return "S5-7"
	else:
		return "S8+"

def get_floorprice(hero_data):
	# Ref https://kingdom.watch/about/floorprice
	# Generation G0, G1, G2, G3, G4+
	# Rarity 
	# Summons Left S0, S1-4, S5-7, S8+, Si (Gen0)
	# Main Class
	# Profession
	g = hero_data["generation"]
	r = hero_data["rarity"]
	s = _get_summonbucket(hero_data["maxsummons"])
	m = classes[str(hero_data["mainclass"])]
	p = hero_data["profession"]

	try:
		try:
			fp_key = "-".join(map(str,[g,r,s,m,p]))
			fp = get_floorprices()[fp_key]
			return fp
		except KeyError:
			try:
				fp_key = "-".join(map(str,[g,r,s,m]))
				fp = get_floorprices()[fp_key]
				return fp
			except KeyError:
				try:
					fp_key = "-".join(map(str,[g,r,s]))
					fp = get_floorprices()[fp_key]
					return fp
				except KeyError:
					try:
						fp_key = "-".join(map(str,[g,r]))
						fp = get_floorprices()[fp_key]
						return fp
					except KeyError:
						fp_key = "-".join(map(str,[g]))
						fp = get_floorprices()[fp_key]
						return fp
	except Exception as e:
		logging.debug(e)
		return 0



# Ref https://gist.github.com/zed/0ac760859e614cd03652
def wccount(filename):
    out = subprocess.Popen(['wc', '-l', filename],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT
                         ).communicate()[0]
    return [int(s) for s in str(out).split(" ") if s.isdigit()].pop()

def fetch():
	rowcnt = wccount(datafile)
	# if rowcnt == 0:
	# 	csv_headers = ','.join(map(str,list(sample_data.keys())))
	# 	with open(datafile, "w") as file:
	# 		file.write(csv_headers)

	offset = rowcnt-1 if rowcnt > 1 else 0

	payload = {
	    "limit": limit,
	    "params": [
	    ],
	    "offset": offset,
	    "order": {
	        "orderBy": "id",
	        "orderDir": "asc"
	    }
	}
	logging.debug("fetching {}-{}".format(offset,limit+offset),payload)
	
	dfk_heroes = requests.post(dfk_hero_api, json=payload).json()

	for dfk_hero in dfk_heroes:
		dfk_hero2 = dfk_hero
		dfk_hero2["floorprice"] = get_floorprice(dfk_hero)
		
		with open(datafile, 'a') as f:
			writer = csv.DictWriter(f, sample_data.keys())
			if rowcnt == 0:
				writer.writeheader()
			writer.writerow(dfk_hero2)
			rowcnt += 1

def get_latest_hero():
	payload = {
	    "limit": 1,
	    "params": [
	    ],
	    "offset": 0,
	    "order": {
	        "orderBy": "id",
	        "orderDir": "desc"
	    }
	}
	logging.debug(payload)
	latest_hero = requests.post(dfk_hero_api, json=payload).json().pop()
	return latest_hero


def process():
	#fetch()

	rowcnt = wccount(datafile)
	if rowcnt > 1:
		loopcnt = (int(get_latest_hero()["id"])-rowcnt)/limit
	else:
		loopcnt = int(get_latest_hero()["id"])/limit

	for i in range(0, ceil(loopcnt)):
		fetch()
		sleep(random.random())
	#print(get_floorprice(sample_data))
	#print(get_floorprices())

def run():
	process()


if __name__ == "__main__":
	run()