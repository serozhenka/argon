from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Post, PostImage
from users.utils import user_exists_and_is_account_owner

@login_required(login_url=reverse_lazy('account:login'))
def feed_page(request):
    return render(request, 'post/feed.html')

@login_required(login_url=reverse_lazy('account:login'))
def post_add_page(request):

    if request.method == "GET":
        return render(request, 'post/post_add.html')
    elif request.method == "POST":
        images = request.FILES.getlist('images')
        post = Post.objects.create(
            user=request.user,
            description=request.POST.get('description')
        )

        for image in images:
            PostImage.objects.create(
                post=post,
                image=image,
            )

        return redirect('account:account', request.user.username)

