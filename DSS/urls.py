from django.conf.urls import include
from django.urls import re_path as url
from DSS import views,models
from django.conf.urls.static import static


urlpatterns = [
    url(r'^numberOfSolutions', views.numberOfSolutions, name='numberOfSolutions'),
    url(r'^listOfSolutions', views.listOfSolutions, name='listOfSolutions'),
    url(r'^detailedSolution', views.detailedSolution, name='detailedSolution')
]
