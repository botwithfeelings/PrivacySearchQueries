
# coding: utf-8

# In[1]:

from __future__ import division
import ssl
import nltk
import re
import urllib2
import string
from math import log
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from google_query_similarity import get_query_html, to_ascii, tokenize


# In[2]:

stop_words = stopwords.words('english') + list(string.punctuation)


# In[3]:

def sw_filter(word):
    return word not in stop_words


# In[4]:

def clean_tokenize(text):
    return filter(sw_filter, tokenize(text))


# In[5]:

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


# In[6]:

def get_visible_text(url):
    request = urllib2.Request(url,
                              None,
                              {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 '
                                             '(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
    opt_out_context = ssl._create_unverified_context()

    visible_texts = list()
    try:
        urlfile = urllib2.urlopen(request, context=opt_out_context)
        page = urlfile.read()
        soup = BeautifulSoup(page, 'html.parser')
        texts = soup.findAll(text=True)
    except Exception as e:
        return None

    visible_texts = filter(visible, texts)
    return ' '.join(visible_texts)


# In[7]:

def get_search_urls(page):
    urls = list()
    if page is not None:
        # Strip the extended set using beautifulsoup.
        soup = BeautifulSoup(page, 'lxml')
        summary_divs = soup.findAll("div", {"class": "g"})
        for div in summary_divs:
            for d in div.findAll('div', {'class': 'rc'}):
                for hr in d.findAll('h3', {'class': 'r'}):
                    link = hr.find('a').get('href')
                    urls.append(link)
    return urls


# In[8]:

def get_document_set(urls, debug):
    docs = list()
    if debug:
        print "No. of urls " + str(len(urls))

    for url in urls:
        text = get_visible_text(url)
        if text is not None:
            docs.append(text)
            if debug:
                print "Fetched url: " + url

    return docs


# In[9]:

def get_q_docs(query, docs):
    q_tokens = clean_tokenize(query)

    docs_r = list()
    for d in docs:
        d_tokens = clean_tokenize(d)
        if not set(q_tokens).isdisjoint(d_tokens):
            docs_r.append(d)
    return docs_r


# In[10]:

def get_w_likelihood_query(word, query_tokens, fd_query_docs, fd_coll):
    # Relative frequency of word in the collection as a whole.
    prob_w_coll = fd_coll.freq(word)

    # The probabilistic likelishood of the word given the query
    # is calculated over the set of documents containing at least
    # one query term.
    prob_w_query = 0
    prob_doc = 1/len(fd_coll)
    for fd_doc in fd_query_docs:
        # Calculate likelihood of word for current document.
        lamda = 0.6 # From the authors.
        prob_w_doc = (lamda * fd_doc.freq(word)) + ((1-lamda) * prob_w_coll)

        # Calculate the likelihood of the query given the document.
        prob_query_doc = 1.0
        for q in query_tokens:
            prob_q_coll = fd_coll.freq(q)
            prob_q_doc = (lamda * fd_doc.freq(q)) + ((1-lamda) * prob_q_coll)
            prob_query_doc *= prob_q_doc

        # Calculate the likelihood of the document given the query
        # through Bayesian inversion.
        prob_doc_query = prob_query_doc * prob_doc
        prob_w_query += (prob_w_doc * prob_doc_query)

    return prob_w_query


# In[21]:

def get_clarity_score(query, docs, debug):
    # Form the collection from the docs and get the overall frequency distribution
    coll = ' '.join(docs)
    coll_tokens = clean_tokenize(coll)
    fd_coll = nltk.FreqDist(coll_tokens)
    vocab = fd_coll.keys()

    if debug:
        print "Vocab size: " + str(len(vocab))

    # Get the documents with at least one query term and compute
    # the frequency distributions for each of these.
    docs_r = get_q_docs(query, docs)

    if debug:
        print "Docs with query term(s): " + str(len(docs_r))

    fd_query_docs = list()
    for doc in docs_r:
        doc_tokens = clean_tokenize(doc)
        fd_query_docs.append(nltk.FreqDist(doc_tokens))

    # Get the tokens in the query.
    query_tokens = clean_tokenize(query)

    score = 0.0
    for word in vocab:
        prob_w_coll = fd_coll.freq(word)
        prob_w_query = get_w_likelihood_query(word, query_tokens, fd_query_docs, fd_coll)

        score += (prob_w_query * log((prob_w_query/prob_w_coll), 2))

        if debug:
            print word, prob_w_query, prob_w_coll, score

    return score


# In[16]:

def do_stuff(query, count, debug):
    page = get_query_html(query, num_results=count)
    urls = get_search_urls(page)
    docs = get_document_set(urls, debug)
    return get_clarity_score(query, docs, debug)


# In[13]:

def main():
    ap = ArgumentParser(description='Compute the clarity score of a given short text and the no. of documents.')
    ap.add_argument('-q', '-query', help='Query text', required=True)
    ap.add_argument('-c', '-doc', help='No. of fetched documents to use', default=100)
    ap.add_argument('-d', '-debug', help='Print traces', action='store_true')

    args = ap.parse_args()

    query = args.q
    count = int(args.c)
    debug = bool(args.d)

    score = do_stuff(query, count, debug)

    print query.ljust(45), score
    return


# In[ ]:

if __name__ == '__main__':
    main()
