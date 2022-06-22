import cv2
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
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
        for i in range(50):
            post = Post.objects.create(
                user=request.user,
                description=request.POST.get('description')
            )

            for i in range(0, len(images)):
                post = PostImage.objects.create(
                    post=post,
                    image=images[i],
                    order=i,
                )
                absolute_url = str(settings.BASE_DIR) + post.image.url
                img = cv2.imread(absolute_url)
                width = int(img.shape[1])
                height = int(img.shape[0])

                if height / width > 1.25:  # 5 / 4
                    img = img[int(height/2 - 5/8*width):int(height/2 + 5/8*width), 0:width]
                elif height / width < 0.8:  # 4 / 5
                    img = img[0:height, int(width/2 - 5/8*height):int(width/2 + 5/8*height)]

                cv2.imwrite(absolute_url, img)

        return redirect('account:account', request.user.username)

