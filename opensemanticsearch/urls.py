from django.conf.urls import include, url

from django.contrib import admin

from django.contrib import auth

from django.urls import path


urlpatterns = [
	path('admin/', admin.site.urls),
	url(r'^dataset_elastic/', include(('dataset_elastic.urls', 'dataset_elastic'), namespace="dataset_elastic")),
	url(r'^notebookSearch/', include(('notebookSearch.urls', 'notebookSearch'), namespace="notebookSearch")),
	url(r'^webSearch/', include(('webSearch.urls', 'webSearch'), namespace="webSearch")),
	url(r'^genericpages/', include(('genericpages.urls', 'genericpages'), namespace="genericpages")),
	url(r'^webAPI/', include(('webAPI.urls', 'webAPI'), namespace="webAPI")),
	url(r'^DSS/', include(('DSS.urls', 'DSS'), namespace="DSS")),
	url(r'^accountManagement/', include(('accountManagement.urls', 'accountManagement'), namespace="accountManagement")),
	path('', include(('genericpages.urls', 'genericpages'), namespace="genericpages")),

]
