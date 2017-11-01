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
                                                   'indextrends/index'))
FILTERED_RECALL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    'indextrends/amt'))


def run_recall_with_trend(recall_dir, query_dir):
    """
    Run the recall calculation based on the recall directory and query directory

    :param recall_dir: directory containing all recall queries
    :param query_dir: directory containing all automatically generated queries
    :return: None, prints statistics to stdout
    """
    total = 0
    for category in os.listdir(recall_dir):
        cat_recall = os.path.join(recall_dir, category)
        cat_query = os.path.join(query_dir, category)
        if os.path.isdir(cat_recall):
            for candidate in os.listdir(cat_recall):
                if candidate != 'combined.xlsx':
                    recall_file = os.path.join(cat_recall, candidate)
                    query_file = os.path.join(cat_query, candidate)
                    if os.path.exists(query_file):
                        # we have a directory that exists in both, let us determine the recall score
                        with open(recall_file, 'r') as f_recall, open(query_file, 'r') as f_query:
                            recall_list = f_recall.readline().lower().split(',')[1:-1]
                            query_list = f_query.readline().lower().split(',')[1:-1]
                            frac1, num1 = get_recall(recall_list, query_list)
                            frac2, num2 = get_recall_unordered(recall_list, query_list)
                            frac3, num3 = get_recall(query_list, recall_list)
                            frac4, num4 = get_recall_unordered(query_list, recall_list)


                            print '{}\n{}\t{}\n\trecall:\t{:.3f}\t{:.3f}'.format(candidate.split('.')[0], len(recall_list), len(query_list),
                                                       frac1,
                                                       frac2),
                            print '\tprecision:\t{:.3f}\t{:.3f}'.format(frac3,
                                                       frac4)
                            print '{}\t{}'.format(num1, num2)
                            total += len(recall_list) - num2
    print total


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
