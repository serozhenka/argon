from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from users import views as authentication_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', authentication_views.feed_page, name='feed'),

    path('login/', authentication_views.login_page, name='login'),
    path('logout/', authentication_views.logout_page, name='logout'),
    path('register/', authentication_views.register_page, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
