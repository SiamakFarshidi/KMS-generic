from django.urls import re_path

from genericpages import views

# urlpatterns = [
#     re_path(r'^someuri/', include([
#         re_path(r'^genericpages', views.genericpages, name='genericpages'),
#         re_path('', views.landingpage, name='landingpage'),
#     ])),
# ]
urlpatterns = [
	#url(r'^index', views.index, name='index'),
    re_path(r'^genericpages', views.genericpages, name='genericpages'),
    re_path('', views.landingpage, name='landingpage'),
]