import os

from django.urls import re_path, include
from genericpages import views

# urlpatterns = [
#     re_path(r'^someuri/', include([
#         re_path(r'^genericpages', views.genericpages, name='genericpages'),
#         re_path('', views.landingpage, name='landingpage')
#     ]))
# ]
urlpatterns = [
	#url(r'^index', views.index, name='index'),
    re_path(r'^genericpages', views.generic_pages, name='generic_pages'),
    re_path('', views.landing_page, name='landing_page'),
]