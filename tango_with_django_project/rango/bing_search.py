import requests
import sys
from keys import BING_API_KEY

def run_query(search_terms):
    #Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/v1/'
    source = 'Web'
    username = ''
    
    #Specify how many results we wish to be returned per page.
    #Offset specifies where in the results list to start from.
    results_per_page = 10
    offset = 0
    
    #Wrap quotes around our query terms as required by the Bing API.
    #The query we will then use is stored within variable query.
    query = "'{0}'".format(search_terms.replace(" ", "%20"))
    
    #Construct the latter part of our request's URL.
    #Set the format of the response to json and sets other properties.
    search_url = "{0}{1}?Query=%27{4}%27&$format=json&$top={2}&$skip={3}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)
    
    #Create our results list
    results = []
    
    try:
        
        #Connect to the server and read the response generated as JSON
        json_response = requests.get(search_url, auth=(username, BING_API_KEY)).json()
        
        
        #Loop through each page returned, populating out results list.
        for result in json_response['d']['results']:
            results.append({
            'title': result['Title'],
            'link': result['Url'],
            'summary': result['Description']})
        
    except requests.exceptions.RequestException as e:
        print 'Error when querying'
        print e
        sys.exit(1)
    
    #Return the list of results so the calling function.
    return results

def main():
    results = run_query(raw_input("Search Query\n:>"))
    
    for result in results:
        print "Title  - " + result['title']
        print "URL - " + result['link']
        print "Summary - " + result['summary']

if __name__ == '__main__':
    main()
    
    