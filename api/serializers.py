from rest_framework import serializers

from users.models import Account
from post.models import Post, PostImage, PostLike


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
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'description', 'post_images', 'is_liked_by_user', 'likes_count', 'is_edited', 'id', 'created']

    def get_is_liked_by_user(self, obj):
        try:
            return PostLike.objects.get(
                user=self.context['request'].user,
                post=obj,
            ).is_liked
        except PostLike.DoesNotExist:
            return False