import os
import cv2
import json

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core import files
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from enum import Enum

from follow.models import Following, Followers, FollowingRequest
from .forms import LoginForm, RegisterForm, AccountEditForm
from .models import Account
from .utils import user_exists_and_is_account_owner, save_temp_profile_image_from_base64String

class DashboardPages(str, Enum):
    EDIT_PROFILE = 'edit_profile'
    PASSWORD = 'password_change'
    PRIVACY_AND_SECURITY = 'privacy_and_security'

@user_passes_test(lambda user: not user.is_authenticated, login_url='/', redirect_field_name=None)
def login_page(request):
    context = {
        'page': 'login',
    }
    if request.method == "GET":
        context['form'] = LoginForm()
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('feed')

        context['form'] = form

    return render(request, 'users/login_register.html', context=context)

@user_passes_test(lambda user: not user.is_authenticated, login_url='/', redirect_field_name=None)
def register_page(request):
    context = {
        'page': 'register',
    }
    if request.method == "GET":
        context['form'] = RegisterForm()
    elif request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')

        context['form'] = form

    return render(request, 'users/login_register.html', context=context)

@login_required(login_url=reverse_lazy('account:login'))
def logout_page(request):
    logout(request)
    return redirect('feed')

@login_required(login_url=reverse_lazy('account:login'))
def feed_page(request):
    return render(request, 'feed.html')

@login_required(login_url=reverse_lazy('account:login'))
def account_page(request, username):
    context = {}
    if request.method == "GET":
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return redirect('feed')

        following_model_account = Following.objects.get(user=account)
        followers_model_account = Followers.objects.get(user=account)

        if not request.user == account:

            try:
                friend_request = FollowingRequest.objects.get(sender=account, receiver=request.user)
                context['incoming_request'] = friend_request.is_active
            except FollowingRequest.DoesNotExist:
                pass

            try:
                friend_request = FollowingRequest.objects.get(sender=request.user, receiver=account)
                context['outgoing_request'] = friend_request.is_active
            except FollowingRequest.DoesNotExist:
                pass

            following_model_user = Following.objects.get(user=request.user)
            context['is_following'] = following_model_user.is_following(account)
            context['is_followed'] = following_model_account.is_following(request.user)

        context['following_count'] = following_model_account.count()
        context['followers_count'] = followers_model_account.count()

        context["account"] = account
        return render(request, 'users/account.html', context=context)

@login_required(login_url=reverse_lazy('account:login'))
def account_edit_page(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    context = {
        "account": account,
        "DATA_UPLOAD_MAX_MEMORY_SIZE": settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
        "page_name": DashboardPages.EDIT_PROFILE,
    }
    if request.method == "GET":
        form = AccountEditForm(instance=account)
    elif request.method == "POST":
        form = AccountEditForm(request.POST, instance=account)
        if form.is_valid():
            form.save()

    context['form'] = form

    return render(request, 'users/edit_account.html', context=context)

@login_required(login_url=reverse_lazy('account:login'))
def privacy_and_security_page(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    context = {
        "account": account,
        "page_name": DashboardPages.PRIVACY_AND_SECURITY,
    }

    if request.method == "GET":
        return render(request, 'users/privacy_and_security.html', context=context)
    
@login_required(login_url=reverse_lazy('account:login'))
def change_user_privacy_status(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    if request.method == "GET":
        return redirect('account:privacy-security', username=request.user.username)
    elif request.method == "POST":
        is_public = request.POST.get('is_public') == "true"
        account.is_public = is_public
        account.save()
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')
    return HttpResponse(json.dumps({'response_result': 'error'}), content_type='application/json')

@login_required(login_url=reverse_lazy('account:login'))
def crop_image(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    payload = {}

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        try:
            imageString = request.POST.get('image')
            url = save_temp_profile_image_from_base64String(imageString, account)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))

            cropX = 0 if cropX < 0 else cropX
            cropY = 0 if cropY < 0 else cropY

            cropped_image = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            if cropped_image.shape[0] > 300:
                cropped_image = cv2.resize(cropped_image, (300, 300))

            cv2.imwrite(url, cropped_image)
            account.image.delete()
            account.image.save("profile_image.png", files.File(open(url, 'rb')))
            account.save()

            payload['result'] = 'success'
            payload['cropped_image_url'] = account.image.url

            os.remove(url)
            if os.path.exists(f"{settings.TEMP}/{str(account.pk)}"):
                os.rmdir(f"{settings.TEMP}/{str(account.pk)}")

        except Exception as e:
            print(e)
            payload['result'] = 'error'
            payload['exception'] = str(e)

        return HttpResponse(json.dumps(payload), content_type='application/json')