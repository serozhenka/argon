from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse_lazy

from users.models import Account
from .models import ChatRoom

@login_required(login_url=reverse_lazy('account:login'))
def chat_page(request, username=None):
    context = {}

    if request.method == "GET":
        if username:  # If username was passed we should render specific room page
            try:
                user = Account.objects.get(username=username)
            except Account.DoesNotExist:
                return redirect('chat:chat-general-page')

            room = ChatRoom.objects.get_create(user1=request.user, user2=user)
            other_user = room.other_user(request.user)

            context.update({
                'room_id': room.id,
                'other_user': other_user,
                'debug': settings.DEBUG,
            })

        context['page'] = "chat"
        return render(request, 'chat/chat_page.html', context=context)