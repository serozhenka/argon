import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Following, FollowingRequest
from users.models import Account
from .utils import user_exists_and_is_not_request_user

@login_required(login_url=reverse_lazy('account:login'))
def follow_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        if account.is_public:
            Following.objects.get(user=request.user).add_following(account)
        else:
            following_request, created = FollowingRequest.objects.get_or_create(
                sender=request.user,
                receiver=account
            )
            following_request.is_active = True
            following_request.save()

        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')

@login_required(login_url=reverse_lazy('account:login'))
def unfollow_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        Following.objects.get(user=request.user).remove_following(account)
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')

@login_required(login_url=reverse_lazy('account:login'))
def remove_follower_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        Following.objects.get(user=account).remove_following(request.user)
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')

@login_required(login_url=reverse_lazy('account:login'))
def cancel_following_request_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        try:
            following_request = FollowingRequest.objects.get(sender=request.user, receiver=account)
        except FollowingRequest.DoesNotExist:
            return redirect('feed')

        following_request.cancel()
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')


@login_required(login_url=reverse_lazy('account:login'))
def accept_following_request_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        try:
            following_request = FollowingRequest.objects.get(sender=account, receiver=request.user)
        except FollowingRequest.DoesNotExist:
            return redirect('feed')

        following_request.accept()
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')

@login_required(login_url=reverse_lazy('account:login'))
def decline_following_request_page(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        try:
            following_request = FollowingRequest.objects.get(sender=account, receiver=request.user)
        except FollowingRequest.DoesNotExist:
            return redirect('feed')

        following_request.decline()
        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')
