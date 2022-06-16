from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),

    path('<str:username>/', views.account_page, name='account'),
    path('<str:username>/edit/', views.account_edit_page, name='account-edit'),
]
