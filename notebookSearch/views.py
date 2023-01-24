import calendar
import json
import os
import urllib
from datetime import time
from urllib.request import urlopen

import gitlab
import numpy as np
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from elasticsearch import Elasticsearch
from github import Github, RateLimitExceededException
from spellchecker import SpellChecker

import logging

logger = logging.getLogger(__name__)

elasticsearch_url = os.environ['ELASTICSEARCH_URL']
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')
base_path = os.environ.get('BASE_PATH', '/')

es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
# -------------------------------------------------------------------------------------------
ACCESS_TOKEN_Github = os.environ['ACCESS_TOKEN_Github']
ACCESS_TOKEN_Gitlab = os.environ['ACCESS_TOKEN_Gitlab']

# http request authentication
header = {"Authorization": "token %s" % ACCESS_TOKEN_Github}
# initialize query request parameters
page_url = '&per_page=100'
indexPath = "/var/lib/opensemanticsearch/notebookSearch/Indexes.json"


# -------------------------------------------------------------------------------------------
def genericsearch(request):
    try:
        term = request.GET['term']
    except:
        term = ''
    response_data = {}

    if (term == "*"):
        term = ""
    # response_data= search_github_by_url(term)
    #   response_data=search_repository_github(term)
    # search_projects_Gitlab(term)

    #   indexFile= open("notebooks.json","w+")
    #   indexFile.write(json.dumps(response_data))
    #   indexFile.close()

    #    return HttpResponse(json.dumps(response_data), content_type="application/json")

    try:
        term = request.GET['term']
        term = term.rstrip()
        term = term.lstrip()
    except:
        term = ''

    try:
        page = request.GET['page']
    except:
        page = 0

    try:
        filter = request.GET['filter']
    except:
        filter = ''

    try:
        facet = request.GET['facet']
    except:
        facet = ''

    try:
        suggested_search_term = request.GET['suggestedSearchTerm']
    except:
        suggested_search_term = ''

    search_results = getSearchResults(request, facet, filter, page, term)

    if suggested_search_term != "":
        search_results["suggestedSearchTerm"] = ""
    else:
        suggested_search_term = ""
        if search_results["NumberOfHits"] == 0:
            suggested_search_term = potentialSearchTerm(term)
            search_results = getSearchResults(request, facet, filter, page, "*")
            search_results["NumberOfHits"] = 0
            search_results["searchTerm"] = term
            search_results["suggestedSearchTerm"] = suggested_search_term
    search_results['base_path'] = base_path
    return render(request, 'notebook_results.html', search_results)


# -----------------------------------------------------------------------------------------------------------------------
def potentialSearchTerm(term):
    alternative_search_term = ""

    spell = SpellChecker()
    search_term = term.split()
    alternative_search_term = ""
    for sTerm in search_term:
        alter_word = spell.correction(sTerm)
        if alter_word:
            alternative_search_term = alternative_search_term + " " + alter_word

    alternative_search_term = alternative_search_term.rstrip()
    alternative_search_term = alternative_search_term.lstrip()

    if alternative_search_term == term:
        alternative_search_term = ""
        for sTerm in search_term:
            syn = synonyms(sTerm)
            if len(syn) > 0:
                alter_word = syn[0]
                alternative_search_term = alternative_search_term + " " + alter_word

    alternative_search_term = alternative_search_term.rstrip()
    alternative_search_term = alternative_search_term.lstrip()

    return alternative_search_term


# -----------------------------------------------------------------------------------------------------------------------

def getSearchResults(request, facet, filter, page, term):
    if filter != "" and facet != "":
        saved_list = request.session['filters']
        saved_list.append({"term": {facet + ".keyword": filter}})
        request.session['filters'] = saved_list
    else:
        if 'filters' in request.session:
            del request.session['filters']
        request.session['filters'] = []

    page = (int(page) - 1) * 10
    result = {}
    if term == "*" or term == "top10":
        result = es.search(
            index="notebooks",
            body={
                "from": page,
                "size": 10,
                "query": {
                    "bool": {
                        "must": {
                            "match_all": {}
                        }
                    }
                }
            }
        )
    else:
        user_request = "some_param"
        query_body = {
            "from": page,
            "size": 10,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": term,
                            "fields": ["name", "description"],
                            "type": "best_fields",
                            "minimum_should_match": "50%"
                        }
                    },
                }
            }
        }

        result = es.search(index="notebooks", body=query_body)
    lstResults = []

    for searchResult in result['hits']['hits']:
        lstResults.append(searchResult['_source'])

    numHits = result['hits']['total']['value']

    upperBoundPage = round(np.ceil(numHits / 10) + 1)
    if (upperBoundPage > 10):
        upperBoundPage = 11

    facets = []

    results = {
        "facets": facets,
        "results": lstResults,
        "NumberOfHits": numHits,
        "page_range": range(1, upperBoundPage),
        "cur_page": (page / 10 + 1),
        "searchTerm": term,
        "functionList": getAllfunctionList(request)
    }

    return results


# -----------------------------------------------------------------------------------------------------------------------
def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]


# -------------------------------------------------------------------------------------------
def search_projects_Gitlab(keyword):
    #    cURL = r'curl --header "PRIVATE-TOKEN:'+ACCESS_TOKEN_Gitlab+'" "https://gitlab.example.com/api/v4/search?scope=projects&search='+keyword+'"'
    gl = gitlab.Gitlab('https://gitlab.com/', private_token=os.getenv(ACCESS_TOKEN_Gitlab))
    gl.search(gitlab.SEARCH_SCOPE_ISSUES, keyword, page=2, per_page=10)

    # get a generator that will automatically make required API calls for
    # pagination
    for item in gl.search(gitlab.SEARCH_SCOPE_ISSUES, 'search_str', as_list=False):
        print(item)

    json_data = {}
    return json_data


# -------------------------------------------------------------------------------------------

def search_repository_github(keywords):
    g = Github(ACCESS_TOKEN_Github)
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    keywords.append("notebook")
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    cnt = 0
    data = []
    iter_obj = iter(result)
    while True:
        try:
            cnt = cnt + 1
            repo = next(iter_obj)
            new_record = {
                "id": cnt,
                "name": repo.full_name,
                "description": result.sub(r'[^A-Za-z0-9 ]+', '', repo.description),
                "html_url": repo.html_url,
                "git_url": repo.clone_url,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "size": repo.size,
            }
            if new_record["language"] == "Jupyter Notebook" and new_record not in data:
                data.append(new_record)
        except StopIteration:
            break
        except RateLimitExceededException:
            continue
    data = (json.dumps({"results_count": result.totalCount, "hits": data}).replace("'", '"'))
    return json.loads(data)


# -------------------------------------------------------------------------------------------
def github_index_pipeline(request):
    g = Github(ACCESS_TOKEN_Github)
    try:
        keywords = request.GET['term']
    except:
        keywords = ''
    response_data = {}

    if (keywords == "*"):
        keywords = ""

    keywords = [keyword.strip() for keyword in keywords.split(',')]
    keywords.append("Jupyter Notebook")
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    cnt = 0
    data = []
    iter_obj = iter(result)
    while True:
        try:
            cnt = cnt + 1
            repo = next(iter_obj)
            new_record = {
                "id": cnt,
                "name": repo.full_name,
                "html_url": repo.html_url,
                "git_url": repo.clone_url,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "size": repo.size,
            }
            if new_record["language"] == "Jupyter Notebook" and new_record not in data:
                data.append(new_record)
        except StopIteration:
            break
        except RateLimitExceededException:
            search_rate_limit = g.get_rate_limit().search
            logger.info('search remaining: {}'.format(search_rate_limit.remaining))
            reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
            # add 10 seconds to be sure the rate limit has been reset
            sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
            time.sleep(sleep_time)
            continue
    indexFile = open(indexPath, "w+")
    indexFile.write(json.dumps(data))
    indexFile.close()
    return "Github indexing finished!"


# -------------------------------------------------------------------------------------------
def search_code_github(keyword):
    rate_limit = 'g.get_rate_limit()'
    rate = rate_limit.search
    if rate.remaining == 0:
        print(f'You have 0/{rate.limit} API calls remaining. Reset time: {rate.reset}')
        return
    else:
        print(f'You have {rate.remaining}/{rate.limit} API calls remaining')

    query = f'"{keyword} english" in:file extension:po'
    result = 'g.search_code(query, order=\'desc\')'

    max_size = 100
    print(f'Found {result.totalCount} file(s)')
    if result.totalCount > max_size:
        result = result[:max_size]

    for file in result:
        print(f'{file.download_url}')


# -------------------------------------------------------------------------------------------
def search_repository_github_by_url(keywords):
    query = 'https://api.github.com/search/repositories?q=' + keywords

    request = urllib.request.urlopen(query)
    data = json.load(request)
    return data


# -----------------------------------------------------------------------------------------------------------------------
def getAllfunctionList(request):
    if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
        request.session['BasketURLs'] = []
    if not 'MyBasket' in request.session or not request.session['MyBasket']:
        request.session['MyBasket'] = []

    functionList = ""
    saved_list = request.session['MyBasket']
    for item in saved_list:
        functionList = functionList + r"modifyCart({'operation':'add','type':'" + item['type'] + "','title':'" + item[
            'title'] + "','url':'" + item['url'] + "','id':'" + item['id'] + "' });"
    return functionList
