
# coding: utf-8

# In[53]:

from __future__ import division
import csv
import os
import glob
import pandas as pd
import operator as op
from datetime import datetime
from math import ceil
from refs import refs


# In[3]:

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


# In[4]:

def load_trends_df(filename):
    df = pd.DataFrame()
    if os.path.isfile(filename):
        df = pd.read_csv(filename, header=0)
    return df


# In[82]:

def process_trends(trendsdir, seed, resultdir):
    # Make results directory if not exists.
    if not os.path.exists(resultdir):
        os.makedirs(resultdir)

    result_file = os.path.join(resultdir, seed + ".csv")

    dirname = os.path.join(trendsdir, seed + " comp")
    filenames = get_trend_files(dirname, "csv")

    # Sanity Check: is there trend data for the reference (seed).
    ref = refs[seed]
    ref_file = os.path.join(dirname, ref + ".csv")
    if ref_file not in filenames:
        print seed
        return
    
    # Load the reference file itself for 
    ref_df = load_trends_df(ref_file)
    ref_vals_scaled = ref_df[ref]

    resultdf = pd.DataFrame()
    date_col_added = False

    for fname in filenames:
        df = load_trends_df(fname)
        query = df.columns[1]

        # Check if there is any trends data for this query.
        query_vals = df[query]
        if not (query_vals > 0).any():
            continue
        
        ref_vals = df[ref]
        if not (ref_vals > 0).any():
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
        # in the dataframe then there is only minute data for the ref aginst
        # this term. Compared to the peak, the maximum value is very small. 
        # So, we shouldn't scale in this case.
        if scaled_diff > int(ref_df.shape[0]*2.5):
            continue

        if not date_col_added:
            resultdf = pd.concat([resultdf, df.ix[:, 0]], axis=1)
            date_col_added = True

        query_vals = query_vals.apply(do_scale)

        # Append this to the result dataframe.
        resultdf = pd.concat([resultdf, query_vals], axis=1)

    # Save the dataframe.
    resultdf.to_csv(result_file, index=False)
    return


# In[80]:

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Compute the trend relative data for search index")
    ap.add_argument("-s", "-seed", help="Seed word", required=True)
    ap.add_argument("-t", "-tdir", help="Directory containing the trends data for seeds", required=True)
    ap.add_argument("-r", "-rdir", help="Directory to put the results of the compute", required=True)

    args = ap.parse_args()

    trendsdir = args.t
    seed = args.s
    resultdir = args.r

    process_trends(trendsdir, seed, resultdir)
    return


# In[43]:

if __name__ == "__main__":
    main()
