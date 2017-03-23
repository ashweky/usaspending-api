from django.conf.urls import url

from usaspending_api.accounts.views import federal as views

# bind ViewSets to URLs
federal_list = views.FederalAccountViewSet.as_view(
    {'get': 'list', 'post': 'list'})
federal_detail = views.FederalAccountViewSet.as_view(
    {'get': 'retrieve', 'post': 'retrieve'})

urlpatterns = [
    url(r'^$', federal_list),
    url(r'(?P<pk>[0-9]+)/$', federal_detail),
]
