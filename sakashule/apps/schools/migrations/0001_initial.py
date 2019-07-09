# Generated by Django 2.1.7 on 2019-05-23 10:32

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('body', models.TextField()),
                ('author', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='profiles.Profile')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at', '-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateField(default=datetime.date(2019, 5, 23))),
                ('time', models.TimeField()),
                ('body', models.TextField(default='Update Event')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at', '-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('about', models.CharField(default="Update school's description", max_length=400)),
                ('history', models.TextField(default='Update school history')),
                ('fee_structure', models.FileField(upload_to='')),
                ('results', models.FileField(upload_to='')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schools', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at', '-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Uniform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.URLField(default='')),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uniforms', to='schools.School')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at', '-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateField(default=datetime.date(2019, 5, 23))),
                ('time', models.TimeField(default=datetime.time(10, 32, 9, 515473))),
                ('body', models.TextField(default='Update Event')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='schools.School')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at', '-id'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='event',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='schools.School'),
        ),
        migrations.AddField(
            model_name='comment',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='schools.School'),
        ),
    ]
