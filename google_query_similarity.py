
# coding: utf-8

# In[2]:

from nltk.corpus import stopwords
from nltk import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from collections import OrderedDict
import numpy as np
import argparse
import csv
import urllib
import urllib2
import unicodedata
import string
import nltk
import sys


# In[3]:

"""All lexical representations are to be used is the stemmed representation by the Porter stemmer"""
stemmer = PorterStemmer()

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


# In[4]:

"""Tokenizes and performs stemming on the tokens."""
def tokenize(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems


# In[5]:

"""Convert unicode to ascii, removes accents."""
def to_ascii(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


# In[6]:

"""Prepares for centroid calculation:
- Calculate L2 norm for each row
- Normalize the row by L2 norm"""
def tfidf_normalize(row):
    # Calculate L2 norm value.
    l2norm = np.linalg.norm(row, 2)

    # Normalize row by L2 norm.
    return row/l2norm


# In[7]:

"""Takes in the sparse matrix"""
def get_query_expansion_vector(vec):
    # Calculate the vector.
    normalized = np.apply_along_axis(tfidf_normalize, axis=1, arr=vec)
    centroid = np.sum(normalized, axis=0)
    qe = centroid/np.linalg.norm(centroid, 2)
    return qe


# In[8]:

"""Retrieves html result for a query pushed into the Google search engine."""
def get_query_html(query, limit, num_results=100):
    address = 'http://www.google.com/search?q={}&num={}&hl=en&start=0'.format(urllib.quote_plus(query), num_results)
    request = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
    urlfile = urllib2.urlopen(request)
    page = urlfile.read()

    # Determine the amount of time needed to sleep
    # before we yield control.
    sleep_time = 3600/limit
    sleep(randint(sleep_time, sleep_time+5))
    return page


# In[9]:

"""Retrives the tf-idf matrix for a query and candidate."""
def get_tfidf_matrices(es_q, es_c):
    lq = len(es_q)
    lc = len(es_c)

    # Combine the document sets for tf-idf calculation.
    combined = es_q
    combined.extend(es_c)

    # We want to get a new vectorizer for every string.
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
    tfs = tfidf.fit_transform(combined)

    vectors = tfs.toarray()
    return vectors[0:lq-1, :], vectors[lq:lq+lc-1, :]


# In[10]:

"""Calculates the kernel function value from two expansion sets rather
than raw short string candidates, makes caching easier."""
def kval_es(es_q, es_c):
    vq, vc = get_tfidf_matrices(es_q, es_c)
    qe_q = get_query_expansion_vector(vq)
    qe_c = get_query_expansion_vector(vc)
    return np.inner(qe_q, qe_c)


# In[13]:

"""Finds the value of the kernel function between
query string q and candidate c, betther not use this,
cause this is costly. Use the extended set version when
handling bulk. Use this for checking or debugging."""
def kval(q, c):
    q_page = get_query_html(q)
    c_page = get_query_html(c)
    es_q = google_expanded_docs(q_page)
    es_c = google_expanded_docs(c_page)
    return kval_es(es_q, es_c)


# In[12]:

"""Retrieves the related searches for a Google query string,
given the html page of the google search page."""
def google_related_searches(page):
    rs = list()
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        # Strip the related search portion using beautifulsoup.
        rsdiv = soup.find("div", { "id" : "brs" })
        for d in rsdiv.findAll('div', {'class':'brs_col'}):
            for p in d.findAll('p', {'class':'_e4b'}):
                rs.append(to_ascii(p.getText()).translate(None, string.punctuation))

    return rs

"""Retrieves the first 100 expanded sets for a query string,
given the html page of the google search page.Expanded set
consists of the result header and the summary text
strip for each of the search results in the returned page."""
def google_expanded_docs(page):
    es = list()
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        # Strip the extended set using beautifulsoup.
        esdivs = soup.findAll("div", { "class" : "g" })
        for esdiv in esdivs:
            for d in esdiv.findAll('div', {'class':'rc'}):
                doc = ""
                for hr in d.findAll('h3', {'class':'r'}):
                    doc += hr.getText()
                    doc += ' '
                for ds in d.findAll('div', {'class':'s'}):
                    for s in ds.findAll('span', {'class' : 'st'}):
                        doc += s.getText()
                es.append(to_ascii(doc).translate(None, string.punctuation))

    return es


# In[14]:

def test_kval(q, c):
    k = kval(q, c)
    print k
