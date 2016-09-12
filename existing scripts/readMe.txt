The files are as follows:
1)list_generation_ngram_comparison.py:
	This script creates a list of keywords related to a provided seed. The Bing API returns a list of keywords associated with a certain keyword. The script maintains a list of approved queries and each time the API returns a list of queries for a parameter query, the script checks the overlap between returned queries and approved queries. If the overlap exceeds a pre configured threshold the parameter query is added to approved queries and the list returned by the API is added to a list of candidate queries, each of which would be supplied to the API in subsequent iterations of the loop. The script stops when the list of candidate queries becomes empty. The comparison method used for calculating overlap is checking for equivalent ngrams.

	Command: python list_generation_ngram_comparison.py <seed>


2) list_generation_ngram_subset_selection.py:
	This script performs the same task as 'list_generation_ngram_comparison.py' with a subtle difference that if a query is approved for adding to the list of approved queries, we add a subset of the related queries returned by API as candidates to the next round.

	Command: python list_generation_ngram_subset_selection.py <seed>


3) list_generation_string_comparison.py:
	This script peforms same task as 'list_generation_ngram_comparison.py' with a subtle difference that the comparison method used to calculate overlap is direct string comparison between queries of both lists i.e. the list returned by the API and the list of approved queries.

	Command: python list_generation_string_comparison.py <seed>


4) list_generation_string_subset_selection.py:
	This script works similar to 'list_generation_string_comparison.py' with a subtle difference that if a query is approved for adding to the list of approved queries, we add a subset of the related queries returned by API as candidates to the next round

	Command: python list_generation_string_subset_selection.py <seed>


5) GTrends.py
	This script downloads Google Trends data for a list supplied keywords and saves it to multiple csv files. One file is created per keyword. The script accepts a csv file which lists the keywords to fetch trends data for.

	command: python GTrends.py <csv file name>