from django.utils.text import slugify
from rest_framework import serializers

from sakashule.apps.schools.models import School, Comment, Event, Update, Uniform, User
from sakashule.apps.profiles.models import Profile
from sakashule.apps.profiles.serializers import ProfileSerializer


class SchoolSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True, max_length=255)
    name = serializers.CharField(
        max_length=255, allow_blank=True)
    school = serializers.SerializerMethodField(read_only=True)
    about = serializers.CharField(required=False, allow_blank=True)
    history = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = School

        fields = [
            'slug',
            'name',
            'school',
            'about',
            'history',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('slug', 'school')


    def get_school(self, obj):
        serializer = ProfileSerializer(
            instance=Profile.objects.get(user=obj.school)
        )
        return serializer.data


    def create(self, validated_data):
        school = School.objects.create(**validated_data)
        return school


    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def validate_schoolname(self, data):
        if School.objects.filter(name=data):
            raise serializers.ValidationError(
                {'errors': "School name already exists"})
        return data

    def validate_user(self, data):
        if School.objects.filter(school=data):
            raise serializers.ValidationError({
                'errors': 'Only one school is allowed per user'
            })
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    body = serializers.CharField(max_length=1000)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment

        fields = ['id', 'body', 'author', 'created_at']

    def create(self, validated_data):
        Comment.objects.create(**data)

    def update(self, instance, data):
        instance.body = data.get('body', instance.body)
        instrance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    date = serializers.DateField(required=False)
    time = serializers.TimeField()
    body = serializers.CharField()

    class Meta:
        model = Event
        fields = ['event_id', 'title', 'date', 'time', 'body']


class UpdateSerializer(serializers.ModelSerializer):
    update_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    date = serializers.DateField()
    time = serializers.TimeField()
    body = serializers.CharField()

    class Meta:
        model = Update
        fields = ['update_id', 'title', 'date', 'time', 'body']


class UniformSerializer(serializers.ModelSerializer):
    image = serializers.URLField(required=False, allow_blank=False)
    title = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Uniform
        fields = ['image', 'title', 'description']
