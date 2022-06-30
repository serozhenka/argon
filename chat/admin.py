from django.contrib import admin

from .models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    search_fields = ('user1__email', 'user1__username', 'user2__email', 'user2__username')


class ChatRoomMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'body', 'timestamp', 'is_read')
    search_fields = ('user__email', 'user__username')


class ChatRoomMessageBodyAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_edited')


admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatRoomMessage, ChatRoomMessageAdmin)
admin.site.register(ChatRoomMessageBody, ChatRoomMessageBodyAdmin)
