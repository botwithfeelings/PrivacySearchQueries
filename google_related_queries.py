
# coding: utf-8

# In[25]:

import google_query_similarity as gr
from collections import OrderedDict
import argparse
import csv
import os
import pickle


# In[26]:

class ScrapeState():
    def __init__(self, seed):
        self.seed = seed
        self.iteration = 0
        self.candidates = list()
        self.next_candidates = list()
        self.threshold = 1.0        

    def pickle(self):
        name_suffix = './googledata/' + self.seed.replace(' ', '_') 
        with open(name_suffix, 'wb') as f:
            pickle.dump(self.__dict__, f, pickle.HIGHEST_PROTOCOL)        

    def unpickle(self):
        name_suffix = './googledata/' + self.seed.replace(' ', '_') 
        if os.path.isfile(name_suffix):
            with open(name_suffix, 'rb') as f:
                tmp = pickle.load(f)
                self.__dict__.update(tmp)
    
    def display(self):
        attrs = vars(self)
        print '\n'.join("%s: %s" % item for item in attrs.items())


# In[16]:

def load_dictionaries(seed):
    # Dictionaries of approved and rejected queries
    # along with their kernel value.
    approved = OrderedDict()
    rejected = OrderedDict()
    
    name_suffix = './googledata/' + seed.replace(' ', '_') + '_' 
    a_name =  name_suffix + 'approved.csv'
    r_name = name_suffix + 'rejected.csv'
    
    if os.path.isfile(a_name):
        with open(a_name, mode='r') as f:
            reader = csv.reader(f)
            approved = {rows[0]:rows[1] for rows in reader}

    if os.path.isfile(r_name):
        with open(r_name, mode='r') as f:
            reader = csv.reader(f)
            rejected = {rows[0]:rows[1] for rows in reader}
    
    return approved, rejected


# In[17]:

def save_related_queries(seed, approved, rejected):
    name_suffix = './googledata/' + seed.replace(' ', '_') + '_' 
    a_name =  name_suffix + 'approved.csv'
    r_name = name_suffix + 'rejected.csv'
        
    with open(a_name, 'a') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in approved.iteritems():
            csv_writer.writerow([k, v])
            
    with open(r_name, 'a') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        for (k, v) in rejected.iteritems():
            csv_writer.writerow([k, v])    


# In[23]:

def do_stuff(seed, limit, keycnt):
    # Load the approved and rejected set 
    # from the previous attempt if any.
    approved, rejected = load_dictionaries(seed)
    
    # Everything we need to run is in this state object.
    # We load it from the last attempt if any.
    state = ScrapeState(seed)
    state.unpickle()
    state.display()
    
    try:
        # Expansion set and first iteration of  for the seed.
        seed_page = gr.get_query_html(seed, keycnt)
        seed_rs = gr.google_related_searches(seed_page)
        seed_es = gr.google_expanded_docs(seed_page)    

        # Initiate the candidates with the seed's related queries.
        state.candidates.extend(seed_rs)
        while state.iteration < limit:
            while len(state.candidates) > 0:
                candidate = state.candidates.pop(0)
                # If the candidate appears in either the accepted
                # or rejected sets then don't process it.
                if (candidate in approved) or (candidate in rejected):
                    continue

                # Get the candidate's related searches and extended set.
                can_page = gr.get_query_html(candidate, keycnt)
                can_rs = gr.google_related_searches(can_page)
                can_es = gr.google_expanded_docs(can_page)

                # Retrieve the kernel value.
                kval = gr.kval_es(seed_es, can_es)

                # If this is the first iteration accept all.
                # Otherwise if the kernel value is less than
                # the threshold then reject it.
                if state.iteration == 0:
                    # For the first iteration accept everything.
                    approved[candidate] = kval

                    # Set the threshold to the minimum of the first iteration.
                    if kval < state.threshold:
                        state.threshold = kval                
                else:
                    # For further iteration, only accept if kernel 
                    # value is greater than the threshold.
                    if kval >= state.threshold:
                        approved[candidate] = kval 
                    else:
                        rejected[candidate] = kval                

                # Add the candidate's related searches to the next_candidates.
                state.next_candidates.extend(can_rs)

            # Add the next candidates to the candidates set
            # and increase the iteration count.
            state.candidates.extend(next_candidates)
            state.next_candidates = list()
            state.iteration += 1
    except Exception as e:
        print 'Error retrieving google search results: ' + str(e)
        print 'Google throttling, wait a couple of minutes and try again.'
    finally:
        save_related_queries(seed, approved, rejected)
        state.pickle()
        
    return


# In[27]:

def main():
    ap = argparse.ArgumentParser(description='Use the script to pull google related search queries.')
    ap.add_argument('-s', '-seed', help='Seed word', required=True)
    ap.add_argument('-i', '-iteration', help='limit to number of related search iteration', default=3)
    ap.add_argument('-k', '-keywordlimit', help='limit to number of keyword request per hour', default=30)
    
    args = ap.parse_args()
    
    seed = args.s
    limit = int(args.i)
    keycnt = int(args.k)
    
    do_stuff(seed, limit, keycnt)
    return


# In[ ]:

if __name__ == '__main__':
    main()

