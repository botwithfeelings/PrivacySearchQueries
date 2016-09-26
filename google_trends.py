
# coding: utf-8

# In[18]:

from pytrends.request import TrendReq, ResponseError, RateLimitError
from random import randint
from time import sleep
from keys import google_user, google_pass
import csv
import argparse
import traceback
import os
import pandas as pd


# In[16]:

MIN_WAIT = 5
trend_keywords = list()
no_response_list = list()
NO_TRENDS_KEYWORDS_FILE = './gtrends/no_trends_data.txt'


# In[30]:

def get_trend_data(t, term, label, directory):
    # Concoct the dictionary for querying gtrends.
    payload = dict()
    payload['q'] = term
    payload['geo'] = 'US'
    payload['hl'] = 'en-US'
    payload['date'] = '01/2011 66m'
    try:
        df = t.trend(payload, return_type='dataframe')
        filename = directory + '/' + label + '.csv'
        df.to_csv(filename)
    except RateLimitError:
        print 'Request limit exceeded, incrementing wait time between requests.'
        # Increase time between requests and put back in the keywords list.
        MIN_WAIT += 5
        trend_keywords.append(term)
    except (ResponseError, IndexError):
        print 'No trend data for: ' + term
        no_response_list.append(term)


# In[24]:

def main():
    ap = argparse.ArgumentParser(description='Argument parser for google trends api script')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=True)
    ap.add_argument('-d', '-dir', help='All csv files to be written inside this directory within gtrends', required=True)
    args = ap.parse_args()
    
    directory = './gtrends/' + args.d
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Retrieve the list of keywords to be fetched into a list.
    with open(args.f, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            trend_keywords.append(row[0])
    
    pyTrends = TrendReq(google_user, google_pass)
    while trend_keywords:
        term = trend_keywords.pop(0)
        label = term.replace('/', '_')
        get_trend_data(pyTrends, term, label, directory)
        sleep(randint(MIN_WAIT, MIN_WAIT * 2))
        
    with open(NO_TRENDS_KEYWORDS_FILE, 'a') as f:
        f.write('\n'.join(no_response_list))
    return


# In[ ]:

if __name__ == '__main__':
    main()

