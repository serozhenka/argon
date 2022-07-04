from django.contrib import admin

from .models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'last_message')
    search_fields = ('user1__email', 'user1__username', 'user2__email', 'user2__username')


class ChatRoomMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'body', 'timestamp', 'is_read')
    search_fields = ('user__email', 'user__username', 'body__id')


class ChatRoomMessageBodyAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_sliced', 'is_edited')

    def text_sliced(self, obj):
        return obj.text[0:50]


admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatRoomMessage, ChatRoomMessageAdmin)
admin.site.register(ChatRoomMessageBody, ChatRoomMessageBodyAdmin)
