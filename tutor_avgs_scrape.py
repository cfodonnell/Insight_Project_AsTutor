#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:25:54 2020

@author: codonnell
"""


import time
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd

def ca_style(soup, state):
    
    tags_zips = soup.find_all('td', {'class': 'column-1'})
    tags_rates = soup.find_all('td', {'class': 'column-2'})
    zips = []
    rates = []
    tags_zips = [tag for tag in tags_zips if len(tag.text.split(','))==3]
    for i, tag in enumerate(tags_zips):
        if len(tag.text.split(',')) == 3:
            zips.append(tag.text.split(',')[2])
            rates.append(tags_rates[i].text)
     
    return pd.DataFrame({'state': np.array([state]*len(zips)),'zip_code': zips, 'av_rate': rates})

def tx_style(soup, state):
    
    tags_zips = soup.find_all('td', {'class': 'column-1'})
    tags_numtuts = soup.find_all('td', {'class': 'column-2'})
    tags_rates = soup.find_all('td', {'class': 'column-3'})
    
    if tags_rates:
        zips = np.array([tag.text for tag in tags_zips[-len(tags_rates):]])
        numtuts = np.array([tag.text for tag in tags_numtuts[-len(tags_rates):]])
        rates = np.array([tag.text for tag in tags_rates])

        length_checker = np.vectorize(len) 
        #remove entries that aren't a 5 digit zip code
        zips_only = zips[length_checker(zips)==5]
        numtuts_only = numtuts[length_checker(zips)==5]
        return pd.DataFrame({'state': np.array([state]*len(zips_only)), 'zip_code': zips_only, 'num_tutors': numtuts_only, 'av_rate': rates})
    else:
        pass

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}
link_data = pd.read_csv('/home/codonnell/details.csv')
links = link_data['link'].values
formats = link_data['format'].values
states = link_data['state'].values

ca_styles = []
tx_styles =[]

for i in range(0,len(link_data)):
    
    r = requests.get(links[i], headers = headers).text
    soup = BeautifulSoup(r, 'html')
    state = states[i]
    
    if formats[i] == 'c':
        ca_styles.append(ca_style(soup, state))
    elif formats[i] == 't':
        tx_styles.append(tx_style(soup, state))
    else:
        pass
    time.sleep(np.random.rand()*5)

ca_data = pd.concat(ca_styles)
tx_data = pd.concat(tx_styles)
ca_data.to_csv('/home/codonnell/ca_data.csv')
tx_data.to_csv('/home/codonnell/tx_data.csv')