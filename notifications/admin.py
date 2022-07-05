from django.contrib import admin

from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['receiver', 'sender', 'action_name', 'content_type', 'object_id', 'id']
    search_fields = ['receiver__username', 'receiver__email']

admin.site.register(Notification, NotificationAdmin)
