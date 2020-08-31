from django.urls import path
from django.conf.urls import url, include

from .views.login import LoginViewSet
from .views.logout import LogoutView
from .views.movies import MoviesViewSet

""" User login/ add/ logout profile urls"""

urlpatterns = [
    url(r'^login/$', LoginViewSet.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
]

# Movies urls
urlpatterns += [
    url(r'^movies/$', MoviesViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^movies/(?P<movie_id>.+)/$',
        MoviesViewSet.as_view({'get': 'retrieve', 'delete': 'delete', 'put': 'partial_update'})),
]