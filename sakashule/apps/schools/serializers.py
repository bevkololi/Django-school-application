from django.utils.text import slugify
from rest_framework import serializers

from sakashule.apps.schools.models import School, Comment
from sakashule.apps.profiles.models import Profile
from sakashule.apps.profiles.serializers import ProfileSerializer


class SchoolSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True, max_length=255)
    name = serializers.CharField(
        required=True,
        max_length=255,
        allow_blank=False,
        error_messages={
            'blank': 'School must have a name',
            'required': 'School must have a name',
            'max_length': 'School name cannot exceed 255 characters'
        })
    school = serializers.SerializerMethodField(read_only=True)
    about = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'Include something about the school',
            'required': 'Include something about the school'
        })
    history = serializers.CharField(
        allow_blank=False,
        error_messages={
            'blank': 'Include the school\'s history',
            'required': 'Include the school\'s history'
        })
    fee_structure = serializers.FileField()
    events = serializers.FileField()
    updates = serializers.FileField()
    uniforms = serializers.URLField()
    location = serializers.CharField()
    results = serializers.FileField()
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
            'fee_structure',
            'events',
            'updates',
            'uniforms',
            'location',
            'results',
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
                {"name": ["School name already exists"]})
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
