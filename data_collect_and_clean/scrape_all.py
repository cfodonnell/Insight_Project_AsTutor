import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import numpy as np
import pandas as pd
import json
import scrape_funcs as sf

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}

already_done = [77449,11368,60629,90011,79936,30044,80209,89138,28208,84102,98122,33128,
               46201, 55401,43215,19102,94108,22046,91911,37128,85001,78214,48201,63108,
               80303, 926, 8701]
pop_zips = pd.read_csv('/home/codonnell/Insight/Insight_Project_AsTutor/data/raw/zips_incomes/zips_ga_co_wa.csv')

np.setdiff1d(pop_zips['zip_code'].values,already_done)

zips = np.setdiff1d(pop_zips['zip_code'].values,already_done)
#zips = already_done
subjects = ['physics', 'math', 'spanish', 'english', 'computer']
links = []
tot_tuts_dfs = []

for zip_code in zips:
    tot_tuts = []
    
    for subject in subjects:
            
        url = 'https://www.wyzant.com/match/search?sort=1&d=20&utc_offset=-5&min_price=10&max_price=200&min_age=18&max_age=100&gender_pref=none&st=5&kw=' + subject + '&ol=false&z=' + str(zip_code)
        driver.get(url)
        
        try:
            num_tuts = driver.find_elements_by_tag_name('strong')[2].text #per subject given zip
        except:
            num_tuts = 0
        
        lks = driver.find_elements_by_xpath('.//a[@class="tutor-card flex"]')
        lks_found = [link.get_attribute('href') for link in lks]
        links.append(lks_found)
        
        try:
            if int(num_tuts.split(' ')[0]) > 10:
                extras = int(np.floor(int(num_tuts.split(' ')[0])/10)) + 1
                for i in range(1,extras):
                    urlmore = 'https://www.wyzant.com/match/search/more?d=20&gender_pref=none&kw=' + subject + '&max_age=100&max_price=500&min_age=18&min_price=10&ol=false&page_number=' + str(i) + '&sort=1&st=5&utc_offset=-5&z=' +str(zip_code)
                    driver.get(urlmore)
                    more_lks = driver.find_elements_by_xpath('.//a[@class="tutor-card flex"]')
                    more_lks_found = [link.get_attribute('href') for link in more_lks]
                    links.append(more_lks_found)
                    time.sleep(np.random.rand()*5)
            else:
                pass
        except:
            pass
            
            
        tot_tuts.append(num_tuts) #per subject given zip
        time.sleep(np.random.rand()*5)
        
    tot_tuts_dfs.append(pd.DataFrame({'zip_code': [str(zip_code)]*5, 'tot_tuts': tot_tuts}))
    time.sleep(np.random.rand()*5)      
            
    
unique_tuts = np.unique(np.array([item for sublist in links for item in sublist]))
sf.save_tut_id(unique_tuts)
sf.get_tutor_info(state, unique_tuts, headers)
tut_num_df = pd.concat(tot_tuts_dfs)
tut_num_df.to_csv('/home/codonnell/tutors//tutnew/tut_num_' + state + '.csv')
