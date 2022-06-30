from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse_lazy

from users.models import Account
from .models import ChatRoom

@login_required(login_url=reverse_lazy('account:login'))
def chat_page(request, username=None):
    if request.method == "GET":
        context = {}
        if username:
            try:
                user = Account.objects.get(username=username)
            except Account.DoesNotExist:
                return redirect('chat:chat-general-page')

            room = ChatRoom.objects.get_create(user1=request.user, user2=user)
            other_user = room.other_user(request.user)
            context['room_id'] = room.id
            context['other_user'] = other_user
            context['debug'] = settings.DEBUG
        return render(request, 'chat/chat_page.html', context=context)