import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core import files
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView

from .constants import DashboardPages
from .forms import LoginForm, RegisterForm, AccountEditForm
from .models import Account
from .utils import save_temp_profile_image_from_base64String, crop_image_from_url
from follow.models import Following, Followers, FollowingRequest
from post.models import Post


class LoginPageView(FormView):
    form_class = LoginForm
    template_name = 'users/login_register.html'
    success_url = reverse_lazy('post:feed')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'page': 'login'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return self.form_valid(form)
        return render(request, self.template_name, {'form': form, 'page': 'login'})


class RegisterPageView(FormView):
    form_class = RegisterForm
    template_name = 'users/login_register.html'
    success_url = reverse_lazy('post:feed')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'page': 'register'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return self.form_valid(form)
        return render(request, self.template_name, {'form': form, 'page': 'register'})


class LogoutPageView(FormView):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.AUTH_LOGIN_ROUTE)


class AccountPageView(DetailView):
    context_object_name = 'account'
    lookup_url_kwarg = 'username'
    model = Account
    template_name = 'users/account.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()

        self.account = get_object_or_404(
            klass=queryset,
            **{self.lookup_url_kwarg: self.kwargs.get(self.lookup_url_kwarg)}
        )

    def get_context_data(self, **kwargs):
        context = {}
        user_following_model = Following.objects.get(user=self.request.user)
        user_followers_model = Followers.objects.get(user=self.request.user)

        if not self.request.user == self.account:
            incoming_request = FollowingRequest.objects.filter(sender=self.account, receiver=self.request.user)
            if incoming_request.exists():
                context['incoming_request'] = incoming_request.is_active

            outgoing_request = FollowingRequest.objects.filter(sender=self.request.user, receiver=self.account)
            if outgoing_request.exists():
                context['outgoing_request'] = outgoing_request.is_active

            context['is_following'] = user_following_model.is_following(self.account)
            context['is_followed'] = user_followers_model.is_follower(self.account)

        context['following_count'] = user_following_model.count()
        context['followers_count'] = user_followers_model.count()
        context['account'] = self.account
        context["posts_count"] = Post.objects.filter(user=self.account, is_posted=True).count()

        return context


class AccountEditPageView(FormView):
    form_class = AccountEditForm
    template_name = 'users/edit_account.html'
    success_url = reverse_lazy('account:account-edit')

    def get_context_data(self, **kwargs):
        return {
            "account": self.request.user,
            "page_name": DashboardPages.EDIT_PROFILE,
            "DATA_UPLOAD_MAX_MEMORY_SIZE": settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = self.form_class(instance=self.request.user)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = AccountEditForm(request.POST, instance=self.request.user)
        if form.is_valid():
            form.save()
            return self.form_valid(form)

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


class AccountPrivacySecurityView(TemplateView):
    template_name = 'users/privacy_and_security.html'

    def get_context_data(self, **kwargs):
        return {
            "account": self.request.user,
            "page_name": DashboardPages.PRIVACY_AND_SECURITY,
        }


class ChangeUserPrivacyStatusView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({'response_result': 'error', 'details': 'GET not allowed'})

    def post(self, request, *args, **kwargs):
        is_public = request.POST.get('is_public') == "true"
        self.request.user.is_public = is_public
        self.request.user.save()
        return JsonResponse({'response_result': 'success'})


class AccountFollowersView(TemplateView):
    template_name = 'users/followers.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data.update({'account_username': self.kwargs.get('username')})
        return context_data


class AccountFollowingsView(TemplateView):
    template_name = 'users/followings.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data.update({'account_username': self.kwargs.get('username')})
        return context_data


class UserSearchView(TemplateView):
    template_name = 'users/user-search.html'


class CropImageView(View):

    def post(self, request, *args, **kwargs):
        try:
            imageString = request.POST.get('image')
            url = save_temp_profile_image_from_base64String(imageString, self.request.user)
            crop_image_from_url(
                url=url,
                x=int(float(str(request.POST.get("cropX")))),
                y=int(float(str(request.POST.get("cropY")))),
                width=int(float(str(request.POST.get("cropWidth")))),
                height=int(float(str(request.POST.get("cropHeight")))),
                max_dimension=int(request.POST.get('maxDimension')),
            )

            if settings.DEFAULT_PROFILE_IMAGE_FILEPATH not in self.request.user.image.url:
                self.request.user.image.delete(save=False)
            self.request.user.image.save("profile_image.png", files.File(open(url, 'rb')))

            os.remove(url)
            if os.path.exists(f"{settings.TEMP}/{str(self.request.user.pk)}"):
                os.rmdir(f"{settings.TEMP}/{str(self.request.user.pk)}")

            return JsonResponse({'response_result': 'success', 'cropped_image_url': self.request.user.image.url})
        except Exception as e:
            return JsonResponse({'response_result': 'error', 'details': str(e)})