from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from redis import Redis
from rq import Queue

from social_network.models import Post, User
from social_network.serializers import PostSerializer, UserSerializer
from social_network.utils import verify_email


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            user = User.objects.get(email=request.data['email'])
            q = Queue(connection=Redis())
            q.enqueue(verify_email, user, settings.EMAILHUNTER_API_KEY)
        return response

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

    def update(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        # allow changing the post only by it's author
        if post.author == request.user:
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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
