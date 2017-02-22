#!/usr/bin/env python2.7
#
# If you pull this code from the repo, you will need to provide a keys file before being able to run it. The keys.py file
# should contain the google authentication credentials (gmail account and their corresponding password) as a list of tuples
# as shown in the following:
# google_auth = [('email1@gmail.com', 'pass1'), ('email2@gmail.com', 'pass2'), ..., ('emailn@gmail.com', 'passn')]
#
# This script can be used to pull Google trends data for a specified query. When a csv is passed with search queries
# of interest in the first column, this script will pull the search history trends for each.
#
#
# You will need to provide the following arguments to the argument parser for this script:
#
# * csv file, containing queries to get trends for
# * seed word, specifies the folder which all trends will be placed within
# * whether all queries should be compared against the seed in the Google Trend results
#
# In running this script, we have identified the following issues that you need to be aware of and potentially
# address:
#
# * Trend data collected is normalized for each query individually. If the data is requested for only one query, the
#   normalization such that the maximum fraction of search volume history in the requested time range will have a value
#   of 100 and all other values will be relative to that. If the history is collected for more than one trend at the
#   same time, the data for all queries will be normalized relative to the maximum of all queries. Therefore, if
#   query histories are requested individually, they cannot be compared directly.
# * Since the trend data retrieved is normalized to the entire Google search volume, care needs to be taken to ensure
#   that a change in a specific trend is not caused by a severe increase/decrease in a small number of queries. The
#   proposed method to accomplish this is by comparing the trend data against several queries which are considered to
#   have a consistent volume across time (life and love) [].
#

# standard library imports
from __future__ import division
import argparse
import csv
from random import randint, shuffle
import os
from time import sleep

# third party imports
from pytrends.request import TrendReq

# local imports
from keys import google_auth
from refs import refs

def get_google_auth():
    """
    Get a random google username/password from the loaded list, if any are available.

    :return: A random username/password combination
    """
    shuffle(google_auth)
    if len(google_auth) > 0:
        return google_auth.pop(0)
    return None


def write_failed_list(filename, seed, failed, count, succ):
    """

    :param filename:
    :param seed:
    :param failed:
    :param count:
    :param succ:
    :return:
    """
    with open(filename, 'w+') as f:
        f.write('\n'.join(failed))
        if succ:
            # Write over any failed list file if exists.
            success_rate = ((count - len(failed)) / count) * 100    
            f.write('\n' + seed + ', sucess rate: ' + str(success_rate) + '%')


def get_trend_data(t, term, trends, failed, seed, comp):
    """

    :param t:
    :param term:
    :param trends:
    :param failed:
    :param seed:
    :param comp:
    :return:
    """
    # First check if we have the data from some other session.
    dir_suffix = seed
    if comp:
        dir_suffix += ' comp'
    label = term.replace('/', '_')        
    filename = os.path.join('./gtrends', dir_suffix, label + '.csv')
    if os.path.isfile(filename):
        return True
    
    kw = list()
    kw.append(term)
    # Concoct the dictionary for querying gtrends.
    if comp:
        kw.append(refs[seed])    
    
    try:
        t.build_payload(kw, timeframe='2011-01-01 2017-01-31')
        df = t.interest_over_time()
        df.to_csv(filename)
    except Exception as e:
        print 'No trend data for: ' + term, repr(e)
        failed.append(term)
    return True


def run_google_trends(trends_file, seed, comp, limit):
    """
    Collect the trend data for all queries in a file if the data exists. This function has the ability to recover from
    failure if Google's anti-spam prevention temporarily causes the trend collection from failing.

    :param trends_file: The csv file containing the queries to retrieve trends for. The queries must be located in the
                        first columns.
    :param seed: The seed word associated with the trends file. This will define the directory used to store the trends
                 collected. It will also be added to the trends data collected for each query in trends_file (if comp
                 parameter is set to True).
    :param comp: Set to True if you want to compare the seed word against all queries when collecting trend data. This
                 allows all trends collected to have a common reference point.
    :param limit: No. of trend request to make per hour.             
    :return: None
    """
    dir_suffix = seed
    if comp:
        dir_suffix += ' comp'

    directory = os.path.join('./gtrends', dir_suffix)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Retrieve the list of keywords to be fetched into a list.
    trends_list = list()
    with open(trends_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            trends_list.append(row[0])

    count = len(trends_list)
    sleep_time = 3600/int(limit)

    # Retrieve the list of failed requests if any.
    failed_file = os.path.join('./gtrends', dir_suffix, seed + ' no trends data.txt')
    failed_list = list()
    if os.path.isfile(failed_file):
        with open(failed_file, 'r') as f:
            failed_list = list(map(str.strip, f.readlines()))
    
    # Get authentication keys.
    google_user, google_pass = get_google_auth()
    py_trends = TrendReq(google_user, google_pass, custom_useragent='WSPR PrivacySearchQueries')
    while trends_list:
        term = trends_list.pop(0)
        if term in failed_list:
            continue
        succ = get_trend_data(py_trends, term, trends_list, failed_list, seed, comp)
        if not succ:
            print 'Google authentications exhausted, wait a few minutes and try again.'
            break
        
        sleep(randint(sleep_time, sleep_time+5))
    
    write_failed_list(failed_file, seed, failed_list, count, True)
    return

def main():
    ap = argparse.ArgumentParser(description='Use the script to pull google trends data.')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=True)
    ap.add_argument('-s', '-seed', help='Seed Word. All csv files to be written inside same name directory within '
                                        'gtrends', required=True)
    ap.add_argument('-c', '-cmp', help='Enable comparison with seed word', action='store_true')
    ap.add_argument('-k', '-keywordlimit', help='limit to number of keyword request per hour', default=30)
    args = ap.parse_args()

    run_google_trends(args.f, args.s, args.c, args.k)
    return

if __name__ == '__main__':
    main()
