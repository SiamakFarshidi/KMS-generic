from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
# Create your views here.

def login(request):
    es = Elasticsearch("http://localhost:9200")
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
