import psycopg2
from sqlalchemy import create_engine

def open_sql_con():
    '''Open connection to tutor database'''
    
    with open('../sql_id.txt', 'r') as f:
        cred = [x.replace("'", '').strip() for x in f]
        dbname = cred[0]
        username = cred[1]
        pswd = cred[2]
    
    return psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)

def create_sql_engine():
    '''Create engine to write to tutor database'''
    
    with open('../sql_id.txt', 'r') as f:
        cred = [x.replace("'", '').strip() for x in f]
        dbname = cred[0]
        username = cred[1]
        pswd = cred[2]
    
    return create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))