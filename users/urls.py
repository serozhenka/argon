from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),

    # Password reset feature
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset/password_reset_form.html',
        subject_template_name='password_reset/password_reset_subject.txt',
        email_template_name='password_reset/password_reset_email.html',
        html_email_template_name='password_reset/password_reset_email.html',
        success_url=reverse_lazy('account:password_reset_done'),
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset/password_reset_done.html'
    ), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset/password_reset_confirm.html',
        success_url=reverse_lazy('account:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset/password_reset_complete.html'
    ), name='password_reset_complete'),
    # End of password reset feature

    path('<str:username>/', views.account_page, name='account'),
    path('<str:username>/edit/', views.account_edit_page, name='account-edit'),
    path('<str:username>/edit/crop-image/', views.crop_image, name='crop-image'),
]
