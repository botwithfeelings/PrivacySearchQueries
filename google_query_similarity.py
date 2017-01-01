#
#
#

# standard library imports
from random import randint
import string
from time import sleep
import unicodedata
import urllib
import urllib2

# third party imports
from bs4 import BeautifulSoup
import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokenize(text):
    """
    Tokenizes and performs stemming on the tokens.

    :param text:
    :return:
    """
    # All lexical representations are to be used is the stemmed representation by the Porter stemmer
    stemmer = PorterStemmer()

    text = text.lower()
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems


def to_ascii(s):
    """
    Convert unicode to ascii, removes accents.

    :param s:
    :return:
    """
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


def tfidf_normalize(row):
    """
    Prepares for centroid calculation:
        - Calculate L2 norm for each row
        - Normalize the row by L2 norm

    :param row:
    :return:
    """
    # Calculate L2 norm value.
    l2norm = np.linalg.norm(row, 2)

    # Normalize row by L2 norm.
    return row/l2norm


def get_query_expansion_vector(vec):
    """
    Takes in the sparse matrix

    :param vec:
    :return:
    """
    # Calculate the vector.
    normalized = np.apply_along_axis(tfidf_normalize, axis=1, arr=vec)
    centroid = np.sum(normalized, axis=0)
    qe = centroid/np.linalg.norm(centroid, 2)
    return qe


def get_query_html(query, limit=None, num_results=100):
    """
    Retrieves html result for a query pushed into the Google search engine.

    :param query:
    :param limit:
    :param num_results:
    :return:
    """
    address = 'http://www.google.com/search?q={}&num={}&hl=en&start=0'.format(urllib.quote_plus(query), num_results)
    request = urllib2.Request(address,
                              None,
                              {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 '
                                             '(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
    urlfile = urllib2.urlopen(request)
    page = urlfile.read()

    # Determine the amount of time needed to sleep
    # before we yield control.
    if limit is not None:
        sleep_time = 3600/limit
        sleep(randint(sleep_time, sleep_time+5))
    return page


def get_tfidf_matrices(es_q, es_c):
    """
    Retrives the tf-idf matrix for a query and candidate.

    :param es_q:
    :param es_c:
    :return:
    """
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


def kval_es(es_q, es_c):
    """
    Calculates the kernel function value from two expansion sets rather
    than raw short string candidates, makes caching easier.

    :param es_q:
    :param es_c:
    :return:
    """
    vq, vc = get_tfidf_matrices(es_q, es_c)
    qe_q = get_query_expansion_vector(vq)
    qe_c = get_query_expansion_vector(vc)
    return np.inner(qe_q, qe_c)


def kval(q, c):
    """
    Finds the value of the kernel function between
    query string q and candidate c, better not use this,
    cause this is costly. Use the extended set version when
    handling bulk. Use this for checking or debugging.

    :param q:
    :param c:
    :return:
    """
    q_page = get_query_html(q)
    c_page = get_query_html(c)
    es_q = google_expanded_docs(q_page)
    es_c = google_expanded_docs(c_page)
    return kval_es(es_q, es_c)


def google_related_searches(page):
    """
    Retrieves the related searches for a Google query string,
    given the html page of the google search page."

    :param page:
    :return:
    """
    rs = list()
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        # Strip the related search portion using beautifulsoup.
        rsdiv = soup.find("div", {"id": "brs"})
        for d in rsdiv.findAll('div', {'class': 'brs_col'}):
            for p in d.findAll('p', {'class': '_e4b'}):
                rs.append(to_ascii(p.getText()).translate(None, string.punctuation))

    return rs


def google_expanded_docs(page):
    """
    Retrieves the first 100 expanded sets for a query string,
    given the html page of the google search page.Expanded set
    consists of the result header and the summary text
    strip for each of the search results in the returned page.

    :param page:
    :return:
    """
    es = list()
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        # Strip the extended set using beautifulsoup.
        esdivs = soup.findAll("div", {"class": "g"})
        for esdiv in esdivs:
            for d in esdiv.findAll('div', {'class': 'rc'}):
                doc = ""
                for hr in d.findAll('h3', {'class': 'r'}):
                    doc += hr.getText()
                    doc += ' '
                for ds in d.findAll('div', {'class': 's'}):
                    for s in ds.findAll('span', {'class': 'st'}):
                        doc += s.getText()
                es.append(to_ascii(doc).translate(None, string.punctuation))

    return es


def test_kval(q, c):
    k = kval(q, c)
    print k
