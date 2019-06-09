from social_network.models import Post, User
from rest_framework.serializers import HyperlinkedModelSerializer


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'full_name', 'date_joined', 'email',
                  'password')
        read_only_fields = ('date_joined',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PostSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('url', 'id', 'text', 'author', 'creation_datetime',
                  'liked_by_users',)
        read_only_fields = ('liked_by_users', 'creation_datetime',)
