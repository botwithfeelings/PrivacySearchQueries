
# coding: utf-8

# In[17]:

from nltk.corpus import stopwords
from nltk import word_tokenize
from collections import OrderedDict
from random import shuffle
from bs4 import BeautifulSoup
from time import sleep
import argparse
import csv
import urllib
import urllib2


# In[ ]:

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# In[15]:

"""A method that cleans the list of obtained queries by removing stopwords
from every query and return the cleaned queries as a list"""
def clean_obtained_queries(queries, stop):
    clean_queries = []
    for q in queries:
        words = word_tokenize(q)
        query = (" ".join([i for i in words if i not in stop])).strip(' .,\'')
        clean_queries.append(query)
    return clean_queries


# In[13]:

"""A method that calculates overlap between a list of related 
queries and the global set of already approved queries."""
def get_overlap(approved_queries, approved_ngrams, related_queries, method):
    if method == 'n' and len(approved_ngrams) == 0:
        return 1    
    if method == 's' or len(approved_queries) == 0:
        return 1    
    if len(related_queries) == 0:
        return 0
    count = 0.0
    print approved_ngrams
    print related_queries
    for item in related_queries:
        if method == 'n':
            item_set = set(item.split())
            if len(item_set) in approved_ngrams:
                len_list = approved_ngrams[len(item_set)]
                if len_list is not None:
                    for ngram in len_list:
                        inter = item_set & set(ngram.split())
                        if len(inter) == len(item_set):
                            count += 1
                            break
        elif method == 's':
            if item in approved_queries.keys():
                count += 1
            
    control_size = min(len(approved_queries), len(related_queries))
    return count/control_size


# In[14]:

def save_related_queries(seed, threshold, factor, method, approved, rejected):
    name_suffix = './googledata/' + seed.replace(' ', '_') + '_' + str(threshold) + '_' + str(factor) + '_' + method + '_'
    a_name =  name_suffix + 'approved.csv'
    r_name = name_suffix + 'rejected.csv'
        
    with open(a_name, 'w') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in approved.iteritems():
            csv_writer.writerow([k, v])
            
    with open(r_name, 'w') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in rejected.iteritems():
            csv_writer.writerow([k, v])    


# In[18]:

def google_related_searches(query):
    try:
        address = "http://www.google.com/search?q=%s&num=100&hl=en&start=0" % (urllib.quote_plus(query))
        request = urllib2.Request(address, None, {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
        urlfile = urllib2.urlopen(request)
        page = urlfile.read()
    except Exception as e:
        print 'Error retrieving google search results: ' + str(e)
        return False, list()
    
    # Strip the related search portion using beautifulsoup.
    rs = list()
    soup = BeautifulSoup(page, 'lxml')
    rsdiv = soup.find("div", { "id" : "brs" })
    for d in rsdiv.findAll('div', {'class':'brs_col'}):
        for p in d.findAll('p', {'class':'_e4b'}):
            rs.append(p.getText())
    return True, rs


# In[ ]:

def main():
    # Structure to hold search queries by the length of their ngram. This is
    # find a faster lookup for determining overlap values quickly.
    approved_ngrams = dict()

    #A dictionary of approved queries along with their overlap value
    approved_queries = OrderedDict() 
    rejected_queries = OrderedDict()

    # A set maintained for related queries where the overlap value was zero.
    # This can happen when either none of the related keywords appear in the
    # approved ngrams or we could not find any related keywords for the
    # given seed query.
    junk_related_keywords = set()
    
    stop = stopwords.words('english')
    
    ap = argparse.ArgumentParser(description='Find related searches using the google search scraping.')
    ap.add_argument('-s', '-seed', help='Seed word', required=True)
    ap.add_argument('-t', '-threshold', help='Overlapping threshold', default=0.25)
    ap.add_argument('-f', '-factor', help='Selection factor of approved related keywords', default=1.00)
    ap.add_argument('-o', '-overlap', help='Overlapping measurement method (n)gram or (s)tring', default='n')
    args = ap.parse_args()
    
    # Default values
    seed_word = args.s
    threshold = float(args.t)
    selection_factor = float(args.f)
    overlap_method = args.o
    
    try:
        newset = [seed_word]
        while 0 < len(newset) and len(newset) < 40000:
            new_query = newset.pop(0)

            # If this query appears anywhere in the approved, rejected, or
            # junk queries, then don't process it.
            if  (new_query in approved_queries) or (new_query in rejected_queries) or (new_query in junk_related_keywords):
                continue

            # Fetch the related searches.
            success, related_keywords = google_related_searches(new_query)            
            
            # Check if we failed to retrieve the related searches.
            if not success:
                # Put back the query in the candidate set and try again.
                newset.insert(0, new_query)
                continue

            # Remove stopwords from the related keywords.
            related_keywords = clean_obtained_queries(related_keywords, stop)

            # Get overlap value
            overlap_value = get_overlap(approved_queries, approved_ngrams, related_keywords, overlap_method)

            if overlap_value >= threshold:
                # Overlap value is beyond threshold. Save the new 
                # query's overlap value and add it to the approved
                # queries list.
                approved_queries[new_query] = overlap_value

                # The related keywords are now cadidates for further
                # related keyword fetching.
                subset_index = int(selection_factor * len(related_keywords))
                shuffle(related_keywords)
                newset.extend(related_keywords[0:subset_index])

                # Add the new query to the approved ngrams.
                l = len(new_query.split())
                approved_ngrams.setdefault(l, list()).append(new_query)
            else:
                # Reject the new query.
                rejected_queries[new_query] = overlap_value

                # If the overlap value is zero, then add them to junk queries.
                if overlap_value == 0:
                    junk_related_keywords |= set(related_keywords)
    except Exception as e:
        print 'Error processing related search ' + str(e)
    finally:
        save_related_queries(seed_word, threshold, selection_factor, overlap_method, approved_queries, rejected_queries)


# In[ ]:

if __name__ == '__main__':
    main()

