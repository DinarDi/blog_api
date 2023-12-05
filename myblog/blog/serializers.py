from django.contrib.auth.models import User

from rest_framework import serializers

from blog.models import Post


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)


class AuthorInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for user info
    """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class PostBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common fields
    """
    author = AuthorInfoSerializer(read_only=True)


class PostSerializer(DynamicFieldsModelSerializer, PostBaseSerializer):
    """
    Serializer for posts
    """
    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'body',
                  'status', 'created', 'updated')