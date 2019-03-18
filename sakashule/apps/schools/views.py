from django.utils.text import slugify
from rest_framework import status, viewsets, generics
from rest_framework import mixins
from django.contrib.postgres.fields.jsonb import KeyTransform

from django.db import models
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView, ListCreateAPIView, UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

from sakashule.apps.schools.models import School, Comment
from sakashule.apps.schools.serializers import SchoolSerializer, CommentSerializer
from sakashule.apps.authentication.models import User
from sakashule.apps.authentication.serializers import UserSerializer
from sakashule.apps.core.renderers import BaseJSONRenderer
from sakashule.apps.schools.permissions import IsNotSchoolOwner, IsSchoolOwnerOrReadOnly
from sakashule.apps.profiles.models import Profile
from sakashule.apps.profiles.serializers import ProfileSerializer
from sakashule.apps.schools.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter


class SchoolAPIView(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly
    )
    renderer_classes = (BaseJSONRenderer,)
    queryset = School.objects.all()
    renderer_names = ('school', 'schools')
    serializer_class = SchoolSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        school = request.data.get('school', {})
        serializer = self.serializer_class(data=school, partial=True)
        serializer.validate_schoolname(school['name'])
        serializer.is_valid(raise_exception=True)
        serializer.save(school=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        slug = kwargs['slug']

        school = School.objects.filter(slug=slug).first()
        if school is None:
            return Response({
                'errors': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        elif not school.school == request.user:
            return Response({
                'errors': 'You are not allowed to modify these details'
            })
        serializer = self.serializer_class(
            school, data=request.data.get('school', {}), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=request.user)
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        slug = kwargs['slug']

        school = School.objects.filter(slug=slug).first()
        if school is None:
            return Response({
                'errors': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            school, context={'request': request}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        schools = School.objects.all()

        page = self.paginate_queryset(schools)
        serializer = self.serializer_class(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(self, request, *args, **kwargs)

        return Response({'message': 'The school has successfully been deleted.'})


class SchoolFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='exact')
    username = filters.CharFilter(field_name='school__username', lookup_expr='exact')
    
    class Meta:
        model = School
        fields = ['name', 'username']

class SearchFilterListAPIView(ListAPIView):
    serializer_class = SchoolSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (BaseJSONRenderer,)
    renderer_names = ("school", "schools",)
    queryset = School.objects.all()
    pagination_class = StandardResultsSetPagination

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = SchoolFilter
    search_fields = ('name', 'school__username')
    ordering_fields = ('name', 'school__username')
