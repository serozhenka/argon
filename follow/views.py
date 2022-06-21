import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import Following, FollowingRequest
from .utils import user_exists_and_is_not_request_user


@login_required(login_url=reverse_lazy('account:login'))
def follow_general_view(request, username):

    if request.method == "GET":
        return redirect('feed')

    elif request.method == "POST":
        account, passes = user_exists_and_is_not_request_user(request, username)
        if not passes:
            return redirect('feed')

        action = request.POST.get('action')

        try:
            if action == "follow":
                if account.is_public:
                    Following.objects.get(user=request.user).add_following(account)
                else:
                    following_request, created = FollowingRequest.objects.get_or_create(
                        sender=request.user,
                        receiver=account
                    )
                    following_request.is_active = True
                    following_request.save()

            elif action == "unfollow":
                Following.objects.get(user=request.user).remove_following(account)

            elif action == "remove":
                Following.objects.get(user=account).remove_following(request.user)

            elif action == "cancel-request":
                following_request = FollowingRequest.objects.get(sender=request.user, receiver=account)
                following_request.cancel()

            elif action == "accept-request":
                following_request = FollowingRequest.objects.get(sender=account, receiver=request.user)
                following_request.accept()

            elif action == "decline-request":
                following_request = FollowingRequest.objects.get(sender=account, receiver=request.user)
                following_request.decline()

            else:
                return HttpResponse(json.dumps({'response_result': 'error'}), content_type='application/json')

        except FollowingRequest.DoesNotExist:
            return redirect('feed')

        return HttpResponse(json.dumps({'response_result': 'success'}), content_type='application/json')
