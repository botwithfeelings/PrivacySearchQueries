
# coding: utf-8

# In[15]:
from __future__ import division
import csv
import os
import glob
import pandas as pd
import numpy as np
from collections import OrderedDict
from datetime import datetime

from trend_stats import cliffs_delta, load_trends_df, kstest2samp

# In[18]:

def get_trend_files(dirname, extension):
    filestring = dirname + '/*.{}'
    files = [i for i in glob.glob(filestring.format(extension))]
    return files


# In[19]:

def save_stats(results, dirname, seed):
    filename = dirname + seed + ".csv"
    if any(results):
        with open(filename, 'w') as f:
            csv_writer = csv.writer(f, lineterminator='\n')
            for (k, v) in results.iteritems():
                csv_writer.writerow([k, v[0], v[1], v[2]])


# In[21]:

def process_trends(trendsdir, seed, splitdate, resultdir):
    # Make results directory if not exists.
    if not os.path.exists(resultdir):
        os.makedirs(resultdir)

    sd = datetime.strptime(splitdate, '%Y-%m-%d')
    dirname = os.path.join(trendsdir, seed)
    filenames = get_trend_files(dirname, "csv")
    results = OrderedDict()
    for fname in filenames:
        df = load_trends_df(fname)
        query = df.columns[1]

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        predf = df[df['date'] < sd]
        postdf = df[df['date'] >= sd]

        prevals = predf[query].values
        postvals = postdf[query].values

        # Compute ks 2-sample test with p-value
        ksval, pvalue = kstest2samp(prevals, postvals)

        # Compute the Cliff's Delta value
        d, flag = cliffs_delta(prevals, postvals)

        results[query] = (ksval, pvalue, d)

    # Save the results into a csv.
    save_stats(results, resultdir, seed)
    return


# In[24]:

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Compute 2 sample ks test and Cliff's Delta for the trend data of a given seed")
    ap.add_argument("-s", "-seed", help="Seed word", required=True)
    ap.add_argument("-d", "-dir", help="Directory containing the trends data for seeds", required=True)
    ap.add_argument("-i", "-inc", help="Incident date to split the trend data in YYYY-m-d format", required=True)
    ap.add_argument("-r", "-rdir", help="Directory to put the results of the compute", required=True)

    args = ap.parse_args()

    trendsdir = args.d
    seed = args.s
    splitdate = args.i
    resultdir = args.r

    process_trends(trendsdir, seed, splitdate, resultdir)
    return


# In[ ]:

if __name__ == "__main__":
    main()
