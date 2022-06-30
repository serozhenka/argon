from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('u/', include('users.urls')),
    path('follow/', include('follow.urls')),
    path('api/', include('api.urls')),
    path('chat/', include('chat.urls')),

    path('', include('post.urls')),
    path('user-search/', users_views.user_search_page, name='user-search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
