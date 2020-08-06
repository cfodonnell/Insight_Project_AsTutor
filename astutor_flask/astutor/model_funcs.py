import pickle
import numpy as np
import xgboost

def load_model():
    return pickle.load(open('model_xgb3.sav', 'rb'))
    
def load_encodings():
    return pickle.load(open('cbenc2.pkl', 'rb'))
    
def load_tfidf_sub():
    return pickle.load(open('tfidf.sav', 'rb'))
    
def load_tfidf_ed():
    return pickle.load(open('tfidf_ed.sav', 'rb'))
    
def load_PCA_sub():
    return pickle.load(open('subPCA.pkl', 'rb'))
    
def load_PCA_ed():
    return pickle.load(open('edPCA.pkl', 'rb'))
    
def load_kmeans():
    return pickle.load(open('kmeans_16.sav', 'rb'))
    
def assign_cluster(kmeans, tfidf, subjects):
    '''Returns the closest cluster for a given string of subjects''' 
    
    centroids = kmeans.cluster_centers_
    diff =  centroids - np.array(tfidf.transform(subjects).todense())
    return np.argmin(np.array([np.linalg.norm(d) for d in diff]))
    
    
def qual_encode(qual):
    
    qual_list = ['Masters','MBA','PhD','J.D.']
    qual_encodings = {'Masters': 1, 'MBA': 1, 'PhD': 2, 'J.D.': 3}
    if qual in qual_list:
        return qual_encodings[qual]
    else:
        return 0

def edu_length(quals):
    edu = np.array(quals)
    edu_len = len(edu[edu!=0])
    return 3*edu_len + 1
    
def all_insts(inst1,inst2,inst3):

    inst = inst1 + ' ' + inst2 + ' ' + inst3 
    stopwords = ['university','University','of','in','College','college']
    for word in stopwords:
        inst = inst.replace(word,'').strip(' ')
    return inst
    
def is_ivy(inst1,inst2,inst3):
    ivys = ['Brown', 'Columbia', 'Dartmouth', 'Harvard', 'Cornell', 'Pennsylvania', 'Princeton', 'Yale']
    ivy = []
    for inst in [inst1,inst2,inst3]:
        if any(x in inst for x in ivys):
            ivy.append(1)
        else:
            ivy.append(0)
    return ivy
