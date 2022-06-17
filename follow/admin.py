from django.contrib import admin

from .models import Followers, Following, FollowingRequest

class FollowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'following_count')
    search_fields = ('user__email', 'user__username')

    def following_count(self, obj):
        return len(obj.users_following.all())

    following_count.short_description = 'Following Count'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).prefetch_related('users_following')


class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'followers_count')
    search_fields = ('user__email', 'user__username')

    def followers_count(self, obj):
        return len(obj.users_followers.all())

    followers_count.short_description = 'Followers Count'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).prefetch_related('users_followers')


class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_active', 'created')
    search_fields = ('sender__email', 'sender__username', 'receiver__email', 'receiver__username')


admin.site.register(Following, FollowingAdmin)
admin.site.register(Followers, FollowerAdmin)
admin.site.register(FollowingRequest, FollowRequestAdmin)