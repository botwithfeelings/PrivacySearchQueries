#!/usr/bin/env python2.7
#
#
# This script can be used to determine simple recall statistics for the query data set. It does a simple lookup to
# determine what percent of the recall queries was captured by the automated query generation process.
#
#

from argparse import ArgumentParser
from nltk import RegexpTokenizer
import os
import re

QUERY_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'googledata/pruned'))
RECALL_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'surveyQueries/grouped_by_seed'))


def get_recall(recall_list, query_list):
    """
    Determine the fraction of queries in the recall list that were captured by the query list

    :param recall_list: list containing all queries from a recall data set
    :param query_list: list containing all automatically generated queries
    :return: fraction of recall queries captured
    """
    num = 0
    for q in recall_list:
        if q in query_list:
            num += 1

    if len(recall_list) == 0:
        return 0, 0
    return float(num)/float(len(recall_list)), num


def get_recall_unordered(recall_list, query_list):
    """
    Determine the fraction of queries in the recall list that were captured by the query list without concern for
    word order, capitalization, or punctuation. Differences in apostrophes (single quotes) will still be considered.

    :param recall_list: list containing all queries from a recall data set
    :param query_list: list containing all automatically generated queries
    :return: fraction of recall queries captured
    """
    tokenizer = RegexpTokenizer(r'[a-zA-Z\']+')
    query_token = []
    for q in query_list:
        l = tokenizer.tokenize(q.lower())
        sorted(l, key=str.lower)
        query_token.append(l)

    num = 0
    for q in recall_list:
        l = tokenizer.tokenize(q.lower())
        sorted(l, key=str.lower)
        if l in query_token:
            num += 1

    if len(recall_list) == 0:
        return 0, 0
    return float(num)/float(len(recall_list)), num

def run_recall(recall_dir, query_dir):
    """
    Run the recall calculation based on the recall directory and query directory

    :param recall_dir: directory containing all recall queries
    :param query_dir: directory containing all automatically generated queries
    :return: None, prints statistics to stdout
    """
    #total=0
    for candidate in os.listdir(recall_dir):
        recall_file = os.path.join(recall_dir, candidate)
        if os.path.isfile(recall_file):
            query_file = os.path.join(query_dir, candidate)
            if os.path.exists(query_file):
                # we have a file that exists in both, let us determine the recall score
                with open(recall_file, 'r') as f_recall, open(query_file, 'r') as f_query:
                    #recall_reader = csv.reader(f_recall.read().splitlines())
                    #query_reader = csv.reader(f_query.read().splitlines())
                    #recall_list = [re.sub(r'[^\x00-\x7f]',r'', row).lower() for row in recall_reader]
                    #query_list = [re.sub(r'[^\x00-\x7f]',r'', row[0]).encode('ascii', errors='ignore').lower() for row in query_reader]

                    recall_list = [re.sub(r'[^\x00-\x7f]',r'', row).lower() for row in f_recall.read().splitlines()]
                    query_list = [re.sub(r'[^\x00-\x7f]',r'', row).encode('ascii', errors='ignore').split(',')[0].strip().lower() for row in f_query.read().splitlines()]
                    frac1, num1 = get_recall(recall_list, query_list)
                    frac2, num2 = get_recall_unordered(recall_list, query_list)
                    frac3, num3 = get_recall(query_list, recall_list)
                    frac4, num4 = get_recall_unordered(query_list, recall_list)
                    print '\n{}'.format(candidate.split('.')[0])
                    print '\tmetric\t\tordered comparison\t\tunordered comparison'
                    print '\t------\t\t------------------\t\t--------------------'
                    print '\trecall\t\t{:.3f}\t\t{:.3f}'.format(frac1, frac2)
                    print '\tprecision\t\t{:.3f}\t\t{:.3f}'.format(frac3, frac4)

                    print '\n\tnumber of queries in generated set:\t{}\n\tnumber of queries in AMT set:\t{}'.format(len(query_list), len(recall_list))
                    print '\tnumber matching in ordered recall:\t{}\n\tnumber matching in unordered recall:\t{}'.format(num1, num2)
                    print '\tnumber matching in ordered precision:\t{}\n\tnumber matching in unordered precision:\t{}'.format(num3, num4)
                    #total += len(recall_list) - num2

                    # print '{}\n\trecall:\t{:.3f}\t{:.3f}'.format(os.path.splitext(candidate)[0],
                    #                            get_recall(recall_list, query_list),
                    #                            get_recall_unordered(recall_list, query_list)),
                    # print '\tprecision:\t{:.3f}\t{:.3f}'.format(get_recall(query_list, recall_list),
                    #                            get_recall_unordered(query_list, recall_list))
    #print total


def get_recall_arg_parse():
    """
    Get the argument parser for running recall
    :return:
    """

    ap = ArgumentParser(description='Determine the naive recall of the search query data set')
    ap.add_argument('-query',
                    help='Directory containing automatically generated queries',
                    default=QUERY_DIRECTORY)
    ap.add_argument('-recall',
                    help='Directory containing recall queries',
                    default=RECALL_DIRECTORY)

    return ap

if __name__ == '__main__':
    parser = get_recall_arg_parse()
    args = parser.parse_args()

    run_recall(args.recall, args.query)
