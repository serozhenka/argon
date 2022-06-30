from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

@login_required(login_url=reverse_lazy('account:login'))
def chat_page(request):
    if request.method == "GET":
        return render(request, 'chat/chat_page.html', context={})