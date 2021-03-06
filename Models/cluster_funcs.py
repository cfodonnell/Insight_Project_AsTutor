import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def find_optimal_clusters(data, max_k):
    '''Returns a kmeans elbow plot in the chosen range''' 

    iters = range(2, max_k+1, 2)
    
    sse = []
    for k in iters:
        sse.append(MiniBatchKMeans(n_clusters=k, init_size=1024, batch_size=2048, random_state=20).fit(data).inertia_)
        print('Fit {} clusters'.format(k))
        
    f, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Plot')
    
def assign_cluster(kmeans, tfidf, subjects):
    '''Returns the closest cluster for a given string of subjects''' 
    
    centroids = kmeans.cluster_centers_
    diff =  centroids - np.array(tfidf.transform(subjects).todense())
    return np.argmin(np.array([np.linalg.norm(d) for d in diff]))
    
def plot_tsne_pca(data, labels):
    '''Plot PCA and TSNE plots of clustered text'''

    max_label = max(labels)
    max_items = np.random.choice(range(data.shape[0]), size=5000, replace=False)
    
    pca = PCA(n_components=2).fit_transform(data[max_items,:].todense())
    tsne = TSNE().fit_transform(PCA(n_components=50).fit_transform(data[max_items,:].todense()))
    
    
    idx = np.random.choice(range(pca.shape[0]), size=1000, replace=False)
    
    # choose only labels associated with subset of data 
    label_subset = labels[max_items]
    label_subset = [cm.hsv(i/max_label) for i in label_subset[idx]]
    
    f, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    ax[0].scatter(pca[idx, 0], pca[idx, 1], c=label_subset)
    ax[0].set_title('PCA Cluster Plot')
    
    ax[1].scatter(tsne[idx, 0], tsne[idx, 1], c=label_subset)
    ax[1].set_title('TSNE Cluster Plot')
    
def get_top_keywords(data, clusters, labels, n_terms):
    '''Returns the top 10 most common words associated with each cluster'''

    df = pd.DataFrame(data.todense()).groupby(clusters).mean()
    
    for i,r in df.iterrows():
        print('\nCluster {}'.format(i))
        print(','.join([labels[t] for t in np.argsort(r)[-n_terms:]]))
        
def subj_rank(subj, subj_pop):
    '''Returns an array of subjects, ranked by popularity'''

    if subj in subj_pop['subjects_lower'].values:
        return np.where(subj_pop['subjects_lower'].values == subj)[0][0]
    else:
        return 0

def real_subs(subj, subj_pop):
    '''Filters out phrases which are not exact matches with a subject name (e.g. last word in one subject
    followed by first word in different unrelated subject.'''
    
    if subj in subj_pop['subjects_lower'].values:
        idx = np.where(subj_pop['subjects_lower'].values == subj)[0][0]
        if subj_pop['hours_tutoring'].iloc[idx] >200000:
            return subj_pop['subjects'].iloc[idx]
        else:
            return ''
    else:
        return ''