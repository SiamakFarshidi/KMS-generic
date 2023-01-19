from django.conf.urls import include
from django.urls import re_path as url
from webAPI import views,models
from django.conf.urls.static import static


urlpatterns = [
    url(r'^indexingpipeline', views.indexingpipeline, name='indexingpipeline'),
    url(r'^genericsearch', views.genericsearch, name='genericsearch'),
    url(r'^aggregates', views.aggregates, name='aggregates')
]
