from django.urls import path

from . import views

app_name = 'follow'

urlpatterns = [
    path('follow-action/<str:username>/', views.follow_general_view, name='follow-action'),
]
