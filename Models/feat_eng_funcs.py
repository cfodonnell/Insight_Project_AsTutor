import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as esw

def qual_encode(qual):
    '''Assign a numerical value to each qaulification, with Masters/MBA determined to be the least valuable and PhD/J.D. determined
    to be the most valuable.'''
    
    qual_list = ['Masters','MBA','PhD','J.D.']
    qual_encodings = {'Masters': 5, 'MBA': 5, 'PhD': 20, 'J.D.': 30}
    if qual in qual_list:
        return qual_encodings[qual]
    else:
        return 0
    
def get_exp(bio):
    '''Extract an estimate for a tutor's total years of experience. Tutors often mention this in their bio section, either in
    a numerical or textual description of their years teaching a subject. Ignore any numbers greater than 50, as this is
    unrealistic. This function looks for years in digit form.'''
    
    if 'years' in bio:
        yrs = np.array([int(i) for i in re.findall('\d+', bio)])
        if len(yrs[yrs<50])>0:
            return max(yrs[yrs<50])
        else:
            return 0
    else:
        return 0
    
def get_exp_text(bio):
    '''Extract an estimate for a tutor's total years of experience. Tutors often mention this in their bio section, either in
    a numerical or textual description of their years teaching a subject. Ignore any numbers greater than 50, as this is
    unrealistic. This function looks for years in text form.'''
    
    numbers = ['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve',
          'thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','thirty',
          'forty','fifty']
    numbers_dict = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
                'eleven':11,'twelve':12, 'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,
                'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50}
    
    if any(x in bio.lower() for x in numbers):
        matches = [x for x in numbers if x in bio.lower()]
        return sum([numbers_dict[x] for x in matches])
    else:
        return 0
    
def tfidf_encode(text):
    '''Encode a passage of text using TFIDF vectorization. Use a max number of features of 20000, and consider 1 and 2 word
    sequences.'''
    
    stopWords = esw 

    tfidf = TfidfVectorizer(
    min_df = 0,
    max_df = 0.95,
    max_features = 20000,
    stop_words = stopWords,
    ngram_range = (1,2)
    )
    tfidf.fit(text)
    
    return tfidf.transform(text)
    


