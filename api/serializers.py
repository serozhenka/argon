from django.db.models import Q
from rest_framework import serializers

from chat.models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody
from notifications.models import Notification
from post.models import Post, PostImage, PostLike, Comment, CommentLike
from users.models import Account

class AccountSerializer(serializers.ModelSerializer):
    is_following_by_request_user = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['username', 'name', 'bio', 'image', 'is_public', 'is_following_by_request_user', 'online']

    def get_is_following_by_request_user(self, obj):
        return self.context['request'].user.following.is_following(obj)


class SimpleAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'name', 'image', 'online']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image', 'order']

class CommentSerializer(serializers.ModelSerializer):
    user = SimpleAccountSerializer()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['user', 'description', 'is_liked_by_user', 'likes_count', 'id', 'timestamp']

    def get_is_liked_by_user(self, obj):
        try:
            return CommentLike.objects.get(
                user=self.context['request'].user,
                comment=obj,
            ).is_liked
        except CommentLike.DoesNotExist:
            return False


class PostSerializer(serializers.ModelSerializer):
    user = SimpleAccountSerializer()
    post_images = PostImageSerializer(many=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'description', 'post_images', 'is_liked_by_user', 'likes_count', 'is_edited', 'id', 'timestamp']

    def get_is_liked_by_user(self, obj):
        try:
            return PostLike.objects.get(
                user=self.context['request'].user,
                post=obj,
            ).is_liked
        except PostLike.DoesNotExist:
            return False

class ChatRoomBodySerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoomMessageBody
        fields = ['text', 'image', 'is_edited']

class ChatRoomMessageSerializer(serializers.ModelSerializer):
    user = SimpleAccountSerializer()
    body = ChatRoomBodySerializer()

    class Meta:
        model = ChatRoomMessage
        fields = ['user', 'body', 'timestamp', 'is_read']


class ChatRoomSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    notification = serializers.SerializerMethodField()
    last_message = ChatRoomMessageSerializer()

    class Meta:
        model = ChatRoom
        fields = ['other_user', 'last_message', 'notification']

    def get_other_user(self, obj):
        other_user = obj.other_user(self.context['request'].user)
        return SimpleAccountSerializer(other_user).data

    def get_notification(self, obj):
        me = self.context['request'].user
        other_user = obj.other_user(me)
        notification = Notification.objects.filter(sender=other_user, receiver=me, content_type__model='chatroommessage').first()
        return NotificationSerializer(notification).data

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['receiver', 'sender', 'is_read', 'timestamp', 'id']