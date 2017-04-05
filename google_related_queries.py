#!/usr/bin/env python2.7
#
# This script can be used to pull related search queries from a Google search from an initial seed query. It recursively
# passes search queries to a Google search page, pulling out the Google-defined related queries from the resulting page.
# For each of these candidate queries, it compares the summary snippets associated with the search first 100 search
# results with the snippets in the seed query by use of a kernel function (for more information, see the documentation
# in google_query_similarity.py) and a decision is made whether to accept this candidate query as related or reject it
# based on an outlier threshold defined by the first iteration. This recursion wil continue until the iteration count
# specified in the command line arguments has been reached.
#
#
# You will need to provide the following arguments to the argument parser for this script:
#
# * seed
# * iteration count (generally set to 3)
# * request limit (see bullet 2 in next list)
#
# In running this script, we have identified the following issues that you need to be aware of and potentially
# address:
#
# * This script relies on a specific structure of Google's search results. The logic provided
#   by the script can break at any time if Google changes how the results and/or related queries are displayed.
# * When running this script, we have been hit with Google's rate limiters, rejecting all of our requests.
#   In order to bypass this issue, we have implemented a feature to only submit a specific number of requests
#   in a time period. While you might be able to use a higher rate, we were generally running at 100 requests/hour.
#

# standard library imports
from __future__ import division
import argparse
from collections import OrderedDict
import csv
import os
import pickle
import traceback

# third party imports
import numpy as np

# local imports
import google_query_similarity as gr

INDEX_RECALL_DIR = "./indexrecall/"


class ScrapeState:
    def __init__(self, seed):
        """
        Create a scrape state for a given query seed.

        :param seed: The root query that this state was generated for. The seed should only contain alphanumeric
                     characters and spaces/underscores as the seed is used to generate the backup file.
        """
        self.seed = seed
        self.iteration = 0
        self.candidates = list()
        self.next_candidates = list()
        self.threshold = 1.0

    def pickle(self):
        """
        Save the object to a data file so we can resume where we left off

        :return: None
        """
        name_suffix = './googledata/' + self.seed.replace(' ', '_')
        with open(name_suffix, 'wb') as f:
            pickle.dump(self.__dict__, f, pickle.HIGHEST_PROTOCOL)

    def unpickle(self):
        """
        Load the object from a cached data file to resume where left off.

        :return: None
        """
        name_suffix = './googledata/' + self.seed.replace(' ', '_')
        if os.path.isfile(name_suffix):
            with open(name_suffix, 'rb') as f:
                tmp = pickle.load(f)
                self.__dict__.update(tmp)

    def display(self):
        """
        Print the current state of the object. This can be used to check the progress after unpickling

        :return: None
        """
        attrs = vars(self)
        print '\n'.join("%s: %s" % item for item in attrs.items())


def load_related_queries(seed):
    """
    Load the state of the approved and rejected dictionaries from the saved related query files, if they exist. If no
    files exist, an empty ordered dictionary will be returned. If the file does exist, the ordered dictionary will
    contain the appropriate data.

    The key for the ordered dictionary is the candidate query. The value for the ordered dictionary is the parent query
    and kernel value as a tuple. OrderedDict([query:(parent query, kernel value)])

    :param seed: The root query that this state was generated for. The seed should only contain alphanumeric
                 characters and spaces/underscores as the seed is used to generate the backup file.

    :return: The approved and rejected ordered dictionaries in a tuple (approved, rejected)
    """
    approved = OrderedDict()
    rejected = OrderedDict()

    name_suffix = './googledata/' + seed.replace(' ', '_') + '_'
    a_name = name_suffix + 'approved.csv'
    r_name = name_suffix + 'rejected.csv'

    if os.path.isfile(a_name):
        with open(a_name, mode='r') as f:
            reader = csv.reader(f)
            approved = OrderedDict((rows[0], (rows[1], rows[2])) for rows in reader)

    if os.path.isfile(r_name):
        with open(r_name, mode='r') as f:
            reader = csv.reader(f)
            rejected = OrderedDict((rows[0], (rows[1], rows[2])) for rows in reader)

    return approved, rejected


def save_related_queries(seed, approved, rejected):
    """
    Save the approved and rejected related queries to a file.

    In this implementation, the collections to be stored are ordered dictionaries. While the collection does not need
    to be an ordered dictionary, it must be parsable with the structure (k, (v0, v1)) where k is the related query,
    v0 is the parent query, and v1 is the kernel value for the related query

    :param seed: The root query that the approved/rejected queries were generated for. The seed should only contain
                 alphanumeric characters and spaces/underscores as the seed is used to generate the backup file.
    :param approved: Collection of approved queries following structure described above
    :param rejected: Collection of rejected queries following structure described above
    :return: None
    """
    name_suffix = './googledata/' + seed.replace(' ', '_') + '_'
    a_name = name_suffix + 'approved.csv'
    r_name = name_suffix + 'rejected.csv'

    if any(approved):
        with open(a_name, 'w') as f:
            csv_writer = csv.writer(f, lineterminator='\n')
            for (k, v) in approved.iteritems():
                csv_writer.writerow([k, v[0], v[1]])

    if any(rejected):
        with open(r_name, 'w') as f:
            csv_writer = csv.writer(f, lineterminator='\n')
            for (k, v) in rejected.iteritems():
                csv_writer.writerow([k, v[0], v[1]])


def run_google_related_queries(seed, limit, keycnt):
    """
    This function is where the main logic of getting the related google queries occurs. Execution continues until either
    the maximum number of iterations occur or there is an error in the execution.

    The iterations have the following logic:
        Iteration 0:
            1) Get the first set of related search queries and page summary set from the Google search page of the seed
               query (a summary set is the result header and the summary text strip for each of the results in a Google
               search results page)
            2) Add this initial set of related searched to the candidate set for the initial iteration
            3) The related searches and summary set for each of the candidate queries are acquired
            4) The related queries for every candidate seed in this iteration is added to the candidate seeds for the
               next iteration.
            5) Calculate the kernel function value between each of these candidate queries and the seed query
            6) Determine the threshold kernel function value, set to be Q25-1.5*IQR based on the values calculated in
               this initial iteration. This method of determining outliers is common practice within statistics.
            7) Based on the kernel function value for each of the candidate queries, add them into the accepted list
               iff the kernel function has a value greater than or equal to the threshold.

        Iteration 1+:
            steps 3, 4, 5, and 7 are repeated for all other iterations (1+).

    :param str seed: The root query that the related queries are generated for. The seed should only contain
                     alphanumeric characters and spaces/underscores as the seed is used to generate the backup file.
    :param int limit: Specifies the maximum number of times to iterate through the related queries
    :param int keycnt: The maximum number of Google keyword requests per hour
    :return: None
    """
    # Recover from any previous failures/runs, if any, by loading the queries and unpickling the scrape state
    approved, rejected = load_related_queries(seed)
    state = ScrapeState(seed)
    state.unpickle()
    state.display()

    # Create space for iteration 0 if necessary.
    if state.iteration==0:
        iter0 = OrderedDict()
        iter0kvals = list()

    try:
        # Expansion set and first iteration of  for the seed.
        seed_page = gr.get_query_html(seed, keycnt)
        seed_rs = gr.get_google_related_searches(seed_page)
        seed_es = gr.get_google_query_summary_set(seed_page)

        # Add seed to the accepted set.
        approved[seed] = (seed, 1.0)

        # Initiate the candidates with the seed's related queries as (related search, parent) tuple.
        # The parent in this case is the seed.
        for rs in seed_rs:
            state.candidates.append((rs, seed))
        while state.iteration < limit:
            while len(state.candidates) > 0:
                (candidate, parent) = state.candidates.pop(0)
                # If the candidate appears in either the accepted
                # or rejected sets then don't process it.
                if (candidate in approved) or (candidate in rejected):
                    continue

                # Get the candidate's related searches and extended set.
                can_page = gr.get_query_html(candidate, keycnt)

                try:
                    can_rs = gr.get_google_related_searches(can_page)
                    can_es = gr.get_google_query_summary_set(can_page)

                    # Retrieve the kernel value.
                    kval = gr.kval_es(seed_es, can_es)
                except Exception as e:
                    print 'Error processing google search results: ' + repr(e)
                    print 'Candidate query: ' + candidate
                    continue

                # If this is the first iteration accept all.
                # Otherwise if the kernel value is less than
                # the threshold then reject it.
                if state.iteration == 0:
                    # For the first iteration store everything inside iter0.
                    # We will figure out everything at the end of the iteration.
                    iter0[candidate] = (parent, kval)
                    iter0kvals.append(kval)
                else:
                    # For further iteration, only accept if kernel
                    # value is greater than the threshold.
                    if kval >= state.threshold:
                        approved[candidate] = (parent, kval)
                    else:
                        rejected[candidate] = (parent, kval)

                # Add the candidate's related searches to the next_candidates.
                for rs in can_rs:
                    state.next_candidates.append((rs, candidate))

            # Add the next candidates to the candidates set
            # and increase the iteration count.
            state.candidates.extend(state.next_candidates)
            state.next_candidates = list()

            # Before incrementing the iteration counter, process
            # the first iteration if this is the first iteration.
            if state.iteration == 0:
                q75, q25 = np.percentile(iter0kvals, [75, 25])
                iqr = q75 - q25
                state.threshold = q25 - (1.5 * iqr)

                # Process the iteration 0 candidates and later ones
                # based on this threshold.
                for (k, v) in iter0.iteritems():
                    if v[1] >= state.threshold:
                        approved[k] = v
                    else:
                        rejected[k] = v

            state.iteration += 1
    except Exception as e:
        # We do not want to die unexpectedly without saving the current progress, so catch all errors.
        print 'Error retrieving google search results: ' + repr(e)
        traceback.print_exc()
    finally:
        # Regardless of whether we have failed (i.e. caught an exception) or not, save the approved and rejected queries
        # and the state of the calculation.
        save_related_queries(seed, approved, rejected)
        state.pickle()


def comp_survey_index_similarity(seed, indfile, keycnt):
    """
    Computes and calculates the success rate of a given index, if the threshold is priorly calculated.
    :param seed:
    :param indfile:
    :param keycnt:
    :return:
    """

    # If there is no such file for the given index just return
    if not os.path.isfile(indfile):
        return

    # Create the recall directory if needed.
    if not os.path.exists(INDEX_RECALL_DIR):
        os.makedirs(INDEX_RECALL_DIR)

    # Load the pickled state for the seed to find the threshold
    state = ScrapeState(seed)
    state.unpickle()
    t = state.threshold

    # Retrieve the list of keywords to be fetched into a list.
    ind_list = list()
    with open(indfile, 'rU') as f:
        # If the trends file is from AMT then treat it as a text file due to
        # MAC csv formatting issues.
        ind_list = list(map(str.strip, f.readlines()))

    # Expansion set of for the seed.
    seed_page = gr.get_query_html(seed, keycnt)
    seed_es = gr.get_google_query_summary_set(seed_page)

    # Start computing the k-values for each of the query in the index.
    approved_cnt = 0
    approved = OrderedDict()
    rejected = OrderedDict()
    for q in ind_list:

        # Get the query's related searches and extended set.
        ind_page = gr.get_query_html(q, keycnt)

        kval = 0.0
        try:
            ind_es = gr.get_google_query_summary_set(ind_page)

            # Retrieve the kernel value.
            kval = gr.kval_es(seed_es, ind_es)
        except Exception as e:
            # Could not compute index, set to value so that it is rejected.
            kval = -1.0

        # Check if this is above the threshold.
        if kval >= t:
            approved[q] = kval
            approved_cnt += 1
        else:
            rejected[q] = kval

    # Write out the kvals, and the success rate.
    success_rate = (approved_cnt/len(ind_list)) * 100
    print seed, success_rate, t

    def write_dict(fname, d):
        if any(d):
            with open(fname, 'w') as f:
                csv_writer = csv.writer(f, lineterminator='\n')
                for (k, v) in d.iteritems():
                    csv_writer.writerow([k, v])
        return

    # Write out the decision sets.
    fn_prefix = INDEX_RECALL_DIR + seed.replace(' ', '_')
    a_name = fn_prefix + '_approved.csv'
    r_name = fn_prefix + '_rejected.csv'
    write_dict(a_name, approved)
    write_dict(r_name, rejected)
    return


def main():
    ap = argparse.ArgumentParser(description='Use the script to pull google related search queries.')
    ap.add_argument('-s', '-seed', help='Seed word', required=True)
    ap.add_argument('-i', '-iteration', help='limit to number of related search iteration', default=3)
    ap.add_argument('-k', '-keywordlimit', help='limit to number of keyword request per hour', default=30)
    ap.add_argument('-c', '-comp', help='compute the k-value for the survey index, overrides the iteration '
                                        'limit parameter if given', action='store_true')
    ap.add_argument('-f', '-file', help='file containing the index for computing k-values')

    args = ap.parse_args()

    seed, limit, keycnt, comp, indfile = args.s, int(args.i), int(args.k), bool(args.c), args.f

    if comp:
        comp_survey_index_similarity(seed, indfile, keycnt)
    else:
        run_google_related_queries(seed, limit, keycnt)

    return


if __name__ == '__main__':
    main()
