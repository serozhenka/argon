from django.conf import settings
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path('followers/<str:username>/', views.FollowersApiView.as_view(), name='api-followers-list'),
    path('following/<str:username>/', views.FollowingApiView.as_view(), name='api-following-list'),

    path('posts/', views.PostApiView.as_view(), name='api-post-list'),
    path('posts/<str:username>/', views.PostUserApiView.as_view(), name='api-post-list-by-user'),
]

