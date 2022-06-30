from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='chat-general-page'),
    path('r/<str:room_id>/', views.chat_page, name='chat-page'),
]
