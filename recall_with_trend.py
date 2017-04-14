#!/usr/bin/env python2.7
#
#
# This script can be used to determine simple recall statistics for the query data set with trend data. It does a simple
# lookup to determine what percent of the recall queries was captured by the automated query generation process.
#
#

from argparse import ArgumentParser
import os

from recall_simple import get_recall, get_recall_unordered

FILTERED_QUERY_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   'gtrends/without_seed_cmp'))
FILTERED_RECALL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    'gtrends/without_seed_cmp_amt'))


def run_recall_with_trend(recall_dir, query_dir):
    """
    Run the recall calculation based on the recall directory and query directory

    :param recall_dir: directory containing all recall queries
    :param query_dir: directory containing all automatically generated queries
    :return: None, prints statistics to stdout
    """
    for candidate in os.listdir(recall_dir):
        recall_candidate = os.path.join(recall_dir, candidate)
        if os.path.isdir(recall_candidate):
            query_candidate = os.path.join(query_dir, candidate)
            if os.path.exists(query_candidate):
                # we have a directory that exists in both, let us determine the recall score
                recall_list = [os.path.splitext(q.lower())[0] for q in os.listdir(recall_candidate)]
                query_list = [os.path.splitext(q.lower())[0] for q in os.listdir(query_candidate)]

                print '{}\n\trecall:\t{:.3f}\t{:.3f}'.format(candidate,
                                           get_recall(recall_list, query_list),
                                           get_recall_unordered(recall_list, query_list)),
                print '\tprecision:\t{:.3f}\t{:.3f}'.format(get_recall(query_list, recall_list),
                                           get_recall_unordered(query_list, recall_list))


def get_recall_trend_arg_parse():
    """
    Get the argument parser for running recall
    :return:
    """

    ap = ArgumentParser(description='Determine the naive recall of the search query data set using only queries with '
                                    'trend data')
    ap.add_argument('-query',
                    help='Directory containing automatically generated seed queries',
                    default=FILTERED_QUERY_DIR)
    ap.add_argument('-recall',
                    help='Directory containing recall seed queries',
                    default=FILTERED_RECALL_DIR)

    return ap

if __name__ == '__main__':
    parser = get_recall_trend_arg_parse()
    args = parser.parse_args()

    run_recall_with_trend(args.recall, args.query)
