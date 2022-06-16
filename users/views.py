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

from .forms import LoginForm, RegisterForm, AccountEditForm
from .models import Account
from .utils import user_exists_and_is_account_owner, save_temp_profile_image_from_base64String

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

        context["account"] = account
        return render(request, 'users/account.html', context=context)

@login_required(login_url=reverse_lazy('account:login'))
def account_edit_page(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    context = {
        "account": account,
        "DATA_UPLOAD_MAX_MEMORY_SIZE": settings.DATA_UPLOAD_MAX_MEMORY_SIZE
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
def crop_image(request, username):
    account, passes = user_exists_and_is_account_owner(request, username)
    if not passes:
        return redirect('feed')

    payload = {}

    if request.method == "POST":
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