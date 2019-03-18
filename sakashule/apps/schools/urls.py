from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sakashule.apps.schools.views import SchoolAPIView, SearchFilterListAPIView

app_name = "schools"
router = DefaultRouter()
router.register('schools', SchoolAPIView, base_name="schools")

urlpatterns = [
    path('', include(router.urls)),
    path('schools/search_filter', SearchFilterListAPIView.as_view(), name='search-filter')
]