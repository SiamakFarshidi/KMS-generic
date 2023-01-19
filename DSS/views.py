from django.shortcuts import render
import json
import os
from django.http import JsonResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
#-------------------------------------------------------------------------------------------------------------
def listOfSolutions(request):

    return JsonResponse({"hits": numHits,"solutions": {}})
#-------------------------------------------------------------------------------------------------------------
@csrf_exempt
def numberOfSolutions(request):

    return JsonResponse({'hits': numHits, "solutions":{}})
#-------------------------------------------------------------------------------------------------------------
def detailedSolution(request):
    return JsonResponse({"hits": numHits,"solutions": {}})
#-------------------------------------------------------------------------------------------------------------
