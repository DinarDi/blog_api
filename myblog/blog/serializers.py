from django.contrib.auth.models import User

from rest_framework import serializers

from blog.models import Post, Comment
from blog.pagination import ListPagination


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


class CommentSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for comments
    """
    author = AuthorInfoSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'created', 'updated')


class PostDetailSerializer(DynamicFieldsModelSerializer, PostBaseSerializer):
    """
    Serializer with detail info for posts
    """
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'body',
                  'status', 'created', 'updated', 'comments')

    def get_comments(self, obj):
        """
        Pagination for nested comments in post
        """
        comments = Comment.objects.filter(post=obj)
        paginator = ListPagination()
        if self.context.get('request', None):
            page = paginator.paginate_queryset(comments,
                                               request=self.context['request'])
            serializer = CommentSerializer(page, many=True)
            return serializer.data

        serializer = CommentSerializer(comments, many=True)
        return serializer.data
