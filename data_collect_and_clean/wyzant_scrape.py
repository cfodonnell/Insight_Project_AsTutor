import time
from selenium import webdriver
import numpy as np
import pandas as pd
import proc_funcs as pf
import sql_funcs as sf

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}

# Launch a chrome session using selenium
search_add = 'https://www.wyzant.com/match/search?sort=1&d=20&utc_offset=-5&min_price=10&max_price=200&min_age=18&max_age=100&gender_pref=none&st=5&kw=physics&ol=false&z=78750'
chromedriver = '/home/codonnell/chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get(search_add)

# Manually bypass the website questionnaire
input("Press Enter to continue when the webpage questionnaire has been skipped/completed")

# enter desired zip codes and subjects to search for

zips = [78750,78707,78753]
subjects = ['physics', 'math', 'spanish', 'english', 'computer']
links = []
tot_tuts = []

# collect hyperlinks from tutor search page for each zip code and subject

for zip_code in zips:
    links = []
    tot_tuts = []
    
    for subject in subjects:
            
        url = 'https://www.wyzant.com/match/search?sort=1&d=20&utc_offset=-5&min_price=10&max_price=200&min_age=18&max_age=100&gender_pref=none&st=0&kw=' + subject + '&ol=false&z=' + str(zip_code)
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
                    urlmore = 'https://www.wyzant.com/match/search/more?d=20&gender_pref=none&kw=' + subject + '&max_age=100&max_price=500&min_age=18&min_price=10&ol=false&page_number=' + str(i) + '&sort=1&st=0&utc_offset=-5&z=' +str(zip_code)
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
            
        # Wait a bit between requests
        time.sleep(np.random.rand()*5)
    
    # Filter out tutors who have appeared more than once
    unique_tuts = np.unique(np.array([item for sublist in links for item in sublist]))

# Open SQL connection
con = sf.open_sql_con()
engine = sf.create_sql_engine()

for link in unique_tuts:
    
    # for each tutor link, get the raw data and process it, before adding to two
    # database tables: one for the tutor main deatils (tutor_main), and one 
    # containing the list of subjects taught by each tutor (tutor_subjects)
    
    tutor_info = pf.get_single_tutor(link, headers)
    tutor_info['tut_id'] = pf.get_ids(tutor_info['url'])
    tutor_info['photo'] = pf.has_photo(tutor_info['image'])
    tutor_info['rating_count'] = tutor_info['aggregateRating']['ratingCount']
    tutor_info['rating_av'] = pf.get_rating_value_single(tutor_info['aggregateRating'])
    tutor_info['review_count'] = pf.get_review_count_single(tutor_info['aggregateRating'])
    tutor_info['bio_length'] = pf.get_bio_length(tutor_info['bio'][0])
    tutor_info['subject_list'] = pf.get_subject_list_single(tutor_info['makesOffer'])
    tutor_info['num_subjects'] = len(tutor_info['makesOffer'])
    tutor_info['hours_tutoring'] = pf.remove_hours(tutor_info['time_tutoring'])
    tutor_info['state'] = tutor_info['address']['addressRegion']
    tutor_info['zip_code'] = tutor_info['address']['postalCode']
    tutor_info['edu_length'] = pf.get_edu_length(tutor_info['education'][0])
    tutor_info['inst_1']=pf.extract_edu(tutor_info['education'][0],1)
    tutor_info['inst_2']=pf.extract_edu(tutor_info['education'][0],4)
    tutor_info['inst_3']=pf.extract_edu(tutor_info['education'][0],7)
    tutor_info['qual_1']=pf.extract_edu(tutor_info['education'][0],2)
    tutor_info['qual_2']=pf.extract_edu(tutor_info['education'][0],5)
    tutor_info['qual_3']=pf.extract_edu(tutor_info['education'][0],8)
    tutor_info['hourly_rate'] = float(tutor_info['priceRange'])

    day_cols = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
    tot_hours = 0
    
    id_list = [str(tutor_info['tut_id']) ] * tutor_info['num_subjects']
    subs = [item.replace(' tutoring','') for item in tutor_info['subject_list']]
    tutor_subjects = pd.DataFrame({'tutor_ids':np.array(id_list), 'subjects': np.array(subs)})
    tutor_subjects.to_sql('tutor_subjects', engine, if_exists='append')
    
    for col in day_cols:
        tutor_info[col + '_hours'] = pf.get_hours_day(tutor_info[col])
        tot_hours += pf.get_hours_day(tutor_info[col])
        
    tutor_info['mean_hours'] = tot_hours/7
    tutor_info = pd.Series(tutor_info).to_frame().T
    
    tutor_info = tutor_info[['description','hourly_rate','bio','background_check','tut_id','photo','rating_count','rating_av','review_count','bio_length', 'num_subjects', 'hours_tutoring', 'state', 'zip_code',
           'edu_length', 'inst_1', 'inst_2', 'inst_3', 'qual_1', 'qual_2', 'qual_3', 'sunday_hours', 'monday_hours', 'tuesday_hours',
           'wednesday_hours', 'thursday_hours', 'friday_hours', 'saturday_hours','mean_hours']]
    
    tutor_info.to_sql('tutor_main', engine, if_exists='append')