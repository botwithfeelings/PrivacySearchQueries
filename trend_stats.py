
# coding: utf-8

# In[5]:
from __future__ import division
import os
import pandas as pd
import numpy as np
from scipy import stats


# In[6]:

def kstest2samp(samp1, samp2):
    ksval, pval = stats.ks_2samp(samp1, samp2)
    return ksval, pval


# In[3]:

def load_trends_df(filename):
    df = pd.DataFrame()
    if os.path.isfile(filename):
        df = pd.read_csv(filename, header=0)
    return df


# In[2]:

def runs(lst):
    "Iterator, chunks repeated values"
    for j, two in enumerate(lst):
        if j == 0:
              one, i = two, 0
        if one != two:
            yield j - i,one
            i = j

        one = two

    yield j - i + 1, two


# In[1]:

# Very fast Cliff's Delta calculator. Courtesy of Tim Menzies
# https://gist.github.com/timm/a6e759eb7d9b5f05b468
def cliffs_delta(lst1,lst2,
                dull = [0.147, # small
                        0.33,  # medium
                        0.474 # large
                        ][0] ):
    "Returns true if there are more than 'dull' differences"
    m, n = len(lst1), len(lst2)
    lst2 = sorted(lst2)
    j = more = less = 0
    for repeats, x in runs(sorted(lst1)):
        while j <= (n - 1) and lst2[j] <  x:
              j += 1
        more += j*repeats
        while j <= (n - 1) and lst2[j] == x:
              j += 1
        less += (n - j)*repeats
    d = (more - less) / (m*n)
    return d, abs(d) > dull

