from django.urls import path

from . import views

app_name = 'follow'

urlpatterns = [
    path('follow-action/<str:username>/', views.follow_general_view, name='follow-action'),

    # path('follow-user/<str:username>/', views.follow_general_view, name='follow-user'),
    # path('follow-user/<str:username>/', views.follow_general_view, name='follow-user'),
    # path('unfollow-user/<str:username>/', views.follow_general_view, name='unfollow-user'),
    # path('remove-follower/<str:username>/', views.follow_general_view, name='remove-follower'),
    # path(
    #     'cancel-following-request/<str:username>/',
    #     views.follow_general_view,
    #     name='cancel-following-request'
    # ),
    # path(
    #     'accept-following-request/<str:username>/',
    #     views.follow_general_view,
    #     name='accept-following-request',
    # ),
    # path(
    #     'cancel-following-request/<str:username>/',
    #     views.follow_general_view,
    #     name='decline-following-request'
    # ),
]
