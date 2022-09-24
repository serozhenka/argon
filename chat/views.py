from django.shortcuts import render, redirect
from django.conf import settings

from users.models import Account
from .models import ChatRoom

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