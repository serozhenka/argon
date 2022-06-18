from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from .serializers import AccountSerializer
from follow.models import Followers, Following
from users.models import Account

class FollowersApiView(generics.ListAPIView):
    serializer_class = AccountSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = Account.objects.get(username=self.kwargs.get('username'))
        return Followers.objects.get(user=user).users_followers.all()

class FollowingApiView(generics.ListAPIView):
    serializer_class = AccountSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = Account.objects.get(username=self.kwargs.get('username'))
        return Following.objects.get(user=user).users_following.all()