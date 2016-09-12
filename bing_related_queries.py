
# coding: utf-8

# In[53]:

"""TypeUsage python bing_related_queries -s seed_word -t threshold -f factor -o overlap_method
Where threshold and factor are fractions less than 1.00, overlap_method
should either be (s)tring or (n)gram"""
from nltk.corpus import stopwords
from collections import OrderedDict
from xml.dom.minidom import parseString
from random import choice
from keys import bing_keys
import argparse
import requests
import sys
import csv


# In[45]:

def get_apikey(k=None):
    while True:
        key = choice(bing_keys)
        if key != k:
            return key


# In[46]:

url = "https://ssl.bing.com/webmaster/api.svc/pox/GetRelatedKeywords"
params = {'startDate': '2015-09-01', 
          'endDate': '2016-09-01', 
          'language': 'en-US', 
          'country': 'us'}
stop = stopwords.words('english')


# In[47]:

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


# In[32]:

"""A method that cleans the list of obtained queries by removing stopwords
from every query and return the cleaned queries as a list"""
def clean_obtained_queries(queries):
    clean_related_queries = []
    for q in queries:
        words = nltk.word_tokenize(q)
        query = (" ".join([i for i in words if i not in stop])).strip(' .,\'')
        clean_related_queries.append(query)
    return clean_related_queries


# In[67]:

"""A method that calculates overlap between a list of related 
queries and the global set of already approved queries."""
def get_overlap(related_queries, method):
    if len(approved_ngrams)==0 or len(approved_queries) == 0:
        return 1
    if len(related_queries)==0:
        return 0
    count = 0.0
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


# In[68]:

def save_related_queries(seed, threshold, factor, method):
    a_name = './data/' + seed + '_' + threshold + '_' + factor + '_' + method + '_' + 'approved.csv'
    r_name = './data/' + seed + '_' + threshold + '_' + factor + '_' + method + '_' + 'rejected.csv'
        
    with open(a_name, 'w') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in approved_queries.iteritems():
            csv_writer.writerow([k, v])
            
    with open(r_name, 'w') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in rejected_queries.iteritems():
            csv_writer.writerow([k, v])    


# In[65]:

def main():
    ap = argparse.ArgumentParser(description='Argument parser for bing api get related search queries script')
    ap.add_argument('-s', '-seed', help='Seed word', required=True)
    ap.add_argument('-t', '-threshold', help='Overlapping threshold', default=0.25)
    ap.add_argument('-f', '-factor', help='Selection factor of approved related keywords', default=1.00)
    ap.add_argument('-o', '-overlap', help='Overlapping measurement method', default='n')
    args = ap.parse_args()
    
    # Default values
    seed_word = args.s
    threshold = args.t
    selection_factor = args.f
    overlap_method = args.o
    
    newset = [seed_word]
    while 0 < len(newset) and len(newset) < 40000:
        new_query = newset.pop(0)

        # Set the parameters for this search query
        params['q'] = new_query
        params['apikey'] = get_apikey()

        # If this query appears anywhere in the approved, rejected, or
        # junk queries, then don't process it.
        if  (new_query in approved_queries) or (new_query in rejected_queries) or (new_query in junk_queries):
            continue
        try:   
            # Fetch the response.
            session = requests.Session()
            response = session.get(url, params=params)

            # Check whether the response code is not 200 (ok).
            if response.status_code != 200:
                # Change to another random api key and try again.
                params['apikey'] = get_apikey(params['apikey'])
                print response.text
                continue

            try:
                doc = parseString(response.text)
            except Exception as e:
                print 'Error parsing response ' + str(e)
                continue

            response.close

            # Extract all the related queries for the new query.
            related_keywords = list()
            for element in doc.getElementsByTagName('Query'):
                related_keywords.append(element.firstChild.nodeValue)

            # Remove stopwords from the related keywords.
            related_keywords = clean_obtained_queries(related_keywords)

            # Get overlap value
            overlap_value = get_overlap(related_keywords, overlap_method)

            if overlap_value >= threshold:
                # Overlap value is beyond threshold. Save the new 
                # query's overlap value and add it to the approved
                # queries list.
                approved_queries[new_query] = overlap_value

                # The related keywords are now cadidates for further
                # related keyword fetching.
                subset_index = int(selection_factor * len(related_keywords))
                newset.extend(related_keywords[0:subset_index])

                # Add the new query to the approved ngrams.
                l = len(new_query.split())
                approved_ngrams[l] = approved_ngrams.get(l, []).append(new_query)
            else:
                # Reject the new query.
                rejected_queries[new_query] = overlap_value
                
                # If the overlap value is zero, then add them to junk queries.
                if overlap_value == 0:
                    junk_related_keywords |= set(related_keywords)

        except Exception as e:
            print 'Error processing request ' + str(e)
            continue
        finally:
            save_related_queries(seed_word, threshold, selection_factor, overlap_method)
            return


# In[60]:

if __name__ == '__main__':
    main()

