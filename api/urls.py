from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('followers/<str:username>/', views.FollowersApiView.as_view(), name='api-followers-list'),
    path('following/<str:username>/', views.FollowingApiView.as_view(), name='api-following-list'),
]

