from django.conf.urls import url,include
from notebookSearch import views,models
from django.conf.urls.static import static


urlpatterns = [
    url(r'^genericsearch', views.genericsearch, name='genericsearch'),
    url(r'^github_index_pipeline', views.github_index_pipeline, name='github_index_pipeline')



]


