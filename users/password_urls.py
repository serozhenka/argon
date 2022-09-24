from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .constants import DashboardPages


urls = [
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='password_reset/password_change.html',
        success_url=reverse_lazy('account:password_change_done'),
        extra_context={'page_name': DashboardPages.PASSWORD},
    ), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='password_reset/password_change_done.html'
    ), name='password_change_done'),


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
]