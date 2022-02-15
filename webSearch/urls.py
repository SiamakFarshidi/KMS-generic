from django.conf.urls import url,include
from webSearch import views,models
from django.conf.urls.static import static


urlpatterns = [
	#url(r'^index', views.index, name='index'),
    url(r'^uploadFromJsonStream', views.uploadFromJsonStream, name='uploadFromJsonStream'),
    url(r'^genericsearch', views.genericsearch, name='genericsearch'),
    url(r'^aggregates', views.aggregates, name='aggregates'),
    url(r'^addToBasket', views.addToBasket, name='addToBasket'),
    url(r'^downloadCart', views.downloadCart, name='downloadCart'),
    url(r'^sendFeedback', views.sendFeedback, name='sendFeedback'),
]
