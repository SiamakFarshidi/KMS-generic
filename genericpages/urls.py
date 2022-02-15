from django.conf.urls import url,include
from genericpages import views,models
from django.conf.urls.static import static
urlpatterns = [
	#url(r'^index', views.index, name='index'),
    url(r'^genericpages', views.genericpages, name='genericpages'),
    url('', views.landingpage, name='landingpage'),
]
