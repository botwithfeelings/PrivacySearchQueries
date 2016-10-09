
# coding: utf-8

# In[5]:

from __future__ import division
from pytrends.request import TrendReq, ResponseError, RateLimitError
from random import randint, shuffle
from time import sleep
from keys import google_auth
import csv
import argparse
import traceback
import os
import pandas as pd


# In[17]:

MIN_WAIT = 5


# In[6]:

def get_google_auth():
    shuffle(google_auth)
    if len(google_auth) > 0:
        return google_auth.pop(0)
    return None


# In[44]:

def write_failed_list(filename, seed, failed, count, succ):
    with open(filename, 'w+') as f:
        f.write('\n'.join(failed))
        success_rate = 0
        if succ:
            # Write over any failed list file if exists.
            success_rate = ((count - len(failed)) / count) * 100    
            f.write('\n' + seed + ', sucess rate: ' + str(success_rate) + '%')


# In[36]:

def get_trend_data(t, term, trends, failed, seed):
    # First check if we have the data from some other session.
    label = term.replace('/', '_')        
    filename = os.path.join('./gtrends', seed, label + '.csv')
    if os.path.isfile(filename):
        return True
    
    # Concoct the dictionary for querying gtrends.
    payload = dict()
    payload['q'] = term
    payload['geo'] = 'US'
    payload['hl'] = 'en-US'
    payload['date'] = '01/2011 66m'
    try:
        df = t.trend(payload, return_type='dataframe')
        df.to_csv(filename)
    except RateLimitError:
        print 'Request limit exceeded, switch users.'
        trends.append(term)
        return False        
    except (ResponseError, IndexError):
        print 'No trend data for: ' + term
        failed.append(term)
    return True


# In[41]:

def main():
    ap = argparse.ArgumentParser(description='Use the script to pull google trends data.')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=True)
    ap.add_argument('-d', '-dir', help='All csv files to be written inside this directory within gtrends', required=True)
    args = ap.parse_args()
    
    trends_file = args.f
    seed = args.d
    
    directory = os.path.join('./gtrends', seed)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Retrieve the list of keywords to be fetched into a list.
    trends_list = list()
    with open(trends_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            trends_list.append(row[0])
            
    count = len(trends_list)
    
    # Retrieve the list of failed requests if any.
    failed_file = os.path.join('./gtrends', seed, seed + ' no trends data.txt')
    failed_list = list()
    if os.path.isfile(failed_file):
        with open(failed_file, 'r') as f:
            failed_list = list(map(str.strip, f.readlines()))
    
    # Get authentication keys.
    google_user, google_pass = get_google_auth()
    pyTrends = TrendReq(google_user, google_pass)
    while trends_list:
        term = trends_list.pop(0)
        if term in failed_list:
            continue
        
        succ = get_trend_data(pyTrends, term, trends_list, failed_list, seed)
        sleep(randint(MIN_WAIT, MIN_WAIT * 2))
        if not succ:
            # Request limit exceeded, establish new connection.
            auth = get_google_auth()
            if auth is not None:
                google_user, google_pass = auth
                pyTrends = TrendReq(google_user, google_pass)        
            else:
                print 'Google authentications exhausted, wait a few minutes and try again.'
                write_failed_list(failed_file, seed, failed_list, count, False)
                return
        
    write_failed_list(failed_file, seed, failed_list, count, True)
    return


# In[22]:

if __name__ == '__main__':
    main()

