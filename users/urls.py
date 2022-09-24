from django.urls import path, re_path

from . import views
from .password_urls import urls as password_urls

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('logout/', views.LogoutPageView.as_view(), name='logout'),

    *password_urls,

    path('edit/account', views.AccountEditPageView.as_view(), name='account-edit'),
    path('edit/privacy-security/', views.AccountPrivacySecurityView.as_view(), name='privacy-security'),
    path(
        'edit/privacy-security/status-change/',
        views.ChangeUserPrivacyStatusView.as_view(), name='privacy-security-status-change',
    ),
    path('edit/crop-image/', views.CropImageView.as_view(), name='crop-image'),

    path('<str:username>/', views.AccountPageView.as_view(), name='account'),

    path('<str:username>/followers/', views.AccountFollowersView.as_view(), name='account-followers'),
    path('<str:username>/followings/', views.AccountFollowingsView.as_view(), name='account-following'),

    re_path(r'^$', views.LoginPageView.as_view()),
]
