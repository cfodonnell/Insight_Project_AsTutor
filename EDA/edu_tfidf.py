#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:50:57 2020

@author: codonnell
"""


import time
import numpy as np
import pandas as pd
import json
import seaborn as sb
from matplotlib import pyplot as plt
from matplotlib import rcParams
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import seaborn as sb
import pickle
import re

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import category_encoders as ce
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
from xgboost import plot_importance
from sklearn.metrics import r2_score
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as esw
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn import feature_selection

def qual_encode(qual):
    
    qual_list = ['Masters','MBA','PhD','J.D.']
    qual_encodings = {'Masters': 5, 'MBA': 5, 'PhD': 20, 'J.D.': 30}
    if qual in qual_list:
        return qual_encodings[qual]
    else:
        return 0
    
def get_exp(bio):
    
    if 'years' in bio:
        yrs = np.array([int(i) for i in re.findall('\d+', bio)])
        if len(yrs[yrs<50])>0:
            return max(yrs[yrs<50])
        else:
            return 0
    else:
        return 0
    
dbname = 'tutor_db'
username = 'codonnell'
pswd = '7883511'

con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)

# query:
sql_query = """
SELECT * FROM tutor_main
"""
tutor_data = pd.read_sql_query(sql_query,con)
tutor_data = tutor_data.drop_duplicates(subset='tut_id')
tutor_data['log_hourly_rate'] = np.log(tutor_data['hourly_rate'])
tutor_data['qual_encoded'] = tutor_data.apply(lambda x: qual_encode(x['qual_1']) + qual_encode(x['qual_2']), axis =1) 

ivys = 'Brown|Columbia|Dartmouth|Harvard|Cornell|Pennsylvania|Princeton|Yale'
tutor_data['all_ed'] = tutor_data['inst_1'] + ' ' + tutor_data['inst_2'] + ' ' + tutor_data['inst_3']
tutor_data['ivy_1e'] = tutor_data['inst_1'].str.contains(ivys).astype(int)
tutor_data['ivy_2e'] = tutor_data['inst_2'].str.contains(ivys).astype(int)
tutor_data['ivy_3e'] = tutor_data['inst_3'].str.contains(ivys).astype(int)
tutor_data['ivy_tot'] = tutor_data['ivy_1e']+tutor_data['ivy_2e']+tutor_data['ivy_3e']

tutor_data['state_1e'] = tutor_data['inst_1'].str.contains('State').astype(int)
tutor_data['state_2e'] = tutor_data['inst_2'].str.contains('State').astype(int)
tutor_data['state_3e'] = tutor_data['inst_3'].str.contains('State').astype(int)
tutor_data['state_tot'] = tutor_data['state_1e']+tutor_data['state_2e']+tutor_data['state_3e']
tutor_data['experience'] = tutor_data['bio'].apply(get_exp)

stopWords = esw 

tfidf_ed = TfidfVectorizer(
    min_df = 0,
    max_df = 0.95,
    max_features = 20000,
    stop_words = stopWords,
    ngram_range = (1,2)
)
tfidf_ed.fit(tutor_data['all_ed'])
text_ed = tfidf_ed.transform(tutor_data['all_ed'])