import json
import numpy

def get_ids(url):
    if url.split('/')[-2]:
        tut_id = url.split('/')[-2]
        return int(tut_id)
    else:
        return None
        
def has_photo(url):
    yes = 'silhouette' not in str(url)
    return int(yes)
    
def remove_hours(hours):
    if hours == 'Bio':
        return 0
    else:
        return float(hours.split(' ')[0].replace(',',''))

def get_rating_count(agg):
    return int(json.loads(agg.replace("'",'"'))['ratingCount'])

def get_rating_value(agg):
    val = json.loads(agg.replace("'",'"'))['ratingValue']
    if val:
        return float(val)
    else:
        return 0
    
def get_review_count(agg):
    val = json.loads(agg.replace("'",'"'))['reviewCount']
    if val:
        return float(val)
    else:
        return 0

def get_bio_length(bio):
    return len(bio.split(' '))
    
def get_state(add):
    return json.loads(add.replace("'",'"'))['addressRegion']
def get_zip(add):
    return int(json.loads(add.replace("'",'"'))['postalCode'])

def get_subject_list(sub_list):
    sub_dicts = json.loads(sub_list.replace("'",'"'))
    return [sub['name'] for sub in sub_dicts]

def get_num_subjects(sub_list):
    return len(json.loads(sub_list.replace("'",'"')))

def get_hours_day(day):
    hours = numpy.array(day.replace('[','').replace(']','').replace(' ','').split(','))
    return float(len(hours[hours=='True'])/24)   
    
def get_back_date(date):
    return date.strip('\n').split('\n')[0].split(' ')[-1]
    
def get_edu_length(edu):
    return len(edu.split('\\n'))
    
def extract_edu(edu, pos):
    edu_list = edu.split('\\n')
    if pos >= len(edu_list):
        return []
    else:
        inst = edu_list[pos].strip(' ')
        stopwords = ['university','University','of','in','College','college']
        for word in stopwords:
            inst = inst.replace(word,'').strip(' ')
        return inst

def clean_income(income):
    return float(income.strip('$').replace(',',''))

