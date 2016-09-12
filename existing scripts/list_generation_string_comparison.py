'''This implementation differs from list_generation_string_subset_selection.py in a way
that this implementation adds the entire list of received related queries as candidates 
instead of a subset of the received list.'''
from xml.dom.minidom import parseString
import nltk
from nltk.corpus import stopwords
import sys
import csv
import traceback
from collections import OrderedDict
reload(sys)
sys.setdefaultencoding('utf-8')

#Initialisations
keys = ['dbe5c7c9f9d7418090bc80a24f82809a', '7da3a654733548afb83860868a0f74d0', '1dd4b5e5a7354befa60c95269ca8f3ed', '6037ab4ee95345ac8b3910804e091fda', '542ccb799dfc435ab3f26566d4c3f90d', '24c1878bc1b94388add7d4ae0f5d3731','d6d4990c8506412fa69bbdb7c566dfda'] 
seed_word = str(sys.argv[1])
url = "https://ssl.bing.com/webmaster/api.svc/pox/GetRelatedKeywords"
params = {'startDate': '2015-09-01', 'apikey': keys[3], 'endDate': '2016-02-01', 'language': 'en-US', 'country': 'us'}
queries = OrderedDict() #A dictionary of approved queries along with their overlap value
rejected_queries = OrderedDict()
junk_queries = set()
threshold = 0.25
newset = [seed_word]
fp1 = open("queries_string_"+seed_word+".csv","w")
fp2 = open("discarded_queries_"+seed_word+".csv", "w")
stop = stopwords.words('english')

#A method that cleans the list of obtained queries by removing stop words from every query and return the cleaned queries as a list
def clean_obtained_queries(obtained_queries):
	clean_related_queries = []
	for a in obtained_queries:
		words = nltk.word_tokenize(a)
		clean_tokens = [i for i in words if i not in stop]
		query = " ".join(clean_tokens)
		query = query.strip(' .')
		clean_related_queries.append(query)
	return clean_related_queries

#A method that calculates overlap between a list of related queries and the global set of already approved queries.
def get_overlap(obtained_list, final_list):
	obtained_list = set(obtained_list)
	if len(final_list)==0:
		return 1
	if len(obtained_list)==0:
		return 0
	count = 0.0
	for item in obtained_list:
		if item in final_list:
			count+=1
	control_size = len(final_list) if len(final_list)<len(obtained_list) else len(obtained_list)
	return count/control_size

# A method that chnages the API key to be used in case the current key gets throttled.
def change_key():
	params['apikey'] = keys[0]
	print 'key changed to '+params['apikey']
	keys.append(keys[0])
	del keys[0]

'''The follwoing code block gives an API call on every query in the list newset
 and checks the overlap of the related queries received from API with the set of approved queries.
 If the overlap exceeds the threshold value the query used for the API call is added to approved queries
 and a subset of the received related queries are added as candidates to the list newset. 
 Finally when the candidate list becomes empty, the code writes the approved queries to a csv.'''
try:
	session = requests.Session()
	while len(newset)<40000 and len(newset)>0:
		new_query=newset[0]
		del newset[0]
		params['q']= new_query
		#print params['q']
		#print new_query
		if (new_query in queries) or (new_query in rejected_queries) or (new_query in junk_queries):
			continue
		response = requests.get(url, params = params)
		if response.status_code != 200:
			print response.text
			change_key()
			continue
		try:
			doc = parseString(response.text)
		except:
			continue
		response.close()
		result_list = []
		for result_item in doc.getElementsByTagName("Query"):
			result_list.append(result_item.firstChild.nodeValue)
		related_clean_queries = clean_obtained_queries(result_list)
		overlap_value = get_overlap(related_clean_queries, queries)
		if overlap_value>=threshold:
			queries[new_query]=overlap_value
			newset=newset+related_clean_queries
		else:
			rejected_queries[new_query]=overlap_value
			if overlap_value == 0:
				junk_queries|=set(related_clean_queries)
		print len(newset)
		print "queries = "+ str(len(queries))
		#print queries
except:
	typerroe, value, trace = sys.exc_info()
	print value
	print traceback.format_tb(trace)
	print traceback.print_exc()
finally:
	query_writer = csv.writer(fp1,  lineterminator='\n')
	for key, val in queries.items():
		query_writer.writerow([key, val])
	query_writer = csv.writer(fp2,  lineterminator='\n')
	for key, val in rejected_queries.items():
		query_writer.writerow([key, val])
fp1.close()
fp2.close()