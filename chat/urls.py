from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='chat-general-page'),
    path('<str:username>/', views.chat_page, name='chat-page'),
]
