
# coding: utf-8

# In[1]:

from pytrends.pyGTrends import pyGTrends
import csv
import argparse
import traceback


# In[4]:

def get_trend_data(conn, term, path, label):
    # Concoct the dictionary for querying gtrends.
    payload = dict()
    payload['q'] = term
    payload['geo'] = 'US'
    payload['hl'] = 'en-US'
    payload['date'] = '01/2011 66m'
    try:
        conn.request_report(payload)
        conn.save_csv(path, label)
    except Exception as e:
        print str(e)
        print traceback.print_exc()


# In[6]:

def main():
    ap = argparse.ArgumentParser(description='Argument parser for google trends api script')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=True)
    args = ap.parse_args()
    
    conn = pyGTrends('privacyprojectncsu1@gmail.com','privacyproject')
    with open(args.f, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            trend_term = row[0]
            trend_label = trend_term.replace('/', '_')
            get_trend_data(conn, trend_term, './gtrends/', trend_label)
    return


# In[5]:

if __name__ == '__main__':
    main()

