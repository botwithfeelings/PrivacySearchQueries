
# coding: utf-8

# In[2]:

from pytrends.request import TrendReq
from random import randint
from keys import google_user, google_pass
import csv
import argparse
import traceback
import pandas as pd


# In[7]:

def get_trend_data(t, term, label):
    # Concoct the dictionary for querying gtrends.
    payload = dict()
    payload['q'] = term
    payload['geo'] = 'US'
    payload['hl'] = 'en-US'
    payload['date'] = '01/2011 66m'
    try:
        df = t.trend(payload, return_type='dataframe')
        filename = './gtrends/' + label + '.csv'
        df.to_csv(filename)
    except Exception as e:
        print str(e)
        print traceback.print_exc()


# In[3]:

def main():
    ap = argparse.ArgumentParser(description='Argument parser for google trends api script')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=True)
    args = ap.parse_args()
    
    pyTrends = TrendReq(google_user, google_pass)
    with open(args.f, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            trend_term = row[0]
            trend_label = trend_term.replace('/', '_')
            get_trend_data(pyTrends, trend_term, trend_label)
    return


# In[ ]:

if __name__ == '__main__':
    main()

