from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from users.views import UserSearchView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('u/', include('users.urls')),
    path('follow/', include('follow.urls')),
    path('api/', include('api.urls')),
    path('chat/', include('chat.urls')),
    path('', include('post.urls')),
    path('search/', UserSearchView.as_view(), name='user-search'),

    path('celery-progress/', include('celery_progress.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
