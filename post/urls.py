from django.contrib import admin
from django.conf import settings
from django.urls import path

from . import views

app_name = 'post'

urlpatterns = [
    path('', views.feed_page, name='feed'),
    path('p/add/', views.post_add_page, name='post-add'),
    path('p/<str:post_id>/', views.post_page, name='post-page'),
    path('p/<str:post_id>/like/', views.post_like_page, name='post-like'),
]

