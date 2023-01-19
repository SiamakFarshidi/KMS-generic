from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
import  os
# Create your views here.


elasticsearch_url = os.environ['ELASTICSEARCH_URL']
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

def login(request):
    es = Elasticsearch(elasticsearch_url,http_auth=[elasticsearch_username, elasticsearch_password])
    index = Index('accountmanagement', es)

    try:
        username = request.GET['username']
    except:
        username = ''
    try:
        password = request.GET['password']
    except:
        password = ''


    if not es.indices.exists(index='accountmanagement'):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
        res = es.index(index="accountmanagement", id= id, body={"username":"admin@uva.nl", "password":"a!@$Ss234hjk"})
    else:
        es.indices.close(index='accountmanagement')
        put = es.indices.put_settings(
            index='accountmanagement',
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index='accountmanagement')


    user_request = "some_param"
    query_body = {
        "size" : 1,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "username": username
                        }
                    },
                    {
                        "match": {
                            "password": password
                        }
                    }
                ]
            }
        }
    }
    result = es.search(index="accountmanagement", body=query_body)
    print(result)
    return render(request,'login.html',{"username": username, "password":password})
