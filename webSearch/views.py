from django.http import JsonResponse, HttpResponse
import json
import os
import re
import uuid
from urllib.parse import urlparse

import dateutil.parser
import ijson
import nltk
import numpy as np
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseBadRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from spellchecker import SpellChecker

nltk.download('words')

elasticsearch_url = os.environ['ELASTICSEARCH_URL']
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

words = set(nltk.corpus.words.words())
ResearchInfrastructures = {
    'icos-cp.eu': {
        'id': 1,
        'url': 'https://www.icos-cp.eu/',
        'label': 'Multi-domain',
        'title': 'Integrated Carbon Observation System',
        'acronym': 'ICOS'
    },
    'seadatanet.org': {
        'id': 2,
        'url': 'https://www.seadatanet.org/',
        'label': 'Marine',
        'title': 'Pan-European infrastructure for ocean and marine data management',
        'acronym': 'SeaDataNet'
    },
    'lifewatch.eu': {
        'id': 3,
        'url': 'https://www.lifewatch.eu/',
        'label': 'Multi-domain',
        'title': 'An e-Infrastructure for basic research on biodiversity and ecosystems',
        'acronym': 'LifeWatch'
    },
    'anaee.eu': {
        'id': 4,
        'url': 'https://www.anaee.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Analysis and Experimentation on Ecosystems',
        'acronym': 'AnaEE'
    },
    'actris.eu': {
        'id': 5,
        'url': 'https://www.actris.eu/',
        'label': 'Atmospheric',
        'title': 'The Aerosol, Clouds and Trace Gases Research Infrastructure',
        'acronym': 'ACTRIS'
    },
    'aquacosm.eu': {
        'id': 6,
        'url': 'https://www.aquacosm.eu/',
        'label': 'Marine / Freshwater',
        'title': 'EU network of mesocosms facilities for research on marine and freshwater',
        'acronym': 'AQUACOSM'
    },
    'arise-project.eu': {
        'id': 7,
        'url': 'http://arise-project.eu/',
        'label': 'Atmosphere',
        'title': 'Atmospheric dynamics Research InfraStructure in Europe',
        'acronym': 'ARISE'
    },
    'danubius-pp.eu': {
        'id': 8,
        'url': 'https://danubius-pp.eu/',
        'label': 'River / Marine',
        'title': 'Preparatory Phase For The Paneuropean Research Infrastructure',
        'acronym': 'DANUBIUS-RI'
    },
    'dissco.eu': {
        'id': 9,
        'url': 'https://www.dissco.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Distributed System of Scientific Collections',
        'acronym': 'DiSSCo'
    },
    'eiscat.se': {
        'id': 10,
        'url': 'https://eiscat.se/',
        'label': 'Atmospheric',
        'title': 'EISCAT Scientific Association',
        'acronym': 'EISCAT 3D'
    },
    "elter-ri.eu": {
        "id": 11,
        "url": "https://elter-ri.eu/",
        "domain": "Biodiversity / Ecosystems",
        "title": "Long-Term Ecosystem Research in Europe",
        "acronym": "eLTER RI"
    },
    'embrc.eu': {
        'id': 12,
        'url': 'https://www.embrc.eu/',
        'label': 'Marine / Biodiversity',
        'title': 'Long-Term Ecosystem Research in Europe',
        'acronym': 'EMBRC'
    },
    'emso.eu': {
        'id': 13,
        'url': 'https://emso.eu/',
        'label': 'Multi-domain',
        'title': 'European Multidisciplinary Seafloor and water column Observatory',
        'acronym': 'EMSO'
    },
    'emphasis.plant-phenotyping.eu': {
        'id': 14,
        'url': 'https://emphasis.plant-phenotyping.eu/',
        'label': 'Terrestrial Ecosystem',
        'title': 'European Infrastructure for Plant Phenotyping',
        'acronym': 'EMPHASIS'
    },
    'epos-eu.org': {
        'id': 15,
        'url': 'https://www.epos-eu.org/',
        'label': 'Solid Earth Science',
        'title': 'European Plate Observing System',
        'acronym': 'EPOS'
    },
    'eufar.net': {
        'id': 16,
        'url': 'https://www.eufar.net/',
        'label': 'Atmospheric',
        'title': 'The EUropean Facility for Airborne Research',
        'acronym': 'EUFAR'
    },
    'euro-argo.eu': {
        'id': 17,
        'url': 'https://www.euro-argo.eu/',
        'label': 'Marine',
        'title': 'European Research Infrastructure Consortium for observing the Ocean',
        'acronym': 'Euro-Argo ERIC'
    },
    'eurofleet.fr': {
        'id': 18,
        'url': 'https://www.eurofleet.fr/',
        'label': 'Marine',
        'title': 'An alliance of European marine research infrastructure to meet the evolving needs of the research and industrial communities',
        'acronym': 'EUROFLEETS+'
    },
    'eurogoos.eu': {
        'id': 19,
        'url': 'https://eurogoos.eu/',
        'label': 'Marine',
        'title': 'European Global Ocean Observing System',
        'acronym': 'EuroGOOS'
    },
    'eurochamp.org': {
        'id': 20,
        'url': 'https://www.eurochamp.org/',
        'label': 'Atmospheric',
        'title': 'Integration of European Simulation Chambers for Investigating Atmospheric Processes',
        'acronym': 'EUROCHAMP'
    },
    'hemera-h2020.eu': {
        'id': 21,
        'url': 'https://www.hemera-h2020.eu/',
        'label': 'Atmospheric',
        'title': 'Integrated access to balloon-borne platforms for innovative research and technology',
        'acronym': 'HEMERA'
    },
    'iagos.org': {
        'id': 22,
        'url': 'https://www.iagos.org/',
        'label': 'Atmospheric',
        'title': 'In Service Aircraft for a Global Observing System',
        'acronym': 'IAGOS'
    },
    'eu-interact.org': {
        'id': 23,
        'url': 'https://eu-interact.org/',
        'label': 'Terrestrial Ecosystem',
        'title': 'Building Capacity For Environmental Research And Monitoring In Arctic And Neighbouring Alpine And Forest Areas',
        'acronym': 'INTERACT'
    },
    'is.enes.org': {
        'id': 24,
        'url': 'https://is.enes.org/',
        'label': 'Multi-domain',
        'title': 'Infrastructure For The European Network For Earth System Modelling Enes',
        'acronym': 'IS-ENES'
    },
    'jerico-ri.eu': {
        'id': 25,
        'url': 'https://www.jerico-ri.eu/',
        'label': 'Marine',
        'title': 'The European Integrated Infrastructure For In Situ Coastal Observation',
        'acronym': 'JERICO-RI'
    },
    'sios-svalbard.org': {
        'id': 26,
        'url': 'https://www.sios-svalbard.org/',
        'label': 'Multi-domain',
        'title': 'Svalbard integrated Earth observing system',
        'acronym': 'SIOS'
    }
}
aggregares = {
    "locations": {
        "terms": {
            "field": "locations.keyword",
            "size": 20,
        }
    },
    "people": {
        "terms": {
            "field": "people.keyword",
            "size": 20,
        }
    },
    "organizations": {
        "terms": {
            "field": "organizations.keyword",
            "size": 20,
        }
    },
    "products": {
        "terms": {
            "field": "products.keyword",
            "size": 20,
        }
    },
    "workOfArt": {
        "terms": {
            "field": "workOfArt.keyword",
            "size": 20,
        }
    },
    'ResearchInfrastructure': {
        "terms": {
            "field": "researchInfrastructure.acronym.keyword",
            "size": 20,
        }
    },
    "files": {
        "terms": {
            "field": "files.extension.keyword",
            "size": 20,
        }
    }
}


def upload_from_json_stream(request, libpath=None):
    title_txt = []
    organization_ss = []
    created_ss = []
    content_type_ss = []
    file_modified_dt = []
    author_ss = []
    producer_ss = []
    language_s = []
    filename_extension_s = []
    person_ss = []
    location_ss = []
    id = []
    dc_format_ss = []
    dc_title_ss = []
    File_Size_ss = []
    _text_ = []
    cnt = 1
    with open(libpath, "rb") as input_file:
        parser = ijson.parse(input_file)
        for doc in parser:
            if doc[2] == "_version_":
                cnt = cnt + 1
                print("Record " + str(cnt) + " added!")
                doc = {
                    "title_txt": title_txt,
                    "organization_ss": organization_ss,
                    "created_ss": created_ss,
                    "content_type_ss": content_type_ss,
                    "file_modified_dt": file_modified_dt,
                    "author_ss": author_ss,
                    "producer_ss": producer_ss,
                    "language_s": language_s,
                    "filename_extension_s": filename_extension_s,
                    "person_ss": person_ss,
                    "location_ss": location_ss,
                    "id": id,
                    "dc_format_ss": dc_format_ss,
                    "File_Size_ss": File_Size_ss,
                    "_text_": _text_
                }
                save_record(doc)

                title_txt.clear()
                organization_ss.clear()
                created_ss.clear()
                content_type_ss.clear()
                file_modified_dt.clear()
                author_ss.clear()
                producer_ss.clear()
                language_s.clear()
                filename_extension_s.clear()
                person_ss.clear()
                location_ss.clear()
                id.clear()
                dc_format_ss.clear()
                dc_title_ss.clear()
                File_Size_ss.clear()
                _text_.clear()
            else:
                if (doc[1] == "string"):
                    if "response.docs.item.title_txt" in doc[0]:
                        title_txt.append(doc[2])
                    elif "response.docs.item.organization_ss" in doc[0]:
                        organization_ss.append(doc[2])
                    elif "response.docs.item.created_ss" in doc[0]:
                        created_ss.append(doc[2])
                    elif "response.docs.item.content_type_ss" in doc[0]:
                        content_type_ss.append(doc[2])
                    elif "response.docs.item.file_modified_dt" in doc[0]:
                        file_modified_dt.append(doc[2])
                    elif "response.docs.item.author_ss" in doc[0]:
                        author_ss.append(doc[2])
                    elif "response.docs.item.producer_ss" in doc[0]:
                        producer_ss.append(doc[2])
                    elif "response.docs.item.id" in doc[0]:
                        id.append(doc[2])
                    elif "response.docs.item.language_s" in doc[0]:
                        language_s.append(doc[2])
                    elif "response.docs.item.filename_extension_s" in doc[0]:
                        filename_extension_s.append(doc[2])
                    elif "response.docs.item.person_ss" in doc[0]:
                        person_ss.append(doc[2])
                    elif "response.docs.item.location_ss" in doc[0]:
                        location_ss.append(doc[2])
                    elif "response.docs.item.dc_format_ss" in doc[0]:
                        dc_format_ss.append(doc[2])
                    elif "response.docs.item.dc_title_ss" in doc[0]:
                        dc_title_ss.append(doc[2])
                    elif "response.docs.item.File_Size_ss" in doc[0]:
                        File_Size_ss.append(doc[2])
                    elif "response.docs.item._text_" in doc[0]:
                        _text_.append(doc[2])


# -----------------------------------------------------------------------------------------------------------------------
def save_record(doc):
    es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
    index = Index('webcontents', es)

    if not es.indices.exists(index='webcontents'):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
    else:
        es.indices.close(index='webcontents')
        put = es.indices.put_settings(
            index='webcontents',
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index='webcontents')

    title_txt = []
    organization_ss = []
    created_ss = []
    content_type_ss = []
    file_modified_dt = []
    author_ss = []
    producer_ss = []
    language_s = []
    filename_extension_s = []
    person_ss = []
    location_ss = []
    id = []
    dc_format_ss = []
    dc_title_ss = []
    File_Size_ss = []
    _text_ = []

    if "title_txt" in doc:
        title_txt.clear()
        for txt in doc["title_txt"]:
            txt = text_cleansing(txt)
            if txt and txt not in title_txt:
                title_txt.append(txt)
    else:
        title_txt = ["N/A"]
    # ........................................................
    if "organization_ss" in doc:
        organization_ss.clear()
        for txt in doc["organization_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in organization_ss:
                organization_ss.append(txt)
    else:
        organization_ss = ["N/A"]
    # ........................................................
    if "created_ss" in doc:
        created_ss.clear()
        for txt in doc["created_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in created_ss:
                created_ss.append(dateutil.parser.parse(txt))
    else:
        created_ss = ["N/A"]
    # ........................................................
    if "content_type_ss" in doc:
        content_type_ss.clear()
        for txt in doc["content_type_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in content_type_ss:
                content_type_ss.append(txt)
    else:
        content_type_ss = ["N/A"]
    # ........................................................
    if "file_modified_dt" in doc:
        file_modified_dt.clear()
        for txt in doc["file_modified_dt"]:
            txt = text_cleansing(txt)
            if txt and txt not in file_modified_dt:
                file_modified_dt.append(dateutil.parser.parse(txt))
    else:
        file_modified_dt = ["N/A"]
    # ........................................................
    if "author_ss" in doc:
        author_ss.clear()
        for txt in doc["author_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in author_ss:
                author_ss.append(txt)
    else:
        author_ss = ["N/A"]
    # ........................................................
    if "producer_ss" in doc:
        producer_ss.clear()
        for txt in doc["producer_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in producer_ss:
                producer_ss.append(txt)
    else:
        producer_ss = ["N/A"]
    # ........................................................
    if "language_s" in doc:
        language_s.clear()
        for txt in doc["language_s"]:
            txt = text_cleansing(txt)
            if txt and txt not in language_s:
                language_s.append(txt)
    else:
        language_s = ["N/A"]
    # ........................................................
    if "filename_extension_s" in doc:
        filename_extension_s.clear()
        for txt in doc["filename_extension_s"]:
            txt = text_cleansing(txt)
            if txt and txt not in filename_extension_s:
                filename_extension_s.append(txt)
    else:
        filename_extension_s = ["N/A"]
    # ........................................................
    if "person_ss" in doc:
        person_ss.clear()
        for txt in doc["person_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in person_ss:
                person_ss.append(txt)
    else:
        person_ss = ["N/A"]
    # ........................................................
    if "location_ss" in doc:
        location_ss.clear()
        for txt in doc["location_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in location_ss:
                location_ss.append(txt)
    else:
        location_ss = ["N/A"]
    # ........................................................
    if "id" in doc:
        id.clear()
        for txt in doc["id"]:
            if txt and txt not in id:
                id.append(txt)
    else:
        id = ["N/A"]
        return 0
    # ........................................................
    if "dc_format_ss" in doc:
        dc_format_ss.clear()
        for txt in doc["dc_format_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in dc_format_ss:
                dc_format_ss.append(txt)
    else:
        dc_format_ss = ["N/A"]
    # ........................................................
    if "dc_title_ss" in doc:
        dc_title_ss.clear()
        for txt in doc["dc_title_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in dc_title_ss:
                dc_title_ss.append(txt)
    else:
        dc_title_ss = ["N/A"]
    # ........................................................
    if "File_Size_ss" in doc:
        File_Size_ss.clear()
        for txt in doc["File_Size_ss"]:
            txt = text_cleansing(txt)
            if txt and txt not in File_Size_ss:
                File_Size_ss.append(txt)
    else:
        File_Size_ss = ["N/A"]
    # ........................................................
    if "_text_" in doc:
        _text_.clear()
        for txt in doc["_text_"]:
            txt = text_cleansing(txt)
            if txt and txt not in _text_:
                _text_.append(txt)
    else:
        _text_ = ["N/A"]
    # ........................................................
    webFeatures = {
        "title": title_txt,
        "organizations": organization_ss,
        "creation_date": created_ss,
        "content_type": content_type_ss,
        "modification_date": file_modified_dt,
        "authors": author_ss,
        "producers": producer_ss,
        "language": language_s,
        "file_extensions": filename_extension_s,
        "person": person_ss,
        "locations": location_ss,
        "id": id,
        "file_formats": dc_format_ss,
        "file_size": File_Size_ss,
        "text": _text_,
        'ResearchInfrastructure': get_research_infrastructure(id[0])
    }
    res = es.index(index="webcontents", id=id, body=webFeatures)
    es.indices.refresh(index="webcontents")


# ----------------------------------------------------------------------------------------------------------------------- envri-search-engine
def get_research_infrastructure(url):
    lst_ri = []
    for RI in ResearchInfrastructures:
        if RI in url:
            if ResearchInfrastructures[RI]['acronym'] not in lst_ri:
                lst_ri.append(ResearchInfrastructures[RI]['acronym'])
    return lst_ri


# ----------------------------------------------------------------------------------------------------------------------- envri-search-engine
def text_cleansing(txt):
    if type(txt) == str:
        res = isinstance(txt, str)
        if res:
            txt = re.sub(r'[^A-Za-z0-9 .-\?/:,;~%$#*@!&+=_><]+', '', txt)
    if len(txt) == 1:
        txt = ""
    return txt


# ----------------------------------------------------------------------------------------------------------------------- envri-search-engine
def aggregates(request):
    print("indexing...")
    response_data = {'result': "", 'message': 'The indexing process of the dataset repository has been initiated!'}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# -----------------------------------------------------------------------------------------------------------------------
def generic_search(request):
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
        searchtype = request.GET['searchtype']
    except:
        searchtype = 'websearch'

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

    search_results = get_search_results(request, facet, filter, searchtype, page, term)

    if suggestedSearchTerm != "":
        search_results["suggestedSearchTerm"] = ""
    else:
        suggestedSearchTerm = ""
        if search_results["NumberOfHits"] == 0:
            suggestedSearchTerm = potential_search_term(term)
            search_results = get_search_results(request, facet, filter, searchtype, page, "*")
            search_results["NumberOfHits"] = 0
            search_results["searchTerm"] = term
            search_results["suggestedSearchTerm"] = suggestedSearchTerm

    if searchtype == 'imagesearch':
        html_render = 'imagesearch_results.html'
    else:
        html_render = 'webcontent_results.html'

    return render(request, html_render, search_results)


# -----------------------------------------------------------------------------------------------------------------------
def potential_search_term(term):
    spell = SpellChecker()
    search_term = term.split()
    alternative_search_term = ""
    for sTerm in search_term:
        alter_word = spell.correction(sTerm)
        if alter_word != "":
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

def get_search_results(request, facet, filter, searchtype, page, term):
    es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
    if filter != '' and facet != '':
        saved_list = request.session['filters']
        saved_list.append({'term': {facet + '.keyword': filter}})
        request.session['filters'] = saved_list
    else:
        if 'filters' in request.session:
            del request.session['filters']
        request.session['filters'] = []

    page = (int(page) - 1) * 10
    if term == '*' or term == 'top10':
        result = es.search(
            index='webcontents',
            body={
                'from': page,
                'size': 10,

                'query': {
                    'bool': {
                        'must': {
                            'match_all': {}
                        },
                        'filter': {
                            'bool': {
                                'must': request.session.get('filters')
                            }
                        }
                    }
                },
                'aggs': aggregares
            }
        )
    else:
        query_body = {
            'from': page,
            'size': 10,
            'query': {
                'bool': {
                    'must': {
                        'multi_match': {
                            'query': term,
                            'fields': ['title', 'pageContetnts', 'organizations', 'topics',
                                       'people', 'workOfArt', 'files', 'locations', 'dates',
                                       'ResearchInfrastructure'],
                            'type': 'best_fields',
                            'minimum_should_match': '100%'
                        }
                    },
                    'filter': {
                        'bool': {
                            'must': request.session.get('filters')
                        }
                    }
                }
            },
            'aggs': aggregares
        }
        result = es.search(index='webcontents', body=query_body)

    lst_results = []
    lst_image_filename = []
    lst_image_url = []

    for search_result in result['hits']['hits']:
        lst_results.append(search_result['_source'])
        if searchtype == 'imagesearch':
            url = search_result['_source']['url']
            research_infrastructure = search_result['_source']['ResearchInfrastructure']
            for img in search_result['_source']['images']:
                a = urlparse(img)
                filename = os.path.basename(a.path)
                extension = os.path.splitext(filename)[1]
                filename_without_ext = os.path.splitext(filename)[0]
                if filename not in lst_image_filename:
                    lst_image_filename.append(filename)
                    image = {'imageURL': img, 'imageWebpage': url[0], 'filename': filename_without_ext,
                             'extension': extension, 'ResearchInfrastructure': research_infrastructure[0]}
                    lst_image_url.append(image)
    # ......................
    files = []
    locations = []
    people = []
    organizations = []
    work_of_art = []
    products = []
    research_infrastructure = []
    # ......................
    for search_result in result['aggregations']['ResearchInfrastructure']['buckets']:
        if (['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '' and
                search_result['key'] != 'KB'):
            ri = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            research_infrastructure.append(ri)
    # ......................
    for search_result in result['aggregations']['locations']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            loc = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            locations.append(loc)
    # ......................
    for search_result in result['aggregations']['people']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            prod = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            people.append(prod)
    # ......................
    for search_result in result['aggregations']['organizations']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            org = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            organizations.append(org)
    # ......................
    for search_result in result['aggregations']['products']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            pers = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            products.append(pers)
    # ......................
    for search_result in result['aggregations']['workOfArt']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            auth = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            work_of_art.append(auth)
    # ......................
    for search_result in result['aggregations']['files']['buckets']:
        if search_result['key'] != 'None' and search_result['key'] != 'unknown' and search_result['key'] != '':
            ext = {
                'key': search_result['key'],
                'doc_count': search_result['doc_count']
            }
            files.append(ext)
    # ......................

    facets = {
        'files': files,
        'locations': locations,
        'workOfArt': work_of_art,
        'organizations': organizations,
        'people': people,
        'products': products,
        'research_infrastructure': research_infrastructure
    }
    # envri-statics
    # print('Got %d Hits:' % result['hits']['total']['value'])
    # return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})
    num_hits = result['hits']['total']['value']

    upper_bound_page = round(np.ceil(num_hits / 10) + 1)
    if upper_bound_page > 10:
        upper_bound_page = 11

    results = {
        'facets': facets,
        'results': lst_results,
        'NumberOfHits': num_hits,
        'page_range': range(1, upper_bound_page),
        'cur_page': (page / 10 + 1),
        'searchTerm': term,
        'functionList': getAllfunctionList(request),
        'lst_image_url': lst_image_url
    }

    return results


# -----------------------------------------------------------------------------------------------------------------------
def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]


# -----------------------------------------------------------------------------------------------------------------------

def downloadCart(request):
    if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
        request.session['BasketURLs'] = []
    if not 'MyBasket' in request.session or not request.session['MyBasket']:
        request.session['MyBasket'] = []

    Webpages = []
    Datasets = []
    WebAPIs = []
    Notebooks = []

    print("download cart")

    saved_list = request.session['MyBasket']
    for item in saved_list:
        if (item['type'] == "Webpages"):
            Webpages.append({'operation': 'add', 'type': item['type'], 'title': item['title'], 'url': item['url'],
                             'id': item['id']})
        elif (item['type'] == "Datasets"):
            Datasets.append({'operation': 'add', 'type': item['type'], 'title': item['title'], 'url': item['url'],
                             'id': item['id']})
        elif (item['type'] == "WebAPIs"):
            WebAPIs.append({'operation': 'add', 'type': item['type'], 'title': item['title'], 'url': item['url'],
                            'id': item['id']})
        elif (item['type'] == "Notebooks"):
            Notebooks.append({'operation': 'add', 'type': item['type'], 'title': item['title'], 'url': item['url'],
                              'id': item['id']})

    return render(request, 'downloadCart.html',
                  {
                      "Webpages": Webpages,
                      "Datasets": Datasets,
                      "Web APIs": WebAPIs,
                      "Notebooks": Notebooks,
                  }
                  )


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


# -----------------------------------------------------------------------------------------------------------------------
def addToBasket(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)

            if (data['operation'] == 'add'):
                if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
                    request.session['BasketURLs'] = []
                if not 'MyBasket' in request.session or not request.session['MyBasket']:
                    request.session['MyBasket'] = []

                if data['url'] not in request.session['BasketURLs']:

                    saved_list = request.session['BasketURLs']
                    saved_list.append(data['url'])
                    request.session['BasketURLs'] = saved_list

                    saved_list = request.session['MyBasket']
                    saved_list.append(data)
                    request.session['MyBasket'] = saved_list

                    return JsonResponse(data)
                else:
                    print("Duplicated")
                    return JsonResponse({'status': 'Duplicated key'}, status=400)
            if (data['operation'] == 'delete'):
                if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
                    request.session['BasketURLs'] = []
                    del request.session['BasketURLs']
                if not 'MyBasket' in request.session or not request.session['MyBasket']:
                    request.session['MyBasket'] = []
                    del request.session['BasketURLs']

                saved_list = request.session['MyBasket']
                url = ""
                for item in saved_list:
                    if item['id'] == data['id']:
                        url = item['url']
                        saved_list.remove(item)
                request.session['MyBasket'] = saved_list

                saved_list = request.session['BasketURLs']
                for item in saved_list:
                    if item == url:
                        saved_list.remove(item)
                request.session['BasketURLs'] = saved_list
                return JsonResponse(data)

        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


# -----------------------------------------------------------------------------------------------------------------------
def send_feedback(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        data = json.load(request)

        es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
        index = Index('userfeedback', es)

        if not es.indices.exists(index='userfeedback'):
            index.settings(
                index={'mapping': {'ignore_malformed': True}}
            )
            index.create()
        else:
            es.indices.close(index='userfeedback')
            put = es.indices.put_settings(
                index='userfeedback',
                body={
                    "index": {
                        "mapping": {
                            "ignore_malformed": True
                        }
                    }
                })
            es.indices.open(index='userfeedback')

        res = es.index(index="userfeedback", id=uuid.uuid4(), body=data)
        es.indices.refresh(index="userfeedback")

        return JsonResponse(data)
    return JsonResponse({'status': 'Invalid request'}, status=400)
# -----------------------------------------------------------------------------------------------------------------------
