from rest_framework import serializers
from .models import Task, Tasklist, Tag
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    tasklists = serializers.PrimaryKeyRelatedField(many=True,
                                                   queryset=Tasklist.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'tasklists', 'shared_lists')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'completed', 'priority',
                  'date_created', 'due_date', 'tags')


class TasklistSerializer(serializers.ModelSerializer):
    tasks = serializers.StringRelatedField(many=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Tasklist
        fields = ('id', 'name', 'tasks', 'owner', 'shared')
