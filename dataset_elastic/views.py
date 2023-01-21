from django.forms.widgets import NullBooleanSelect, Widget
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import simplejson
from urllib.request import urlopen
import urllib
from datetime import datetime
from elasticsearch import Elasticsearch
from glob import glob
from elasticsearch_dsl import Search, Q, Index
from elasticsearch_dsl.query import MatchAll
from django.core import serializers
from .indexingPipeline import DatasetRecords
from .indexingPipeline import WebCrawler
import re
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from spellchecker import SpellChecker
import os

elasticsearch_url = os.environ['ELASTICSEARCH_URL']
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

es = Elasticsearch(elasticsearch_url,http_auth=[elasticsearch_username, elasticsearch_password])

aggregares={
    "ResearchInfrastructure":{
        "terms":{
            "field": "ResearchInfrastructure.keyword",
            "size": 50,
        }
    },
    "spatialCoverage":{
        "terms":{
            "field": "spatialCoverage.keyword",
            "size": 50,
        }
    },
    "theme":{
        "terms":{
            "field": "theme.keyword",
            "size": 50,
        }
    },
    "publisher":{
        "terms":{
            "field": "publisher.keyword",
            "size": 50,
        }
    },
    "measurementTechnique":{
        "terms":{
            "field": "measurementTechnique.keyword",
            "size": 50,
        }
    },
}
#-------------------------------------------------------------------------------------------
def indexingpipeline(request):
    print("indexing...")
    try:
        RI = request.GET['RI']
    except:
        RI = ''

    if RI=="ICOS":
        DatasetRecords.Run_indexingPipeline_ICOS()
    elif RI=="CDI":
        DatasetRecords.Run_indexingPipeline_SeaDataNet_CDI()
    elif RI=="EDMED":
        DatasetRecords.Run_indexingPipeline_SeaDataNet_EDMED()
    elif RI=="LifeWatch":
        DatasetRecords.Run_indexingPipeline_LifeWatch()

    response_data = {}
    response_data['result'] = RI
    response_data['message'] = 'The indexing process of the '+RI+' dataset repository has been initiated!'

    return HttpResponse(json.dumps(response_data), content_type="application/json")
#----------------------------------------------------------------------------------------
def aggregates(request):
    query_body = {
        "from" : page,
        "size" : 10,
        "query": {
            "match_all": {}
        },
        "aggs":aggregares
    }
    result = es.search(index="envri", body=query_body)
    return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})
#----------------------------------------------------------------------------------------
def genericsearch(request):
    try:
        term = request.GET['term']
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
        suggestedSearchTerm = request.GET['suggestedSearchTerm']
    except:
        suggestedSearchTerm = ''

    searchResults=getSearchResults(request, facet, filter, page, term)

    if(suggestedSearchTerm != ""):
        searchResults["suggestedSearchTerm"]=""
    else:
        suggestedSearchTerm=""
        if searchResults["NumberOfHits"]==0:
            suggestedSearchTerm= potentialSearchTerm(term)
            searchResults=getSearchResults(request, facet, filter, page, "*")
            searchResults["NumberOfHits"]=0
            searchResults["searchTerm"]=term
            searchResults["suggestedSearchTerm"]=suggestedSearchTerm

    return render(request,'dataset_results.html',searchResults )

#-----------------------------------------------------------------------------------------------------------------------
def getSearchResults(request, facet, filter, page, term):
    es = Elasticsearch(elasticsearch_url,http_auth=[elasticsearch_username, elasticsearch_password])
    if filter!="" and facet!="":
        saved_list = request.session['filters']
        saved_list.append({"term": {facet+".keyword": filter}})
        request.session['filters'] = saved_list
    else:
        if 'filters' in request.session:
            del request.session['filters']
        request.session['filters']=[]

    page=(int(page)-1)*10
    result={}
    if term=="*" or term=="top10":
        result = es.search(
            index="envri",
            body={
                "from" : page,
                "size" : 10,
                "query": {
                    "bool" : {
                        "must" : {
                            "match_all": {}
                        },
                        "filter": {
                            "bool" : {
                                "must" :request.session.get('filters')
                            }
                        }
                    }
                },
                "aggs":aggregares
            }
        )
    else:
        user_request = "some_param"
        query_body = {
            "from" : page,
            "size" : 10,
            "query": {
                "bool": {
                    "must": {
                        "multi_match" : {
                            "query": term,
                            "fields": [ "description", "keywords", "contact", "publisher", "citation",
                                        "genre", "creator", "headline", "abstract", "theme", "producer", "author",
                                        "sponsor", "provider", "name", "measurementTechnique", "maintainer", "editor",
                                        "copyrightHolder", "contributor", "contentLocation", "about", "rights", "useConstraints",
                                        "status", "scope", "metadataProfile", "metadataIdentifier", "distributionInfo", "dataQualityInfo",
                                        "contentInfo", "ResearchInfrastructure", "EssentialVariables", "potentialTopics"],
                            "type": "best_fields",
                            "minimum_should_match": "50%"
                        }
                    },
                    "filter": {
                        "bool" : {
                            "must" :request.session.get('filters')
                        }
                    }
                }
            },
            "aggs":aggregares
        }

        result = es.search(index="envri", body=query_body)

    lstResults=[]
    LocationspatialCoverage=[]
    spatialCounter=0
    for searchResult in result['hits']['hits']:
        lstResults.append(searchResult['_source'])
        for potentialocation in searchResult['_source']['spatialCoverage']:
            location=re.sub(r'[^A-Za-z0-9 ]+', '', potentialocation)
            if (location!="") and (location!="None") and (len(location)<20) and (location not in LocationspatialCoverage) and (spatialCounter<10):
                spatialCounter=spatialCounter+1
                geoLocation={"location":location, "RI":  searchResult['_source']['ResearchInfrastructure'][0]}
                LocationspatialCoverage.append(geoLocation)

    #......................
    ResearchInfrastructure=[]
    spatialCoverage=[]
    theme=[]
    publisher=[]
    measurementTechnique=[]
    #......................
    for searchResult in result['aggregations']['ResearchInfrastructure']['buckets']:
        if(searchResult['key']!="None" and searchResult['key']!="unknown" and searchResult['key']!="Unknown" and searchResult['key']!="Data" and searchResult['key']!="Unspecified" and searchResult['key']!="" and searchResult['key']!="N/A"):
            RI={
                'key':searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            ResearchInfrastructure.append (RI)
    #......................
    for searchResult in result['aggregations']['spatialCoverage']['buckets']:
        if(searchResult['key']!="None" and searchResult['key']!="unknown" and searchResult['key']!="Unknown" and searchResult['key']!="Data" and searchResult['key']!="Unspecified" and searchResult['key']!="N/A" and searchResult['key']!="" and ("ANE" not in searchResult['key']) and ("Belgian" not in searchResult['key']) and ("calculated BB" not in searchResult['key']) and int(searchResult['doc_count']>1)):
            SC={
                'key':searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            spatialCoverage.append (SC)
        #......................
    for searchResult in result['aggregations']['theme']['buckets']:
        if(searchResult['key']!="None" and searchResult['key']!="unknown" and searchResult['key']!="Unknown" and searchResult['key']!="Data" and searchResult['key']!="Unspecified" and searchResult['key']!="N/A" and searchResult['key']!="" and int(searchResult['doc_count']>1)):
            Th={
                'key':searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            theme.append (Th)
    #......................
    for searchResult in result['aggregations']['publisher']['buckets']:
        if(searchResult['key']!="None" and searchResult['key']!="unknown" and searchResult['key']!="Unknown" and searchResult['key']!="Data" and searchResult['key']!="Unspecified" and searchResult['key']!="N/A" and searchResult['key']!="" and int(searchResult['doc_count']>1 )):
            Pub={
                'key':searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            publisher.append (Pub)
    #......................
    for searchResult in result['aggregations']['measurementTechnique']['buckets']:
        if(searchResult['key']!="None" and searchResult['key']!="unknown" and searchResult['key']!="Unknown" and searchResult['key']!="Data" and searchResult['key']!="Unspecified" and searchResult['key']!="N/A" and searchResult['key']!="" and int(searchResult['doc_count']>1 )):
            meT={
                'key':searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            measurementTechnique.append (meT)
    #......................
    facets={
        'ResearchInfrastructure':ResearchInfrastructure,
        'spatialCoverage':spatialCoverage,
        'theme':theme,
        'publisher':publisher,
        'measurementTechnique':measurementTechnique
    }

    #envri-statics
    #print("Got %d Hits:" % result['hits']['total']['value'])
    #return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})

    numHits=result['hits']['total']['value']

    upperBoundPage=round(np.ceil(numHits/10)+1)
    if(upperBoundPage>10):
        upperBoundPage=11

    result= {
        "facets":facets,
        "results":lstResults,
        "NumberOfHits": numHits,
        "page_range": range(1,upperBoundPage),
        "cur_page": (page/10+1),
        "searchTerm":term,
        "functionList": getAllfunctionList(request),
        "spatialCoverage":LocationspatialCoverage
    }
    return result
#-----------------------------------------------------------------------------------------------------------------------
def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]
#-----------------------------------------------------------------------------------------------------------------------
def potentialSearchTerm(term):
    alternativeSearchTerm=""

    spell = SpellChecker()
    searchTerm=term.split()
    alternativeSearchTerm=""
    for sTerm in searchTerm:
        alterWord=spell.correction(sTerm)
        if(alterWord!=""):
            alternativeSearchTerm= alternativeSearchTerm+" "+alterWord

    alternativeSearchTerm=alternativeSearchTerm.rstrip()
    alternativeSearchTerm=alternativeSearchTerm.lstrip()

    if alternativeSearchTerm==term:
        alternativeSearchTerm=""
        for sTerm in searchTerm:
            syn=synonyms(sTerm)
            if len(syn)>0:
                alterWord=syn[0]
                alternativeSearchTerm= alternativeSearchTerm+" "+alterWord

    alternativeSearchTerm=alternativeSearchTerm.rstrip()
    alternativeSearchTerm=alternativeSearchTerm.lstrip()

    return alternativeSearchTerm
#----------------------------------------------------------------------------------------
def rest(request):
    try:
        term = request.GET['term']
        term=term.rstrip()
        term=term.lstrip()
    except:
        term = ''
    try:
        year_from = request.GET['year_from']
    except:
        year_from = "0"
    try:
        year_to = request.GET['year_to']
    except:
        year_to = "3000"
    try:
        lon = request.GET['lon']
    except:
        lon = "0"
    try:
        lat = request.GET['lat']
    except:
        lat = "0"
    try:
        station = request.GET['station']
    except:
        station = '*'
    try:
        genre = request.GET['genre']
    except:
        genre = '*'
    try:
        author = request.GET['author']
    except:
        author = '*'
    try:
        distributor = request.GET['distributor']
    except:
        distributor = '*'
    try:
        keywords = request.GET['keywords']
    except:
        keywords = '*'
    try:
        abstract = request.GET['abstract']
    except:
        abstract = '*'


    result = esearch(all_fields=term, year_from=year_from, year_to=year_to, lon=lon,
                     lat=lat, station=station.lower(), genre=genre.lower(), author=author.lower(),
                     distributor=distributor.lower(),
                     keywords=keywords.lower(), abstract=abstract.lower())
    return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})
# -------------------------------------------------------------------------
def home(request):
    # index_elastic()
    context = {}
    # context['form'] = SelectionForm()
    # context['result'] = SelectionForm.fields
    return render(request, "home.html", context)
#----------------------------------------------------------------------------------------
def result(request):
    context = {}
    # context['result'] = SelectionForm()
    return render(request, "result.html")
# -------------------------------------------------------------------------
def search_index(request):
    results = []
    keywords_term = ""
    abstract_term = ""
    all_fields_term = ""
    year_from_term = ""
    year_to_term = ""

    """
    if request.GET.get('keywords') and request.GET.get('abstract'):
        keywords_term = request.GET['keywords']
        abstract_term = request.GET['abstract']
    elif request.GET.get('keywords'):
        keywords_term = request.GET['keywords']
    elif request.GET.get('abstract'):
        abstract_term = request.GET['abstract']
    elif request.GET.get('all_fields'):
        all_fields_term = request.GET['all_fields']
    """

    try:
        keywords_term = request.GET['keywords']
    except:
        pass
    try:
        abstract_term = request.GET['abstract']
    except:
        pass
    try:
        all_fields_term = request.GET['all_fields']
    except:
        pass
    try:
        year_from_term = request.GET['year_from']
    except:
        pass
    try:
        year_to_term = request.GET['year_to']
    except:
        pass

    search_term = keywords_term or abstract_term or all_fields_term or year_from_term or year_to_term

    # print(search_term)
    # results = esearch(keywords = keywords_term, abstract=abstract_term, all_terms = all_fields_term)
    results = esearch(keywords=keywords_term,
                      abstract=abstract_term,
                      all_fields=all_fields_term,
                      year_from=year_from_term,
                      year_to=year_to_term)

    # print(results)
    context = {'results': results, 'count': len(results), 'search_term': search_term}
    return render(request, 'search.html', context)
# ----------------------------------------------------------------
def esearch(keywords="",
            abstract="",
            all_fields="",
            year_from="",
            year_to="",
            lon="",
            lat="",
            station="",
            genre="",
            author="",
            distributor="",
            ):
    client = es
    if all_fields == "*":
        filter_type_all_fields = "wildcard"
    else:
        filter_type_all_fields = "match_phrase"

    if keywords == "*":
        filter_type_keywords = "wildcard"
    else:
        filter_type_keywords = "match"

    if abstract == "*":
        filter_type_abstract = "wildcard"
    else:
        filter_type_abstract = "match"

    if station == '*':
        filter_type_provider = "wildcard"
    else:
        filter_type_provider = "match_phrase"

    if genre == '*':
        filter_type_genre = "wildcard"
    else:
        filter_type_genre = "match_phrase"

    if author == '*':
        filter_type_author = "wildcard"
    else:
        filter_type_author = "match_phrase"

    if distributor == '*':
        filter_type_distributor = "wildcard"
    else:
        filter_type_distributor = "match_phrase"

    if lon == "0":
        lon_gte = "-90.0"
        lon_lte = "90.0"

    else:
        lon_gte = (float(lon) - 1)
        lon_lte = (float(lon) + 1)

    if lat == "0":
        lat_gte = "-90.0"
        lat_lte = "90.0"

    else:
        lat_gte = (float(lat) - 1)
        lat_lte = (float(lat) + 1)

    q = Q("bool",

          should=[
              Q(filter_type_all_fields, keywords=keywords),
              Q(filter_type_all_fields, abstract=abstract),
              Q(filter_type_all_fields, keywords=all_fields),
              Q(filter_type_all_fields, abstract=all_fields),
              Q(filter_type_all_fields, name=all_fields),
              Q(filter_type_all_fields, material=all_fields),
              Q(filter_type_all_fields, publisher=all_fields),
              Q(filter_type_all_fields, description=all_fields),
              Q(filter_type_all_fields, provider=all_fields),
              Q(filter_type_all_fields, distributionInfo=all_fields),
              Q(filter_type_all_fields, about=all_fields),
              Q(filter_type_all_fields, citation=all_fields),
              Q(filter_type_all_fields, responsibleParty=all_fields),
              Q(filter_type_all_fields, creator=all_fields),
              Q(filter_type_all_fields, accountablePerson=all_fields),
              Q(filter_type_all_fields, locationCreated=all_fields),
          ],
          minimum_should_match=1
          )

    s = Search(using=client, index="envri") \
            .filter("range", temporal={'gte': year_from, 'lte': year_to}) \
            .filter("range", longitude={'gte': lon_gte, 'lte': lon_lte}) \
            .filter("range", latitude={'gte': lat_gte, 'lte': lat_lte}) \
            .filter(filter_type_provider, provider=station) \
            .filter(filter_type_genre, genre=genre) \
            .filter(filter_type_distributor, distributor=distributor) \
            .filter(filter_type_author, author=author) \
            .query(q)[:1000]

    response = s.execute()
    search = get_results_rest(response)
    return search

#----------------------------------------------------------------------------------------

def get_results_rest(response):
    results = {}
    for hit in response:
        result = {
            'identifier': str(hit.identifier),
            'name': str(hit.name),
            'temporal': str(hit.temporal),
            'author': [name for name in hit.author],
            'landing_page': str(hit.landing_page),
            'keywords': [keyword for keyword in hit.keywords],
            'distributor': str(hit.distributor),
            'station': str(hit.provider),
            'genre': str(hit.genre),
            'longitude': str(hit.longitude),
            'latitude': str(hit.latitude),
            'abstract': str(hit.abstract)
        }
        results[hit.identifier] = result
    return results

#----------------------------------------------------------------------------------------
def get_results(response):
    results = []
    for hit in response:
        result_tuple = (hit.identifier, hit.landing_page, hit.name)
        results.append(result_tuple)
    return results

#-----------------------------------------------------------------------------------------------------------------------
def getAllfunctionList(request):
    if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
        request.session['BasketURLs'] = []
    if not 'MyBasket' in request.session or not request.session['MyBasket']:
        request.session['MyBasket'] = []

    functionList=""
    saved_list = request.session['MyBasket']
    for item in saved_list:
        functionList= functionList+r"modifyCart({'operation':'add','type':'"+item['type']+"','title':'"+item['title']+"','url':'"+item['url']+"','id':'"+item['id']+"' });"
    return functionList
