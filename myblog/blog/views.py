from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from blog.models import Post
from blog.serializers import PostSerializer
from blog.permissions import IsOwnerOrStaffOrReadOnly, PermissionForUpdate


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

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
        else:
            return self.queryset

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()
