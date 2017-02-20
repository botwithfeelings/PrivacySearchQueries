
# coding: utf-8

# In[53]:

from __future__ import division
import csv
import os
import glob
import pandas as pd
from datetime import datetime
from math import ceil


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


# In[81]:

def process_trends(trendsdir, seed, resultdir):
    # Make results directory if not exists.
    if not os.path.exists(resultdir):
        os.makedirs(resultdir)
        
    result_file = os.path.join(resultdir, seed + ".csv") 

    dirname = os.path.join(trendsdir, seed + " comp")
    filenames = get_trend_files(dirname, "csv")
    
    # Sanity Check: is there trend data for the reference (seed).
    ref_file = os.path.join(dirname, seed + ".csv")
    if ref_file not in filenames:
        print seed
        return
    
    resultdf = pd.DataFrame()
    date_col_added = False
    
    for fname in filenames:
        df = load_trends_df(fname)
        query = df.columns[1]
        
        # Check if there is any trends data for this query.
        query_vals = df[query]
        if not (query_vals > 0).any():
            continue

        if not date_col_added:
            resultdf = pd.concat([resultdf, df.ix[:, 0]], axis=1)
            date_col_added = True
            
        # Check if the query values have the peak, if so we need to
        # have things scaled.
        if (query_vals == 100).any():
            seed_vals = df[seed]
            scale_factor = 100/max(seed_vals)
            df[query] = df[query].apply(lambda x: int(ceil(x*scale_factor)))
            
        # Append this to the result dataframe.
        resultdf = pd.concat([resultdf, df[query]], axis=1)
                              
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


# In[79]:

trendsdir = "./gtrends/with_seed_cmp/"
seed = "search without history"
resultdir = "./indextrends/"
process_trends(trendsdir, seed, resultdir)

