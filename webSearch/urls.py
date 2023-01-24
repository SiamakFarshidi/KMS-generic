from django.conf.urls import include
from django.urls import re_path

from webSearch import views

urlpatterns = [
    # url(r'^index', views.index, name='index'),
    re_path(r'^uploadFromJsonStream', views.upload_from_json_stream, name='uploadFromJsonStream'),
    re_path(r'^genericsearch', views.generic_search, name='genericsearch'),
    re_path(r'^aggregates', views.aggregates, name='aggregates'),
    re_path(r'^addToBasket', views.addToBasket, name='addToBasket'),
    re_path(r'^downloadCart', views.downloadCart, name='downloadCart'),
    re_path(r'^sendFeedback', views.send_feedback, name='sendFeedback'),
]

# urlpatterns = [
#     re_path(r'^someuri/', include([
#         # url(r'^index', views.index, name='index'),
#         re_path(r'^uploadFromJsonStream', views.uploadFromJsonStream, name='uploadFromJsonStream'),
#         re_path(r'^genericsearch', views.genericsearch, name='genericsearch'),
#         re_path(r'^aggregates', views.aggregates, name='aggregates'),
#         re_path(r'^addToBasket', views.addToBasket, name='addToBasket'),
#         re_path(r'^downloadCart', views.downloadCart, name='downloadCart'),
#         re_path(r'^sendFeedback', views.sendFeedback, name='sendFeedback'),
#     ])),
# ]
