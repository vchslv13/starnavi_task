from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from social_network.models import Post, User
from social_network.serializers import PostSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def update(self, request, pk=None, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get_permissions(self):
        # allow unauthenticated users to list, retrieve and create new users
        permission = (AllowAny() if self.action in ('list', 'create', 'retrieve')
                      else IsAuthenticated())
        return [permission]


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    @action(detail=True, methods=['post'], url_name='like',
            permission_classes=[IsAuthenticated])
    def like_post(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        if post.liked_by_users.filter(pk=user.pk):
            return Response({'status': 'already liked'})
        else:
            post.liked_by_users.add(request.user)
            return Response({'status': 'like set'})

    @action(detail=True, methods=['post'], url_name='unlike',
            permission_classes=[IsAuthenticated])
    def unlike_post(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        if not post.liked_by_users.filter(pk=user.pk):
            return Response({'status': 'post was not liked'})
        else:
            post.liked_by_users.remove(request.user)
            return Response({'status': 'post unliked'})
