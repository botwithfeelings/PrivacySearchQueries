#!/usr/bin/env python2.7
#
# NOTE: This script is dependent on the pytrends package which updated on a regular basis depending on the changes in the
# google trends website interface and export changes. If the package gets updated, this script is likely to be broken.
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
import operator as op
import pandas as pd
from time import sleep
from math import ceil

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

def get_pytrends_obj():
    """
    Picks a google credential randomly and creates a
    pytrends object to pull trends data.
    """
    # Get authentication keys.
    google_user, google_pass = get_google_auth()
    py_trends = TrendReq(google_user, google_pass, custom_useragent='WSPR PrivacySearchQueries')
    return py_trends

def get_trend_data(t, term, failed, seed, comp, sleep_time):
    """

    :param t:
    :param term:
    :param trends:
    :param failed:
    :param seed:
    :param comp:
    :param sleep_time:
    :return:
    """
    # First check if we have the data from some other session.
    dir_suffix = seed
    if comp:
        dir_suffix += ' comp'
    label = term.replace('/', '_')
    filename = os.path.join('./gtrends', dir_suffix, label + '.csv')
    if os.path.isfile(filename):
        return

    kw = list()
    kw.append(term)
    # Concoct the dictionary for querying gtrends.
    if comp:
        ref = seed
        if seed in refs.keys():
            ref = refs[seed]
        kw.append(ref)

    try:
        t.build_payload(kw, timeframe='2011-01-01 2017-01-31')
        df = t.interest_over_time()
        df.to_csv(filename)
    except Exception as e:
        print 'No trend data for: ' + term, repr(e)
        failed.append(term)

    sleep(randint(sleep_time, sleep_time+5))
    return

def get_trend_data_multiple(t, terms, failed, sleep_time):
    """
    Pulls trend data based on reference scale.
    :param t:
    :param terms:
    :param failed:
    :param sleep_time:
    :return: The dataframe containing the scale.
    """
    scale_df = None
    try:
        t.build_payload(terms, timeframe='2011-01-01 2017-01-31')
        scale_df = t.interest_over_time()
    except Exception as e:
        print 'No trend data for: ' + ', '.join(terms), repr(e)
        failed.extend(terms)

    sleep(randint(sleep_time, sleep_time+5))
    return scale_df


def run_google_trends(trends_file, seed, comp, scale, limit, amt):
    """
    Collect the trend data for all queries in a file if the data exists. This function has the ability to recover from
    failure if Google's anti-spam prevention temporarily causes the trend collection from failing.

    :param trends_file: The csv file containing the queries to retrieve trends for. The queries must be located in the first columns. Overriden by the scale parameter.
    :param seed: The seed word associated with the trends file. This will define the directory used to store the trends collected. It will also be added to the trends data collected for each query in trends_file (if comp parameter is set to True).
    :param comp: Set to True if you want to compare the seed word against all queries when collecting trend data. This allows all trends collected to have a common reference point.
    :param scale: Set to True if you want to pull trends data for the seed (reference for seed) comparison scale for the given seed. This will override the comp parameter.
    :param limit: No. of trend request to make per hour.
    :param amt: Indicate which seed queries list to use.
    :return: None
    """
    dir_suffix = seed
    if comp:
        dir_suffix += ' comp'

    if scale:
        dir_suffix = 'seed_scales'

    directory = os.path.join('./gtrends', dir_suffix)
    if not os.path.exists(directory):
        os.makedirs(directory)

    sleep_time = 3600/int(limit)

    if scale:
        seed_file = "./seed_queries.txt"
        if bool(amt):
            seed_file = "./seed_queries_amt.txt"

        # Load the seeds list.
        seed_list = list()
        with open(seed_file, 'r') as f:
            seed_list = f.readlines()

        pull_seed_scale(dir_suffix, seed, sleep_time, seed_list)
    else:
        # If there is no such file just return
        if not os.path.isfile(trends_file):
            return

        # Retrieve the list of keywords to be fetched into a list.
        trends_list = list()

        # If the trends file is from AMT then treat it as a text file due to
        # MAC csv formatting issues.
        with open(trends_file, 'r') as f:
            if bool(amt):
                trends_list = f.readlines()
            else:
                reader = csv.reader(f)
                for row in reader:
                    trends_list.append(row[0])

        pull_seed_trends(trends_list, dir_suffix, seed, sleep_time, comp)

    return

def load_failed_list(failed_file):
    """
    Loads the list of terms without trend data.
    :param failed_file: File containing the list of failed terms.
    :return: The list of terms without trends data.
    """
    failed_list = list()
    if os.path.isfile(failed_file):
        with open(failed_file, 'r') as f:
            failed_list = list(map(str.strip, f.readlines()))
    return failed_list

def pull_seed_scale(dir_suffix, seed, sleep_time, seed_list):
    """
    Builds the seed to seed scale for a given seed.
    :param dir_suffix: The directory inside gtrends folder containing the scale files.
    :param seed: The seed query.
    :param sleep_time: Amount of time to wait between trend requests.
    :param seed_list: List of seeds for comparison in the scale
    :return: None.
    """
    # Retrieve the list of failed requests if any.
    failed_file = os.path.join('./gtrends', dir_suffix, seed + ' no trends data.txt')
    failed_list = load_failed_list(failed_file)

    # Iterate over the reference dictionary and make pull requests.
    py_trends = get_pytrends_obj()
    ref = seed
    if seed in refs.keys():
        ref = refs[seed]
    terms = [ref]

    # Pull the reference data trends to check if we can go further.
    ref_df = get_trend_data_multiple(py_trends, terms, failed_list)

    # If there aren't any trend data for the reference
    # for current seed, we can't do anything about it's scale.
    if ref_df is None:
        return
    ref_vals_scaled = ref_df[ref]
    if not (ref_vals_scaled > 0).any():
        return

    ref_df = pd.DataFrame()
    ref_df = pd.concat([ref_df, ref_vals_scaled], axis=1)

    # Load the seed queries list
    for s in seed_list:
        if s != seed:
            r = s
            if s in refs.keys():
                r = refs[s]
            terms.append(r)
        else:
            continue

        scale_df = get_trend_data_multiple(py_trends, terms, failed_list, sleep_time)

        # Remove all the terms except the seed for the next request.
        del terms[1:]

        # Process the dataframe and combine it with the other.
        col_names = scale_df.columns.values.tolist()
        col_names.remove(ref)
        # If there aren't any value for the reference columns then
        # we can't do anything.
        ref_vals = scale_df[ref]
        if not (ref_vals > 0).any():
            failed_list.extend(col_names)
            continue

        # Determine the scale factor from the reference column.
        max_ref_val = max(ref_vals)
        scale_factor = 100/max_ref_val
        do_scale = lambda x: int(ceil(x*scale_factor))
        ref_vals = ref_vals.apply(do_scale)

        # Get the sum of the absolute difference
        # between scaled reference values.
        scaled_diff = sum(map(op.abs, map(op.sub, ref_vals, ref_vals_scaled)))

        # If the scaled difference is more than 2.5 for each of the rows
        # in the dataframe then there is only minute data for these terms.
        # Compared to the peak, the maximum value is very small. So, we
        # shouldn't scale in this case.
        if scaled_diff > int(scale_df.shape[0]*2.5):
            failed_list.extend(col_names)
            continue

        for col in scale_df.columns:
            if col not in ref_df.columns:
                col_vals = scale_df[col].apply(do_scale)
                if (col_vals > 0).any():
                    ref_df = pd.concat([ref_df, col_vals], axis=1)
                else:
                    failed_list.append(col)

    # Write failed list if any.
    if failed_list:
        write_failed_list(failed_file, seed, failed_list, len(refs), True)

    # Push the scale dataframe to csv file.
    scale_file = os.path.join('./gtrends', dir_suffix, seed + '.csv')
    ref_df.to_csv(scale_file, index=True)
    return

def pull_seed_trends(trends_list, dir_suffix, seed, sleep_time, comp):
    """
    Pulls the seed trend data for a given seed.
    :param trends_list: The list file containing the queries to retrieve trends for. Overriden by the scale parameter.
    :param dir_suffix: The directory inside gtrends folder containing the scale files.
    :param seed: The seed query.
    :param sleep_time: Amount of time to wait between trend requests.
    :param comp: Set to True if you want to compare the seed word against all queries when collecting trend data. This allows all trends collected to have a common reference point.
    :return: None.
    """
    count = len(trends_list)

    # Retrieve the list of failed requests if any.
    failed_file = os.path.join('./gtrends', dir_suffix, seed + ' no trends data.txt')
    failed_list = load_failed_list(failed_file)

    py_trends = get_pytrends_obj()
    while trends_list:
        term = trends_list.pop(0)
        if term in failed_list:
            continue

        print term

        get_trend_data(py_trends, term, failed_list, seed, comp, sleep_time)

    write_failed_list(failed_file, seed, failed_list, count, True)
    return

def main():
    ap = argparse.ArgumentParser(description='Use the script to pull google trends data.')
    ap.add_argument('-f', '-file', help='CSV file containing trend keywords at column 0', required=False)
    ap.add_argument('-s', '-seed', help='Seed Word. All csv files to be written inside same name directory within '
                                        'gtrends', required=True)
    ap.add_argument('-c', '-cmp', help='Enable comparison with seed word', action='store_true')
    ap.add_argument('-l', '-scale', help='Enable seed to seed comparison scale', action='store_true')
    ap.add_argument('-k', '-keywordlimit', help='limit to number of keyword request per hour', default=200)
    ap.add_argument('-a', '-amt', help='Use the AMT seed list rather than the index one', action='store_true')
    args = ap.parse_args()

    run_google_trends(args.f, args.s, args.c, args.l, args.k, args.a)
    return

if __name__ == '__main__':
    main()
