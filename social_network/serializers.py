from social_network.models import Post, User
from rest_framework.serializers import HyperlinkedModelSerializer


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'full_name', 'date_joined', 'email',)


class PostSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('url', 'id', 'text', 'author', 'creation_datetime',
                  'liked_by_users',)
