from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from blog.models import Post, Comment
from blog.pagination import ListPagination
from blog.serializers import PostSerializer, CommentSerializer, PostDetailSerializer
from blog.permissions import IsOwnerOrStaffOrReadOnly, PermissionForUpdate, ItsOwnerOrStaff


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'body']
    ordering_fields = ['created']

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrStaffOrReadOnly, PermissionForUpdate]
        elif self.action == 'add_comment':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrStaffOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'list':
            # Return queryset with status "PB"
            queryset = self.queryset.filter(status='PB')
            return queryset
        elif self.action == 'my_posts':
            # Return queryset with posts for owner
            user = self.request.user
            queryset = self.queryset.filter(author=user)
            return queryset
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        """
        List method for get all posts
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         fields=('id', 'author', 'title', 'body',
                                                 'created', 'updated'))
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Method for get post depending on the user. If it's owner - return data with fields for owner,
        else return data with fields for all users.
        """
        instance = self.get_object()
        if instance.author == self.request.user:
            serializer = PostDetailSerializer(instance, fields=('id', 'title', 'body',
                                                                'status', 'comments'),
                                              context={'request': self.request})
            return Response(serializer.data)
        else:
            serializer = PostDetailSerializer(instance, fields=('id', 'author', 'title',
                                                                'body', 'comments'),
                                              context={'request': self.request})
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """
        Action to get own posts
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = PostSerializer(page, many=True,
                                    fields=('id', 'title', 'body', 'status'))
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Action for add comment to the post
        """
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['author'] = self.request.user
            serializer.validated_data['post'] = post
            serializer.save()
            return Response({'status': 'Comment added'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()


class CommentViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = ListPagination
    permission_classes = [ItsOwnerOrStaff]

    def get_queryset(self):
        if self.action == 'my_comments':
            user = self.request.user
            queryset = self.queryset.filter(author=user)
            return queryset
        else:
            return self.queryset

    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if self.request.user.is_staff:
            serializer = self.get_serializer(instance,
                                             fields=('id', 'author', 'body',
                                                     'created', 'updated'))
        else:
            serializer = self.get_serializer(instance, fields=('id', 'body', 'created', 'updated'))
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """
        Action to get own comments
        """
        queryset = self.get_queryset()

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         fields=(
                                             'id', 'body', 'created', 'updated'
                                         ))
        return self.get_paginated_response(serializer.data)

