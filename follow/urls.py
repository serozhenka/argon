from django.urls import path

from . import views

app_name = 'follow'

urlpatterns = [
    path('follow-user/<str:username>/', views.follow_page, name='follow-user'),
    path('unfollow-user/<str:username>/', views.unfollow_page, name='unfollow-user'),
    path('remove-follower/<str:username>/', views.remove_follower_page, name='remove-follower'),
    path(
        'cancel-following-request/<str:username>/',
        views.cancel_following_request_page,
        name='cancel-following-request'
    ),
    path(
        'accept-following-request/<str:username>/',
        views.accept_following_request_page,
        name='accept-following-request',
    ),
    path(
        'cancel-following-request/<str:username>/',
        views.decline_following_request_page,
        name='decline-following-request'
    ),
]
