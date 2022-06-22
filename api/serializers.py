from rest_framework import serializers

from users.models import Account
from post.models import Post, PostImage


class AccountSerializer(serializers.ModelSerializer):
    is_following_by_request_user = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['username', 'name', 'bio', 'image', 'is_public', 'is_following_by_request_user']

    def get_is_following_by_request_user(self, obj):
        return self.context['request'].user.following.is_following(obj)


class SimpleAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'name', 'image']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image', 'order']

class PostSerializer(serializers.ModelSerializer):
    user = SimpleAccountSerializer()
    post_images = PostImageSerializer(many=True)

    class Meta:
        model = Post
        fields = ['user', 'description', 'post_images', 'likes_count', 'is_edited', 'created']
