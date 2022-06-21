from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

@login_required(login_url=reverse_lazy('account:login'))
def feed_page(request):
    return render(request, 'post/feed.html')

@login_required(login_url=reverse_lazy('account:login'))
def post_add_page(request):
    return render(request, 'post/post_add.html')