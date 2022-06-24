from django.http import Http404
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from .permissions import FollowingPrivatePermission
from .serializers import AccountSerializer, PostSerializer, CommentSerializer
from follow.models import Followers, Following
from post.models import Post, Comment
from users.models import Account

class FollowersApiView(generics.ListAPIView):
    serializer_class = AccountSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            user = Account.objects.get(username=self.kwargs.get('username'))
        except Account.DoesNotExist:
            raise Http404
        return Followers.objects.get(user=user).users_followers.all()

class FollowingApiView(generics.ListAPIView):
    serializer_class = AccountSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            user = Account.objects.get(username=self.kwargs.get('username'))
        except Account.DoesNotExist:
            raise Http404
        return Following.objects.get(user=user).users_following.all()

class PostUserApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [FollowingPrivatePermission]

    def get_queryset(self):
        try:
            user = Account.objects.get(username=self.kwargs.get('username'))
        except Account.DoesNotExist:
            raise Http404
        return Post.objects.filter(user=user).order_by('-created')

class PostApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        following_users = Following.objects.get(user=self.request.user).users_following.all()
        return Post.objects.filter(user__in=following_users).order_by('-created')

class PostCommentsApiView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [FollowingPrivatePermission]

    def get_queryset(self):
        try:
            post = Post.objects.get(id=self.kwargs.get('post_id'))
        except Post.DoesNotExist:
            raise Http404

        return Comment.objects.filter(post=post).order_by('-created')