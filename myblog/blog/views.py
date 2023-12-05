from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from blog.models import Post
from blog.pagination import ListPagination
from blog.serializers import PostSerializer
from blog.permissions import IsOwnerOrStaffOrReadOnly, PermissionForUpdate


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListPagination

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrStaffOrReadOnly, PermissionForUpdate]
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
        queryset = self.get_queryset()

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         fields=('id', 'author', 'title', 'body',
                                                 'created', 'updated'))
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """
        Action to get own posts
        """
        queryset = self.get_queryset()

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = PostSerializer(page, many=True,
                                    fields=('id', 'title', 'body', 'status'))
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()
