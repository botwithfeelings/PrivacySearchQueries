#
# This file contains the functions necessary to get the Google search pages, related queries, kernel values, and
# expansion sets from a specific query.
#
# Several functions in this page depend on hard-coded HTML class names to parse the Google search pages. If the
# structure of the search result page changes, these functions will break.
#
# The main purpose of this is to compute the web based kernel function between two given query strings. For detailed
# explanation of the method used here, see [A web-based kernel function for measuring the similarity of short text snippets]
# URL: http://dl.acm.org/citation.cfm?id=1135834
#
# The following is a simplified description of the algorithm used:
# The similarity kernel function between two short snippets of text or query string x and y are calculated as:
# K(x, y) = QE(x).QE(y)
# That the kernel is the inner product between the query expansions of x and y.
# The query expansion of x, denoted QE(x) is computed as follows:
#   1. Issue x as a query to a search engine S (in this case google).
#   2. Let R(x) be the set of (at most) n retrieved documents d1, d2, . . . , dn (we used n=100, 
#   compared to 200 in the original cited work)
#   3. Compute the TF-IDF term vector vi for each document di in R(x)
#   4. Compute C(x), the centroid of the L2 normalized vectors vi.
#   5. Let QE(x) be the L2 normalization of the centroid C(x).
#
# Compared to the original, we didn't perform any truncation of the TF-IDF vectors achieved in step 3 due to the short
# document size retrieved from google search results page.

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


def stem_tokens(tokens):
    """
    Stem the tokens passed in. All lexical representations are to be used in the stemmed representation by the Porter
    stemmer.

    :param tokens: Tokens to stem
    :return: All tokens passed in with stemming applied
    """
    #
    stemmer = PorterStemmer()
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def regex_tokenize(text):
    """
    Lowercase, tokenize, and stem text based on the nltk regex tokenizer. The difference between this and the next one is 
    that this one takes care of punctuation by itself before tokenize and stemming.

    :param text: The text to tokenize
    :return: A list of stemmed tokens from the input text
    """
    text = text.lower()
    tokenizer = nltk.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    stems = stem_tokens(tokens)
    return stems

def word_tokenize(text):
    """
    Lowercase, tokenize, and stem text based on the nltk word tokenizer

    :param text: The text to tokenize
    :return: A list of stemmed tokens from the input text
    """
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens)
    return stems


def to_ascii(s):
    """
    Convert unicode to ascii, (this process removes accents).

    :param s: The string to convert
    :return: The string in ascii
    """
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


def tfidf_normalize(row):
    """
    A function used to normalize the tf-idf matrix along an axis. This function is used to prepare for centroid
    calculation by:

    * Calculating the L2 norm for each row
    * Normalizing the row by the L2 norm

    :param row: The row to normalize
    :return: The normalized row
    """
    # Calculate L2 norm value.
    l2norm = np.linalg.norm(row, 2)

    # Normalize row by L2 norm.
    return row/l2norm


def get_query_expansion_vector(vec):
    """
    Get the query expansion vector for a tf-idf matrix

    :param vec: A tf-idf sparse matrix
    :return: The expansion vector for the matrix
    """
    # Calculate the vector.
    normalized = np.apply_along_axis(tfidf_normalize, axis=1, arr=vec)
    centroid = np.sum(normalized, axis=0)
    qe = centroid/np.linalg.norm(centroid, 2)
    return qe


def get_query_html(query, limit=None, num_results=100):
    """
    Retrieves html result for a query pushed into the Google search engine.

    :param query: The query to search Google for
    :param limit: THe limit for the number of Google queries to issue in an hour. This parameter should be specified
                  to reduce the risk of being hit by rate limiting.
    :param num_results: THe number of query results to retrieve
    :return: The Google search page for the provided query
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
    Retrives the term frequency inverse document frequency (tf-idf) matrix for a query and candidate.

    :param es_q: The expansion set for the reference query (i.e. the ultimate root query)
    :param es_c: The expansion set for the candidate query
    :return: The tf-idf matrices
    """
    lq = len(es_q)
    lc = len(es_c)

    # Combine the document sets for tf-idf calculation.
    combined = es_q
    combined.extend(es_c)

    # We want to get a new vectorizer for every string.
    tfidf = TfidfVectorizer(tokenizer=word_tokenize, stop_words='english')
    tfs = tfidf.fit_transform(combined)

    vectors = tfs.toarray()
    return vectors[0:lq-1, :], vectors[lq:lq+lc-1, :]


def kval_es(es_q, es_c):
    """
    Calculates the kernel function value from two expansion sets rather than raw short string candidates, makes
    caching easier.

    .. note:: This kernel function is an implementation of the methodology presented in 
    [A web-based kernel function for measuring the similarity of short text snippets]
    URL: http://dl.acm.org/citation.cfm?id=1135834

    :param es_q: The expansion set for the reference query (i.e. the ultimate root query)
    :param es_c: The expansion set for the candidate query
    :return: The kernel function value
    """
    vq, vc = get_tfidf_matrices(es_q, es_c)
    qe_q = get_query_expansion_vector(vq)
    qe_c = get_query_expansion_vector(vc)
    return np.inner(qe_q, qe_c)


def kval(q, c):
    """
    Find the kernel function value between a query string and candidate string

    .. note:: Do not use this when handling bulk queries as it is computationally expensive. This should only be used
              for testing and debugging. Use the extended set version instead when handling bulk.

    :param q: Query string to calculate the kernel value in reference to
    :param c: Candidate to calculate the k value for
    :return: Value of kernel function
    """
    q_page = get_query_html(q)
    c_page = get_query_html(c)
    es_q = get_google_query_summary_set(q_page)
    es_c = get_google_query_summary_set(c_page)
    return kval_es(es_q, es_c)


def get_google_related_searches(page):
    """
    Retrieves the related searches for a Google query string, given the html page of the google search page. The
    related searches are the queries found at the bottom of the first page of results titled "Searches related to this
    search."

    .. note:: This function depends on the classes assigned by Google in the search results. Any change in these
              will likely break the functionality of this function.

    :param page: Google serch result page to determine the related queries of
    :return: The related searches
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


def get_google_query_summary_set(query_results_page):
    """
    Retrieves the summary set for a query string given the html page of the google search page. The summary set
    consists of the result header and the summary text strip for each of the search results in the returned page.
    
    .. note:: This function depends on the classes assigned by Google in the search results. Any change in these
              will likely break the functionality of this function.

    :param query_results_page: Google search result to determine the summary set of
    :return: Summary set for the provided page
    """
    summary_set = list()
    if query_results_page is not None:
        # Strip the extended set using beautifulsoup.
        soup = BeautifulSoup(query_results_page, 'lxml')
        summary_divs = soup.findAll("div", {"class": "g"})
        for div in summary_divs:
            for d in div.findAll('div', {'class': 'rc'}):
                doc = ""
                for hr in d.findAll('h3', {'class': 'r'}):
                    doc += hr.getText()
                    doc += ' '
                for ds in d.findAll('div', {'class': 's'}):
                    for s in ds.findAll('span', {'class': 'st'}):
                        doc += s.getText()
                summary_set.append(to_ascii(doc).translate(None, string.punctuation))

    return summary_set


def test_kval(q, c):
    """
    Calculate and print the kernel function value between a query string and a candidate.

    :param q: Query string to calculate the k value in reference to
    :param c: Candidate to calculate the k value for
    :return: None
    """
    k = kval(q, c)
    print k
