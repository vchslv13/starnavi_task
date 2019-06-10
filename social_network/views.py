from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from social_network.models import Post, User
from social_network.serializers import PostSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        # allow unauthenticated users to list, retrieve and create new users
        permission = (AllowAny() if self.action in ('list', 'create', 'retrieve')
                      else IsAuthenticated())
        return [permission]


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
