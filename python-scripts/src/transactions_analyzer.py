#!/usr/bin/python3
from configparser import ConfigParser
import psycopg2
from sqlalchemy import create_engine
from ipywidgets import interact, interactive, fixed, interact_manual
import pandas as pd
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    
    # Checks to see if section (postgresql) parser exists
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
         
    # Returns an error if a parameter is called that is not listed in the initialization file
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def get_postgresql_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def create_engine_with_config():
    """ Create engine with database config """
    engine = None
    try:
        # read connection parameters
        params = config()
        engine = create_engine('postgresql://postgres:'+params.get('password')+'@'+params.get('host')+'/'+params.get('database'))
    finally:
        if engine is not None:
            print('engine created!')
    return engine

def get_tx_pool_transcations():
    engine=create_engine_with_config()
    tx_transaction = pd.read_sql('select * from aggron_transaction order by enter_time DESC limit 200',engine)
    return tx_transaction

def get_proposed_transactions():
    engine=create_engine_with_config()
    proposed_transaction = pd.read_sql('select * from aggron_subscribe_proposed_transaction order by time DESC limit 200 ',engine)
    return proposed_transaction

def get_new_transactions():
    engine=create_engine_with_config()
    new_transaction = pd.read_sql('select * from aggron_subscribe_new_transaction order by time DESC limit 200 ',engine)
    return new_transaction

def get_new_transactions_by_hash(tx_hash):
    engine=create_engine_with_config()
    query_subscribe_new_transaction= 'SELECT * FROM aggron_subscribe_new_transaction WHERE 1=1'
    query_tx_transaction= 'SELECT * FROM aggron_transaction WHERE 1=1'
    query_proposed_transaction= 'SELECT * FROM aggron_subscribe_proposed_transaction WHERE 1=1'

    if len(tx_hash) !=0:
        query_subscribe_new_transaction +='AND transaction_hash =' + "'"+tx_hash+ "'"
        query_tx_transaction +='AND hash =' + "'"+tx_hash+ "'"
        query_proposed_transaction +='AND transaction_hash =' + "'"+tx_hash+ "'"
    subscribe_new_transaction = pd.read_sql(query_subscribe_new_transaction,engine)
    tx_transaction = pd.read_sql(query_tx_transaction,engine)
    proposed_transaction = pd.read_sql(query_proposed_transaction,engine)

    return subscribe_new_transaction,tx_transaction,proposed_transaction

def latency_of_pending_to_ommitted():
    engine=create_engine_with_config()
    sql='SELECT commit_time AS time,extract(epoch from (commit_time - enter_time)) AS "From Pending to Committed" FROM aggron_transaction WHERE commit_time IS NOT NULL AND commit_time > current_timestamp - interval \'6 hour\' ORDER BY time'
    latency_of_pending_to_ommitted = pd.read_sql(sql,engine)
    return latency_of_pending_to_ommitted

def remove_lapsed():
    engine=create_engine_with_config()
    sql='SELECT remove_time AS time, extract(epoch from (remove_time - enter_time)) AS "Remove Elapsed" FROM aggron_transaction WHERE remove_time IS NOT NULL AND remove_time > current_timestamp - interval \'6 hour\' ORDER BY time'
    remove_lapsed = pd.read_sql(sql,engine)
    return remove_lapsed


if __name__ == '__main__':
    # config()
    # get_postgresql_connection()
#    tx_hash='0x21da2455dc65524945b1163df70e1e7fe5f747462e0fd4173751fad51ed465af'
#    subscribe_new_transaction,tx_transaction,proposed_transaction = get_new_transactions_by_hash(tx_hash)
#    print(subscribe_new_transaction)
#    print(tx_transaction)
#    print(proposed_transaction)
    get_postgresql_connection()