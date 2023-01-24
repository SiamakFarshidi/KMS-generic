from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
# -------------------------------------------------------------------------------------------------------------
def listOfSolutions(request):
    return JsonResponse({"hits": 'numHits', "solutions": {}})


# -------------------------------------------------------------------------------------------------------------
@csrf_exempt
def numberOfSolutions(request):
    return JsonResponse({'hits': 'numHits', "solutions": {}})


# -------------------------------------------------------------------------------------------------------------
def detailedSolution(request):
    return JsonResponse({"hits": 'numHits', "solutions": {}})
# -------------------------------------------------------------------------------------------------------------
