import json
import numpy as np
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup

def get_tutor_info(links, headers):
    '''Collect a group of tutor profiles specified by the given hyperlinks (links).''' 
    
    mains = []
    scheds = []

    empty = {'sunday': [None], 'monday': [None], 'tuesday': [None], 'wednesday': [None],
         'thursday': [None], 'friday': [None], 'saturday': [None]}
    
    # Open each tutor page in turn and collect their info 
    
    for i, link in enumerate(links):
        r = requests.get(link, headers = headers).text
        soup = BeautifulSoup(r, 'html.parser')

        tags = soup.find_all('script')
        try:
            time_tutoring = soup.find_all('h3')[0].text
        except:
            time_tutoring = []
        bio_list = soup.find_all('p', {'class':  'spc-zero-n spc-sm-s'})
        bio = [part.text for part in bio_list]
        
        if soup.find_all('i' ,{'class':'wc-background-pass wc-green'}):
            bck = 1
            bck_passed = soup.find_all('p', {'class':"spc-zero"})[1].text
        else:
            bck = 0
            bck_passed = []
            
        edu = soup.find_all('section' ,{'class':"spc-med-s"})
        if edu:
            educ =[e.text for e in edu]
        else:
            educ = []
        
        # Main details are contained with a json file embedded in the html
        
        try:
            main_details = json.loads(tags[0].string)
            main_details['time_tutoring'] = time_tutoring
            main_details['bio'] = bio
            main_details['background_check'] = bck
            main_details['date_background_passed'] = bck_passed
            main_details['education'] = educ
            mains.append(main_details)
            
            # Schedule details are contained within separate json file
            
            try:
                scheds.append(json.loads(tags[6].string.split('=')[1][:-1]))
            except:
                scheds.append(empty)
        except:
            pass
                
        time.sleep(np.random.rand()*5)
        
    return pd.merge(pd.DataFrame(mains), pd.DataFrame(scheds), left_index=True, right_index=True)
    
def get_single_tutor(link, headers):
    '''Collect a single tutor profile specified by the given hyperlinks (links).''' 

    empty = {'sunday': [None], 'monday': [None], 'tuesday': [None], 'wednesday': [None],
         'thursday': [None], 'friday': [None], 'saturday': [None]} 
    
    r = requests.get(link, headers = headers).text
    soup = BeautifulSoup(r, 'html.parser')

    tags = soup.find_all('script')
    try:
        time_tutoring = soup.find_all('h3')[0].text
    except:
        time_tutoring = []
        
    bio_list = soup.find_all('p', {'class':  'spc-zero-n spc-sm-s'})
    bio = [part.text for part in bio_list]
        
    if soup.find_all('i' ,{'class':'wc-background-pass wc-green'}):
        bck = 1
        bck_passed = soup.find_all('p', {'class':"spc-zero"})[1].text
    else:
        bck = 0
        bck_passed = []
            
    edu = soup.find_all('section' ,{'class':"spc-med-s"})
    
    if edu:
        educ =[e.text for e in edu]
    else:
        educ = []
        
    # Main details are contained with a json file embedded in the html
        
    try:
        main_details = json.loads(tags[0].string)
        main_details['time_tutoring'] = time_tutoring
        main_details['bio'] = bio
        main_details['background_check'] = bck
        main_details['date_background_passed'] = bck_passed
        main_details['education'] = educ
            
            # Schedule details are contained within separate json file
            
        try:
            sched = json.loads(tags[6].string.split('=')[1][:-1])
        except:
            sched = empty
    except:
        pass
        
        #both = {**main_details, **sched}
        
    return {**main_details, **sched}


def get_ids(url):
    '''Extract tutor id from their url'''
    
    if url.split('/')[-2]:
        tut_id = url.split('/')[-2]
        return int(tut_id)
    else:
        return None
        
def has_photo(url):
    '''Check if tutor has a real photo or just the stock silhouette'''
    
    yes = 'silhouette' not in str(url)
    return int(yes)
    
def remove_hours(hours):
    '''Tutors sometimes don't add their schedule, meaning the next tag (Bio) gets added intead. This function removes the word Bio.'''
    
    if hours == 'Bio':
        return 0
    else:
        return float(hours.split(' ')[0].replace(',',''))

def get_rating_count(agg):
    '''Extract rating count from aggregate rating'''
     
    return int(json.loads(agg.replace("'",'"'))['ratingCount'])

def get_rating_count_single(agg):
    '''Extract rating count from aggregate rating'''
     
    return int(raw_info['aggregateRating']['ratingCount'])

def get_rating_value(agg):
    '''Extract rating value from aggregate rating'''

    val = json.loads(agg.replace("'",'"'))['ratingValue']
    if val:
        return float(val)
    else:
        return 0
    
def get_rating_value_single(agg):
    '''Extract rating value from aggregate rating'''

    val = agg['ratingValue']
    if val:
        return float(val)
    else:
        return 0
    
def get_review_count(agg):
    '''Extract review count from aggregate rating'''
    
    val = json.loads(agg.replace("'",'"'))['reviewCount']
    if val:
        return float(val)
    else:
        return 0
    
def get_review_count_single(agg):
    '''Extract review count from aggregate rating'''
    
    val = agg['ratingValue']
    if val:
        return float(val)
    else:
        return 0

def get_bio_length(bio):
    '''Count words in bio'''

    return len(bio.split(' '))
    
def get_state(add):
    '''Extract state from address'''

    return json.loads(add.replace("'",'"'))['addressRegion']
    
def get_zip(add):
    '''Extract zip code from address'''

    return int(json.loads(add.replace("'",'"'))['postalCode'])

def get_subject_list(sub_list):
    '''Extract list of subjects offered'''
    
    sub_dicts = json.loads(sub_list.replace("'",'"'))
    return [sub['name'] for sub in sub_dicts]

def get_subject_list_single(sub_list):
    '''Extract list of subjects offered'''
    
    subs = [sub['name'] for sub in sub_list]
    return subs

def get_num_subjects(sub_list):
    '''Count number of subjects offered'''

    return len(json.loads(sub_list.replace("'",'"'))) 
    
def get_back_date(date):
    '''Extract date that background check was passed'''
    
    return date.strip('\n').split('\n')[0].split(' ')[-1]
    
def get_edu_length(edu):
    '''Count number of lines in education section'''

    return len(edu.split('\n'))
    
def extract_edu(edu, pos):
    '''Extract all institutions attended by the tutor'''
    
    edu_list = edu.split('\n')
    if pos >= len(edu_list):
        return []
    else:
        inst = edu_list[pos].strip(' ')
        stopwords = ['university','University','of','in','College','college']
        for word in stopwords:
            inst = inst.replace(word,'').strip(' ')
        return inst

def clean_income(income):
    '''remove dollar sign from income'''
    return float(income.strip('$').replace(',',''))

def check_if_bad(tutor):
    '''Check if the webpage has bad entries'''
    
    try: 
        int(json.loads(tutor['aggregateRating'].replace("'",'"'))['ratingCount'])
        return False
    except:
        return True

def get_hours_day(day):
    hours = np.array(day)
    return float(len(hours[hours])/24)