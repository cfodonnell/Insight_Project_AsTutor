import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time


def get_tutor_info(zip_code, links, headers):
    
    mains = []
    scheds = []

    empty = {'sunday': [None], 'monday': [None], 'tuesday': [None], 'wednesday': [None],
         'thursday': [None], 'friday': [None], 'saturday': [None]}
    
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
        
        try:
            main_details = json.loads(tags[0].string)
            main_details['time_tutoring'] = time_tutoring
            main_details['bio'] = bio
            main_details['background_check'] = bck
            main_details['date_background_passed'] = bck_passed
            main_details['education'] = educ
        
            mains.append(main_details)
            try:
                scheds.append(json.loads(tags[6].string.split('=')[1][:-1]))
            except:
                scheds.append(empty)
        except:
            pass
                
        time.sleep(np.random.rand()*5)
        
    df = pd.merge(pd.DataFrame(mains), pd.DataFrame(scheds), left_index=True, right_index=True)
    df.to_csv('/home/codonnell/tutors/tutnew/tutors_' + str(zip_code) + '.csv')
    
def save_tut_id(unique_tuts):

    with open('/home/codonnell/tutors_ids.txt', 'w') as filehandle:
        for item in unique_tuts:
            filehandle.write('%s\n' % item)
