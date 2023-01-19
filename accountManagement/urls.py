from django.conf.urls import include
from django.urls import re_path as url
from accountManagement import views,models
from django.conf.urls.static import static


urlpatterns = [
	#url(r'^index', views.index, name='index'),
    url(r'^login', views.login, name='login'),
]
