from django.contrib import admin

from .models import Post, PostImage, PostLike, CommentLike, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'likes_count', 'id', 'created')
    search_fields = ('user__email', 'user__username')

    def likes_count(self, obj):
        return PostLike.objects.filter(post=obj).count()


class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'post_user', 'id')
    search_fields = ('post__user__username', 'post__user__email')

    def post_user(self, obj):
        return obj.post.user


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'is_liked')
    search_fields = ('user__email', 'user__username', 'post__id')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'likes_count', 'created')
    search_fields = ('user__email', 'user__username', 'post')

    def likes_count(self, obj):
        return obj.commentlike_set.count()
        # return CommentLike.objects.filter(comment=obj).count()

class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'is_liked')
    search_fields = ('user__email', 'user__username', 'comment__id')


admin.site.register(Post, PostAdmin)
admin.site.register(PostImage, PostImageAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
