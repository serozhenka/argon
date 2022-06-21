from rest_framework import serializers

from follow.models import Followers
from users.models import Account


class AccountSerializer(serializers.ModelSerializer):
    is_following_by_request_user = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['username', 'name', 'bio', 'image', 'is_public', 'is_following_by_request_user']

    def get_is_following_by_request_user(self, obj):
        return self.context['request'].user.following.is_following(obj)
