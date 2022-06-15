from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),


    path('account/', include('users.urls')),
    path('', users_views.feed_page, name='feed'),
    # path('<str:pk>/', users_views.login_page, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
