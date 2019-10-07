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

from sakashule.apps.schools.models import School, Comment, Event, Update, Uniform
from sakashule.apps.schools.serializers import SchoolSerializer, CommentSerializer, EventSerializer, UpdateSerializer, UniformSerializer
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
        serializer.validate_user(request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=request.user)

        profile = Profile.objects.filter(user=request.user).first()
        prof_data = {'slug': serializer.data['slug']}
        prof_serializer = ProfileSerializer(profile, data=prof_data, partial=True)
        prof_serializer.is_valid(raise_exception=True)
        prof_serializer.save()


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

        profile = Profile.objects.filter(user=request.user).first()
        prof_data = {'slug': serializer.data['slug']}
        prof_serializer = ProfileSerializer(profile, data=prof_data, partial=True)
        prof_serializer.is_valid(raise_exception=True)
        prof_serializer.save()


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


class EventAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('event', 'events')
    lookup_url_kwarg = 'slug'
    lookup_field = 'school__slug'

    def create(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            data=request.data.get('event', {}))
        serializer.is_valid(raise_exception= True)
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        events = Event.objects.filter(school__slug=slug)
        page = self.paginate_queryset(events)
        serializer = self.serializer_class(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)


class EventsUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly,
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('event', 'events')
    lookup_url_kwarg = 'pk'

    def update(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            message = {"error": "Event with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        event = Event.objects.filter(pk=pk).first()
        serializer = self.serializer_class(
            event, data=request.data.get('event', {}), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            message = {"error": "Event with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)
        event = Event.objects.filter(pk=pk).first()
        event.delete()
        return Response({'message': 'The event has been deleted'})



class UpdateAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('update', 'updates')
    lookup_url_kwarg = 'slug'
    lookup_field = 'school__slug'

    def create(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            data=request.data.get('update', {}))
        serializer.is_valid(raise_exception= True)
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        events = Update.objects.filter(school__slug=slug)
        page = self.paginate_queryset(events)
        serializer = self.serializer_class(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    
class UpdatesUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly,
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('update', 'updates')
    lookup_url_kwarg = 'pk'

    def update(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            update = Update.objects.get(pk=pk)
        except Update.DoesNotExist:
            message = {"error": "Update with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        update = Update.objects.filter(pk=pk).first()
        serializer = self.serializer_class(
            update, data=request.data.get('update', {}), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            update = Update.objects.get(pk=pk)
        except Update.DoesNotExist:
            message = {"error": "Update with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)
        update = Update.objects.filter(pk=pk).first()
        update.delete()
        return Response({'message': 'The update has been deleted'})


class UniformAPIView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Uniform.objects.all()
    serializer_class = UniformSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('uniform', 'uniforms')
    lookup_url_kwarg = 'slug'
    lookup_field = 'school__slug'

    def create(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            data = {"errors": "This school does not exist!"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        uniforms = Uniform.objects.filter(school__slug=slug)
        page = self.paginate_queryset(uniforms)
        serializer = self.serializer_class(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)


class UniformUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Uniform.objects.all()
    serializer_class = UniformSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsSchoolOwnerOrReadOnly,
    )
    renderer_classes = (BaseJSONRenderer,)
    pagination_class = StandardResultsSetPagination
    renderer_names = ('uniform', 'uniforms')
    lookup_url_kwarg = 'pk'

    def update(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            uniform = Uniform.objects.get(pk=pk)
        except Uniform.DoesNotExist:
            message = {"error": "Update with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)

        uniform = Uniform.objects.filter(pk=pk).first()
        serializer = self.serializer_class(
            uniform, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            return Response({
                'error': 'School does not exist'
            }, status.HTTP_404_NOT_FOUND)
        try:
            pk = self.kwargs.get('pk')
            uniform = Uniform.objects.get(pk=pk)
        except Uniform.DoesNotExist:
            message = {"error": "Update with this ID does not exist"}
            return Response(message, status.HTTP_404_NOT_FOUND)
        uniform = Uniform.objects.filter(pk=pk).first()
        uniform.delete()
        return Response({'message': 'The uniform has been deleted'})


class SchoolFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='exact')
    username = filters.CharFilter(
        field_name='school__username', lookup_expr='exact')

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
