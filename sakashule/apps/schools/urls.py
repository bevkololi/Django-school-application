from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sakashule.apps.schools.views import SchoolAPIView, SearchFilterListAPIView, EventAPIView, UpdateAPIView, EventsUpdateDestroy, UpdatesUpdateDestroy, UniformAPIView, UniformUpdateDestroy

app_name = "schools"
router = DefaultRouter()
router.register('schools', SchoolAPIView, base_name="schools")

urlpatterns = [
    path('', include(router.urls)),
    path('schools/search_filter', SearchFilterListAPIView.as_view(), name='search-filter'),
    path('schools/<slug>/events/', EventAPIView.as_view(), name='events'),
    path('schools/<slug>/events/<pk>', EventsUpdateDestroy.as_view(), name='event'),
    path('schools/<slug>/updates/', UpdateAPIView.as_view(), name='updates'),
    path('schools/<slug>/updates/<pk>', UpdatesUpdateDestroy.as_view(), name='update'),
    path('schools/<slug>/uniforms/', UniformAPIView.as_view(), name='uniforms'),
    path('schools/<slug>/uniforms/<pk>', UniformUpdateDestroy.as_view(), name='uniform')
]
