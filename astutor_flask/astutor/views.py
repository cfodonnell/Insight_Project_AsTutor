from flask import render_template
from flask import request
from astutor import app
from astutor.model_funcs import qual_encode
from astutor.model_funcs import load_model
from astutor.model_funcs import load_encodings
from astutor.model_funcs import edu_length
from astutor.model_funcs import all_insts
from astutor.model_funcs import is_ivy
from astutor.model_funcs import *
import pandas as pd
import numpy as np
import psycopg2


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )
       
@app.route('/input')
def tutor_input():
    return render_template("tutor_input.html")
    
@app.route('/output',methods=['GET', 'POST'])
def tutor_output():
    
    if request.method == 'POST':
    	
    	years_exp = int(request.form.get('tutor_exp'))
    	hours_tutored = int(request.form.get('tutor_hours'))
    	monday = float(request.form.get('monday_hours'))/24
    	tuesday = float(request.form.get('tuesday_hours'))/24
    	wednesday = float(request.form.get('wednesday_hours'))/24
    	thursday = float(request.form.get('thursday_hours'))/24
    	friday = float(request.form.get('friday_hours'))/24
    	saturday = float(request.form.get('saturday_hours'))/24
    	sunday = float(request.form.get('sunday_hours'))/24
    	qual1 = request.form.get('tutor_deg1')
    	qual2 = request.form.get('tutor_deg2')
    	qual3 = request.form.get('tutor_deg3')
    	tut_loc = request.form.get('tutor_loc')
    	subj_science = request.form.getlist('science')
    	subj_math = request.form.getlist('math')
    	subj_sport = request.form.getlist('sport')
    	subj_exam = request.form.getlist('exam-qualification')
    	subj_hum = request.form.getlist('social-humanities')
    	subj_eng = request.form.getlist('english')
    	subj_lang = request.form.getlist('language')
    	subj_computer = request.form.getlist('computer')
    	subj_fin = request.form.getlist('finance-business-law')
    	subj_art = request.form.getlist('arts-music')
    	subj_gen = request.form.getlist('general-other')
    	inst1 = request.form.get('inst1')
    	inst2 = request.form.get('inst2')
    	inst3 = request.form.get('inst3')

    # encode qualifications to numeric ranking
    all_quals = [qual1,qual2,qual3]
    qual_tot = 0

    for qual in all_quals:
        qual_tot += qual_encode(qual)
        
    # find total education length
    edu_len = edu_length(all_quals)
    inst = all_insts(inst1,inst2,inst3)
    ivy = is_ivy(inst1,inst2,inst3)
    
    # create total subject list
    subj_all = subj_math + subj_science + subj_sport + subj_exam + subj_hum + subj_eng + subj_lang + subj_computer + subj_fin + subj_art + subj_gen
    num_subjects = len(subj_all)
    subj_comb = (' ').join(subj_all)
    
    # load model
    model = load_model()
    encodings = load_encodings()
    
    # load tfidf models and PCA models
    tfidf_sub = load_tfidf_sub()
    tfidf_ed = load_tfidf_ed()
    subPCA = load_PCA_sub()
    edPCA = load_PCA_ed()
    kmeans = load_kmeans()
    
    # constants
    rating_count = 10
    rating_av = 4.895
    review_count = 1
    back_check = 1
    bio_length = 303
    
    # tfidf and pca
    text_ed = tfidf_ed.transform([inst])
    ed_df = pd.Series(edPCA.transform(text_ed.todense())[0]).to_frame().T
    ed_df = ed_df.rename(columns={0:'ed_0',1:'ed_1'})
    
    text_sub = tfidf_sub.transform([subj_comb])
    sub_df = pd.Series(subPCA.transform(text_sub.todense())[0]).to_frame().T
    sub_df = sub_df.rename(columns={0:'sub_0',1:'sub_1',2:'sub_2',3:'sub_3',4:'sub_4'})
    
    
    # encode categorical features
    
    cats = pd.Series({'state':tut_loc,'ivy_1e':ivy[0],'ivy_2e':ivy[1],'ivy_3e':ivy[2]})
    user_cats = encodings.transform(cats.to_frame().T).add_suffix('_cb')
    
    user_input = pd.Series({'qual_encoded':qual_tot, 'background_check':back_check, 'num_subjects':num_subjects,
                          'hours_tutoring':hours_tutored, 'edu_length':edu_len, 'bio_length': bio_length,
                        'sunday_hours': sunday,'monday_hours': monday, 'tuesday_hours': tuesday,
                        'wednesday_hours': wednesday,'thursday_hours': thursday, 'friday_hours': friday, 
                        'saturday_hours': saturday, 'rating_count':rating_count, 'rating_av': rating_av,
                       'review_count':review_count,'experience':years_exp, 'exptext': years_exp, 
                        'exp_tot':years_exp})
                        
    u_input = user_input.to_frame().T.join(user_cats).join(sub_df).join(ed_df)
    u_input = u_input[['qual_encoded', 'num_subjects', 'hours_tutoring', 'edu_length',
       'rating_count', 'review_count', 'rating_av', 'bio_length',
       'sunday_hours', 'monday_hours', 'tuesday_hours', 'wednesday_hours',
       'thursday_hours', 'friday_hours', 'saturday_hours', 'experience',
       'sub_0', 'sub_1', 'sub_2', 'sub_3', 'sub_4', 'ed_0', 'ed_1', 'exptext',
       'exp_tot', 'state_cb', 'ivy_1e_cb', 'ivy_2e_cb', 'ivy_3e_cb']]
    
    the_result = np.exp(model.predict(u_input.values))[0].round()
    
    with open('./sql_id.txt', 'r') as f:
        cred = [x.replace("'", '').strip() for x in f]
        dbname = cred[0]
        username = cred[1]
        pswd = cred[2]
        
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    
    clus_assigned = assign_cluster(kmeans, tfidf_sub, [subj_comb])
    sql_query = """
    SELECT clus_""" + str(clus_assigned) + """ FROM pop_subjects_weighted
    ;
    """
    pop_subjs_sql = pd.read_sql_query(sql_query,con)
    
    ndarr = pop_subjs_sql.values.tolist()
    pop_flat = [x for sublist in ndarr for x in sublist]
    missing_subs = [item for item in pop_flat if item not in subj_all]
    if len(missing_subs) >= 10:
        missing_subs = missing_subs[:10]
        
    missing_subs_list = (', ').join(missing_subs)
    
    num_subjects_new = len(subj_all) + len(missing_subs)
    subj_comb_new = (' ').join(subj_all + missing_subs)
    text_sub_new = tfidf_sub.transform([subj_comb_new])
    sub_df_new = pd.Series(subPCA.transform(text_sub_new.todense())[0]).to_frame().T
    
    u_input['num_subjects'].iloc[0] = num_subjects_new
    u_input['sub_0'].iloc[0] = sub_df_new[0].iloc[0]
    u_input['sub_1'].iloc[0] = sub_df_new[1].iloc[0]
    u_input['sub_2'].iloc[0] = sub_df_new[2].iloc[0]
    u_input['sub_3'].iloc[0] = sub_df_new[3].iloc[0]
    u_input['sub_4'].iloc[0] = sub_df_new[4].iloc[0]
    res_new = np.exp(model.predict(u_input.values))[0].round()
    the_result_new = '$' + str(res_new) + '/hour'
    #the_result_new = clus_assigned
    
    if res_new > the_result:
        text_1 = "Listed below are some highly sought-after subjects that similar users also entered:"
        text_2 = "With these subjects added to your profile, your new suggested rate would be:"
    else:
        text_1 = "Nice! You already have a very strong profile, however similar users also listed the following subjects in their profiles. Consider adding them to your profile to boost your reach!"
        text_2 = ""
        the_result_new = ""
    
    return render_template("tutor_output.html", the_result = the_result, missing_subs = missing_subs_list, the_result_new = the_result_new, text_1 = text_1, text_2 = text_2)
