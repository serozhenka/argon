from django.contrib import admin
from django.conf import settings
from django.urls import path

from . import views

app_name = 'post'

urlpatterns = [
    path('', views.feed_page, name='feed'),
    path('posts/add/', views.post_add_page, name='post-add'),
]

