from rest_framework.viewsets import ModelViewSet
from social_network.models import Post, User
from social_network.serializers import PostSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
